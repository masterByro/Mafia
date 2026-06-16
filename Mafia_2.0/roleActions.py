from gamestate import GameState
from utils import getByRole, isMafia, sendToPlayer
from player import Role, Player

async def setTarget(game: GameState, ctx, number: int):
    player = game.players.get(ctx.author.id)
    if player is None: return "You are not part of the game."
    if game.is_day and not player.role == 'Jailor': return "Actions may only be performed at night."

    if player.role == 'Jester' and player.alive: return "Jester can only seek revenge once lynched."
    if not player.alive and not player.role == 'Jester': return "Dead players cannot perform actions."

    # Roles that dont have a target action #TODO Switch not role not in. That waay its opt in, not opt out
    if player.role in ['Towny', 'Executioner', 'Mayor', 'Veteran', 'Survivor']:
        return f"The {player.role} cannot use this command."

    # Find target by player number
    target = next((p for p in game.players.values() if p.number == number),None)

    if target is None: return "Invalid player number."

    if not target.alive: return f"{target.name} is dead. You cannot perform actions on them."
    
    noSelfTarget: list[Role] = ['Mafioso', 'Framer','Serial Killer', 'Jester', 'Jailor']
    # Self-target restrictions
    if target.id == player.id:
        if player.role in noSelfTarget:
            return f"The {player.role} cannot target themselves."

    # Cannot target same person twice in a row
    if player.role in ['Doctor', 'Escort'] and player.lastTarget == target.id:
        return f"The {player.role} cannot target the same player two nights in a row."

    # Mafia cannot target mafia
    if isMafia(player) and isMafia(target):
        return "You cannot target a fellow Mafia member."

    #Jester can only kill guilty voters the night after lynch
    if player.role == 'Jester':
        if len(player.guiltyVoters) == 0: return "You can no longer seek revenge"
        if target.id not in player.guiltyVoters: return "You can only target players who did not decide you were innocent"

    #Healer can't target revealed Mayor
    if player.role == 'Doctor' and target.role == 'Mayor' and target.revealed:
        return 'You cannot protect the Mayor'
    
    # Success
    player.roundInput = target.id
    return f"You will target {target.name} tonight."

async def jailorKill(game: GameState, ctx):
    player = game.players.get(ctx.author.id)
    if player is None or player.role != 'Jailor' or game.is_day or player.roundInput is None: return 'Not valid. Must be night, you must be jailor, and you must target someone in the day first'

    target = game.players.get(player.roundInput)

    if target is None or not target.alive: return "Your jailed target is no longer valid."

    # toggle execution state
    player.willExecute = not player.willExecute

    if player.willExecute:
        message = f"⚔️ You have decided to execute **{target.name}** tonight. Retype `!kill` to change your mind"
        target_message = "⚔️ The Jailor has decided to execute you tonight."
    else:
        message = f"You have decided NOT to execute **{target.name}**."
        target_message = "The Jailor has changed their mind."

    # send to jailed target
    channel = ctx.guild.get_channel(game.player_channels.get(target.id))

    if channel: await channel.send(target_message)

    return message


async def sayJail(game: GameState, ctx, message: str):
    if game.is_day: return 'You can only use this at night'
    speaker = game.players.get(ctx.author.id)
    jailor = getByRole(game.players, 'Jailor')
    if jailor is None or not jailor.alive or speaker is None or not speaker.alive: return 'Fail 1'

    prisoner_id = jailor.roundInput
    if prisoner_id is None: return 'No prisoner was selected during the day'

    prisoner = game.players.get(prisoner_id)
    if prisoner is None: return 'No prisoner to speak to'

    if speaker.id == jailor.id:
        await sendToPlayer(ctx.guild, game, prisoner.id, f"**[Jailor]** {message}")
        return 'Message sent'
    
    if speaker.id == prisoner.id:
        await sendToPlayer(ctx.guild, game, jailor.id, f"**[{speaker.name}]** {message}")
        return 'Message sent'
    
    return 'Not your command to use buster'