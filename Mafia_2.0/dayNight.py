from utils import checkWin, isGameOver, get_target, getPlayerList, is_blocked, update_dead_chat_visibility, update_mafia_chat_visibility
   
async def day(guild, game):
    channel = guild.get_channel(game.town_channel_id)

    if game.day_number > 1:
        deaths = calculateResults(game)
        await update_dead_chat_visibility(guild, game)
        await update_mafia_chat_visibility(guild, game)
        await isGameOver(guild, game)
       
        for player in game.players.values():
            player.lastTarget = player.roundInput
            player.roundInput = None
            player.vote = None
            player.decision = None

    if game.running:
        game.can_vote = True
        await channel.send(getPlayerList(game))
        await channel.send("The town awakens on Day " + str(game.day_number))
        await channel.send("You may openly discuss with the group")
        await channel.send("You can also openly vote to place a Player on Trial for lynching")

async def night(guild, game):
    await update_dead_chat_visibility(guild, game)
    await update_mafia_chat_visibility(guild, game)
    channel = guild.get_channel(game.town_channel_id)
    await channel.send(getPlayerList(game))
    await channel.send("The town desscends into darkness on Night " + str(game.day_number))
    await channel.send("You can now perform your night action")



def calculateResults(game):
    deaths = []
    blocked = set()
    healed = set()
    framed = set()
    attacked = []
    veteranGuard = False

   #TODO Revisit this
    veteran, target = get_target(game, "Veteran")
    if veteran and target:
        if target == 1:
            veteranGuard = True
            #deaths.append((target.id," was shot in the chest last night!"))

    escort, target = get_target(game, "Escort")
    if escort and target:
        blocked.add(target.id)
        # Escort dies if visiting SK
        if target.role == "Serial Killer":
            deaths.append((escort.id," was horrifically stabbed to death while out visiting last night!"))

    doctor, target = get_target(game, "Doctor")
    if (doctor and target and not is_blocked(doctor, blocked)): 
        healed.add(target.id)

  #TODO Revisit this..
    jester, target = get_target(game, "Jester")
    if target: deaths.append((target.id," is dead! The Jester gets their revenge from the grave!"))


    framer, target = get_target(game, "Framer")
    if (framer and target and not is_blocked(framer, blocked)): 
        framed.add(target.id)

    mafioso, target = get_target(game, "Mafioso")
    if (mafioso and is_blocked(mafioso, blocked) and target and target.id not in healed):
        attacked.append((target.id, " was murdered last night!"))

    sk, target = get_target(game, "Serial Killer")
    if (sk and not is_blocked(sk, blocked) and target and target.id not in healed):
        attacked.append((target.id," was horrifically stabbed to death last night!"))

    detective, target = get_target(game, "Detective")
    if detective:
        if target is None or is_blocked(detective, blocked):
            detective.targetInfo = ("You either did not select anyone to investigate last night, or were blocked")

        else:
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

    for victim_id, _ in deaths:
        game.players[victim_id].alive = False


    return deaths
