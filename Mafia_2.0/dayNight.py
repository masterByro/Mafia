from gamestate import GameState
from player import Player
from utils import checkExecutionerTargetDeaths, getByRole, isGameOver, get_target, getPlayerList, kill, sendDetectiveInfo, update_dead_chat_visibility, update_mafia_chat_visibility
from roleDescriptions import sendNightInfo
from timing import countdown
from channelStuff import sendVoteDropdown

async def passTime(guild, game):
    if not game.is_day: game.day_number += 1
    game.is_day = not game.is_day

    if game.is_day: await day(guild, game)
    else: await night(guild, game)

async def day(guild, game: GameState):
    channel = guild.get_channel(game.town_channel_id)
    await channel.send("\n===================================================================\n")

    await channel.send("The town awakens on Day " + str(game.day_number))
    
    if game.day_number > 1:
        deaths = await calculateResults(guild, game)
        await sendDetectiveInfo(guild, game)
        await update_dead_chat_visibility(guild, game)
        await update_mafia_chat_visibility(guild, game)
   
        if deaths:
            await checkExecutionerTargetDeaths(guild, game, deaths)
            await channel.send("☠️ **Night Results** ☠️\n")
            for victim_id, msg, note in deaths:
                victim = game.players[victim_id]
                await kill(guild, game, game.players[victim_id], f"**{victim.name}** {msg}", note)
        else:
            await channel.send("🌙 **Night Results**\nNo one died last night.")

        for player in game.players.values():
            player.reset_round()

    await channel.send(getPlayerList(game))
    await isGameOver(guild, game)
    
    if game.running:
        game.can_vote = True  
        await channel.send("You may openly discuss with the group")
        await channel.send("You can also openly vote to place a Player on Trial for lynching")
        await sendVoteDropdown(guild, game)

async def night(guild, game: GameState):
    await update_dead_chat_visibility(guild, game)
    await update_mafia_chat_visibility(guild, game)
    channel = guild.get_channel(game.town_channel_id)
    await channel.send("\n===================================================================\n")
    await channel.send(getPlayerList(game))
    await channel.send("The town descends into darkness on Night " + str(game.day_number))
    await channel.send("You can now perform your night action")
    await sendNightInfo(guild, game)
    await countdown(channel, 90, prefix="Night")
    #await passTime(guild, game)


async def calculateResults(guild, game: GameState):
    deaths = [] # (victim_id, death_message, murder_note)
    blocked = set()
    healed = set()
    attacked = []  # (victim_id, death_message, murder_note)
    veteranGuard = False
    deathByVeteran = " was shot in the chest last night!"

    #Jester, Jailor, veteran, escort, doctor, mafioso, serial killer, framer, detective, janitor

    def isDead(player: Player): return any(v_id == player.id for v_id, _, _ in deaths)
    def isBlocked(player: Player): return player.id in blocked
    def isAttacked(player: Player): return any(v_id == player.id for v_id, _, _ in attacked)
    def isDeadOrBlocked(player: Player): return isDead(player) or isBlocked(player) or isAttacked(player)
    def visitVet(visitor: Player, target: Player):
        if target.role == 'Veteran' and veteranGuard: 
            attacked.append((visitor.id, deathByVeteran, target.murderNote))
            return True
        return False

    jester, target = get_target(game, 'Jester')
    if jester and target:
        deaths.append((target.id," is dead! The Jester gets their revenge from the grave!", jester.murderNote))

    #Jailor
    jailor, jailorTarget = get_target(game, 'Jailor')
    if jailor and jailorTarget and not isDeadOrBlocked(jailor):
        blocked.add(jailorTarget.id)
        if jailor.willExecute: deaths.append((jailorTarget.id," was executed by the Jailor. Has justice been served?", jailor.murderNote))

    def visitorCheck(player, target):
        if isDead(player) or isBlocked(player) or isAttacked(player): return False
        if jailorTarget and target.id == jailorTarget.id: return False
        return not visitVet(player, target)
 

    veteran = getByRole(game.players, 'Veteran')
    if veteran and veteran.onAlert and not isDeadOrBlocked(veteran):
        veteranGuard = True

    escort, target = get_target(game, 'Escort')
    if escort and target and visitorCheck(escort, target):
        blocked.add(target.id)
        # Escort dies if visiting SK
        if target.role == 'Serial Killer':
            attacked.append((escort.id," was horrifically stabbed to death while out visiting last night!", target.murderNote))
            will_channel_id = game.player_will_channels.get(escort.id)
            if will_channel_id:
                will_channel = guild.get_channel(will_channel_id)
                if will_channel: 
                    await will_channel.purge(limit=100)
                    await will_channel.send("🩸🩸🩸🩸🩸🩸🩸🩸🩸🩸🩸🩸🩸🩸🩸🩸🩸🩸🩸🩸🩸🩸🩸🩸")

    doctor, target = get_target(game, 'Doctor')
    if doctor and target and visitorCheck(doctor, target):
        healed.add(target.id)

    survivor = getByRole(game.players, 'Survivor')
    if survivor and not isDeadOrBlocked(survivor) and survivor.onAlert:
        healed.add(survivor.id)

    mafioso, target = get_target(game, 'Mafioso')
    if (mafioso and target and visitorCheck(mafioso, target)):
        attacked.append((target.id, " was murdered last night!",  mafioso.murderNote))

    sk, target = get_target(game, 'Serial Killer')
    if (sk and target and visitorCheck(sk, target)):
        attacked.append((target.id," was murdered last night!", sk.murderNote))

    framer, target = get_target(game, 'Framer')
    if (framer and target and visitorCheck(framer, target)): 
        target.framed = True

    detective, target = get_target(game, 'Detective')
    if detective:
        if target is None or isDeadOrBlocked(detective):
            detective.targetInfo = ("You either did not select anyone to investigate last night, or were blocked")
        elif jailorTarget and target.id == jailorTarget.id: 
            detective.targetInfo = ("Your target was in jail last night, you were unable to investigate them")
        else:
            if not visitVet(detective, target):
                bloody = target.role in ['Doctor', 'Mafioso', 'Serial Killer'] or target.framed or isAttacked(target) or isDead(target)
                
                if bloody:
                    detective.targetInfo = (f"Your target, {target.name}, had blood on them last night.")
                    target.framed = False
                else:
                    detective.targetInfo = (f"Your target, {target.name}, did NOT have blood on them last night.")

    canJanitorClean = False
    janitor, janitorTarget = get_target(game, 'Janitor')
    if janitor and janitorTarget:
        canJanitorClean = visitorCheck(janitor, janitorTarget)
        
    for victim_id, msg, note in attacked:
        if victim_id not in healed:
            deaths.append((victim_id, msg, note))
  
    if canJanitorClean and janitorTarget:
            dead_ids = {victim_id for victim_id, _, _ in deaths}
            if janitorTarget.id in dead_ids:
                janitorTarget.cleaned = True
                janitorTarget.role = 'CLEANED'

    return deaths

