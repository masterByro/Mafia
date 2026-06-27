from gamestate import GameState
from player import Player
from utils import checkExecutionerTargetDeaths, getByRole, isGameOver, get_target, getPlayerList, kill, sendDetectiveInfo, update_dead_chat_visibility, update_mafia_chat_visibility, sendWatchmanInfo
from roleDescriptions import sendNightInfo, sendDayActions
from timing import countdown
from channelStuff import sendVoteDropdown
from debug import save_night_debug_start, save_night_debug_end

async def passTime(guild, game):
    if not game.is_day: game.day_number += 1
    game.is_day = not game.is_day

    if game.is_day: await day(guild, game)
    else: await night(guild, game)

async def day(guild, game: GameState):
    channel = guild.get_channel(game.town_channel_id)
    await channel.send("\n==============================\n")

    await channel.send("The town awakens on Day " + str(game.day_number))
    
    if game.day_number > 1:
        deaths = await calculateResults(guild, game)
        await sendDetectiveInfo(guild, game)
        await sendWatchmanInfo(guild, game)
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
        await sendDayActions(guild,game)
        await sendVoteDropdown(guild, game)

async def night(guild, game: GameState):
    game.can_vote = False
    game.canDecide = False
    await update_dead_chat_visibility(guild, game)
    await update_mafia_chat_visibility(guild, game)
    channel = guild.get_channel(game.town_channel_id)
    await channel.send("\n==============================\n")
    await channel.send(getPlayerList(game))
    await channel.send("The town descends into darkness on Night " + str(game.day_number))
    await channel.send("You can now perform your night action")
    await sendNightInfo(guild, game)
    await countdown(channel, 70, prefix="Night")
    #await passTime(guild, game)


async def calculateResults(guild, game: GameState):
    deaths = [] # (victim_id, death_message, murder_note)
    blocked = set()
    healed = set()
    attacked = []  # (victim_id, death_message, murder_note)
    veteranGuard = False
    deathByVeteran = " was shot in the chest last night!"

    # DEBUG: Save starting state
    save_night_debug_start(game)

    #Jester, Jailor, Knight, escort, Healer, Insurgent, serial killer, Propagandist, Inquisitor, Warden, Watchman
    def addVisit(visitor, target): 
        if visitor.id != target.id: target.visits.append(f"{target.name} was visited by {visitor.name}")

    def isDead(player: Player): return any(v_id == player.id for v_id, _, _ in deaths)
    def isBlocked(player: Player): return player.id in blocked
    def isAttacked(player: Player): return any(v_id == player.id for v_id, _, _ in attacked)
    def isDeadOrBlocked(player: Player): return isDead(player) or isBlocked(player) or isAttacked(player)
    def visitVet(visitor: Player, target: Player):
        if target.role == 'Knight' and veteranGuard: 
            attacked.append((visitor.id, deathByVeteran, target.murderNote))
            return True
        return False

    jester, target = get_target(game, 'Jester')
    if jester and target:
        addVisit(jester, target)
        deaths.append((target.id," is dead! The Jester gets their revenge from the grave!", jester.murderNote))

    #Jailor
    jailor, jailorTarget = get_target(game, 'Jailor')
    if jailor and jailorTarget and not isDeadOrBlocked(jailor):
        blocked.add(jailorTarget.id)
        if jailor.willExecute: deaths.append((jailorTarget.id," was executed by the Jailor. Has justice been served?", jailor.murderNote))

    def visitorCheck(player, target):
        if isDead(player) or isBlocked(player) or isAttacked(player): return False
        if jailorTarget and target.id == jailorTarget.id: return False
        addVisit(player, target)
        return not visitVet(player, target)
 

    Knight = getByRole(game.players, 'Knight')
    if Knight and Knight.onAlert and not isDeadOrBlocked(Knight):
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

    Healer, target = get_target(game, 'Healer')
    if Healer and target and visitorCheck(Healer, target):
        healed.add(target.id)

    Wanderer = getByRole(game.players, 'Wanderer')
    if Wanderer and not isDeadOrBlocked(Wanderer) and Wanderer.onAlert:
        healed.add(Wanderer.id)

    Insurgent, target = get_target(game, 'Insurgent')
    if (Insurgent and target and visitorCheck(Insurgent, target)):
        attacked.append((target.id, " was murdered last night!",  Insurgent.murderNote))

    sk, target = get_target(game, 'Serial Killer')
    if (sk and target and visitorCheck(sk, target)):
        attacked.append((target.id," was murdered last night!", sk.murderNote))

    Propagandist, target = get_target(game, 'Propagandist')
    if (Propagandist and target and visitorCheck(Propagandist, target)): 
        target.framed = True

    Inquisitor, target = get_target(game, 'Inquisitor')
    if Inquisitor:
        if target is None or isDeadOrBlocked(Inquisitor):
            Inquisitor.targetInfo = ("You either did not select anyone to investigate last night, or were blocked")
        elif jailorTarget and target.id == jailorTarget.id: 
            Inquisitor.targetInfo = ("Your target was in jail last night, you were unable to investigate them")
        else:
            if not visitVet(Inquisitor, target):
                bloody = target.role in ['Healer', 'Insurgent', 'Serial Killer'] or target.framed or isAttacked(target) or isDead(target)
                
                if bloody:
                    Inquisitor.targetInfo = (f"Your target, {target.name}, had blood on them last night.")
                    target.framed = False
                else:
                    Inquisitor.targetInfo = (f"Your target, {target.name}, did NOT have blood on them last night.")

    canJanitorClean = False
    Warden, janitorTarget = get_target(game, 'Warden')
    if Warden and janitorTarget:
        canJanitorClean = visitorCheck(Warden, janitorTarget)
        
    watchMan, target = get_target(game, 'Watchman')
    if (watchMan and target): 
        if isDeadOrBlocked(watchMan) or visitVet(watchMan, target): pass
        else:
            if jailorTarget and target.id == jailorTarget.id: watchMan.visits = ['Your target was hauled off to Jail last night']
            else: 
                watchMan.visits = target.visits

    for victim_id, msg, note in attacked:
        if victim_id not in healed:
            deaths.append((victim_id, msg, note))
  
    if canJanitorClean and janitorTarget:
            dead_ids = {victim_id for victim_id, _, _ in deaths}
            if janitorTarget.id in dead_ids:
                janitorTarget.cleaned = True
                janitorTarget.role = 'CLEANED'

    # DEBUG: Save results
    save_night_debug_end(game, deaths, blocked, healed, attacked)

    return deaths

