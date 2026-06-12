from gamestate import GameState
from utils import checkExecutionerTargetDeaths, getByRole, isGameOver, get_target, getPlayerList, is_blocked, kill, update_dead_chat_visibility, update_mafia_chat_visibility
from roleDescriptions import sendNightInfo
from channelStuff import sendVoteInfo

async def passTime(guild, game):
    game.is_day = not game.is_day
    game.day_number += 1

    if game.is_day: await day(guild, game)
    else: await night(guild, game)

async def day(guild, game: GameState):
    channel = guild.get_channel(game.town_channel_id)
    await channel.send(getPlayerList(game))
    await channel.send("The town awakens on Day " + str(game.day_number))
    
    if game.day_number > 1:
        deaths = calculateResults(game)
 
        await update_dead_chat_visibility(guild, game)
        await update_mafia_chat_visibility(guild, game)
        for player in game.players.values():
            player.lastTarget = player.roundInput
            player.roundInput = None
            player.vote = None
            player.decision = None
   
        if deaths:
            await checkExecutionerTargetDeaths(guild, game, deaths)
            await channel.send("☠️ **Night Results** ☠️\n")
            for victim_id, msg in deaths:
                victim = game.players[victim_id]
                await kill(guild, game, game.players[victim_id], f"**{victim.name}** {msg}")   
        else:
            await channel.send("🌙 **Night Results**\nNo one died last night.")

    await isGameOver(guild, game)
    if game.running:
        game.can_vote = True  
        await channel.send("You may openly discuss with the group")
        await channel.send("You can also openly vote to place a Player on Trial for lynching")
        await sendVoteInfo(guild, game.players)

async def night(guild, game):
    await update_dead_chat_visibility(guild, game)
    await update_mafia_chat_visibility(guild, game)
    channel = guild.get_channel(game.town_channel_id)
    await channel.send(getPlayerList(game))
    await channel.send("The town desscends into darkness on Night " + str(game.day_number))
    await channel.send("You can now perform your night action")
    await sendNightInfo(guild, game)

def calculateResults(game: GameState):
    deaths = []
    blocked = set()
    healed = set()
    framed = set()
    attacked = []
    veteranGuard = False
    deathByVeteran = " was shot in the chest last night!"

    #Jester, Jailor, veteran, escort, doctor, mafioso, serial killer, framer, detective

    jester, target = get_target(game, "Jester")
    if jester and target:
        deaths.append((target.id," is dead! The Jester gets their revenge from the grave!"))

    #Jailor

    veteran = getByRole(game.players,  "Veteran")
    if veteran and veteran.onAlert:
        veteranGuard = True
        veteran.onAlert = False #Reset it

    def visitVet(target):
        if target.role == "Veteran" and veteranGuard: 
            attacked.append((target.id,deathByVeteran))
            return True
        return False
        
    escort, target = get_target(game, "Escort")
    if escort and target:
        if not visitVet(target):
            blocked.add(target.id)
            # Escort dies if visiting SK
            if target.role == "Serial Killer":
                attacked.append((escort.id," was horrifically stabbed to death while out visiting last night!"))

    doctor, target = get_target(game, "Doctor")
    if (doctor and target and not is_blocked(doctor, blocked)):
        if not visitVet(target): healed.add(target.id)

    mafioso, target = get_target(game, "Mafioso")
    if (mafioso and not is_blocked(mafioso, blocked) and target):
        if not visitVet(target):  
            attacked.append((target.id, " was murdered last night!"))

    sk, target = get_target(game, "Serial Killer")
    if (sk and not is_blocked(sk, blocked) and target):
        if not visitVet(target):
            attacked.append((target.id," was horrifically stabbed to death last night!"))

    framer, target = get_target(game, "Framer")
    if (framer and target and not is_blocked(framer, blocked)): 
        if not visitVet(target):
            framed.add(target.id)

    detective, target = get_target(game, "Detective")
    if detective:
        if target is None or is_blocked(detective, blocked):
            detective.targetInfo = ("You either did not select anyone to investigate last night, or were blocked")
        else:
            if not visitVet(target):
                bloody = (
                    target.role in ["Doctor", "Mafioso", "Serial Killer"]
                    or target.id in framed
                    or target.id in attacked
                )

                if bloody:
                    detective.targetInfo = (f"Your target, {target.name}, had blood on them last night.")
                else:
                    detective.targetInfo = (f"Your target, {target.name}, did NOT have blood on them last night.")

    for victim_id, msg in attacked:
        if victim_id not in healed:
            deaths.append((victim_id, msg))

    return deaths

