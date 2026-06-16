from gamestate import GameState
from utils import getByRole, isMafia, sendToPlayer
from player import Role, Player

def getPossibleOptions(game: GameState, player: Player) -> list[Player]:
    if player is None: return []
    if game.is_day and player.role != 'Jailor': return []
    if player.role == 'Jester' and player.alive: return []
    if not player.alive and player.role != 'Jester': return []
    if player.role in ['Towny', 'Executioner', 'Mayor', 'Veteran', 'Survivor']: return []

    possible = []
    noSelfTarget = ['Mafioso', 'Framer', 'Serial Killer', 'Jester', 'Jailor']

    for target in game.players.values():
        if not target.alive: continue

        # Self-target restrictions
        if target.id == player.id and player.role in noSelfTarget: continue

        # Cannot target same person twice in a row
        if player.role in ['Doctor', 'Escort'] and player.lastTarget == target.id: continue

        # Mafia cannot target mafia
        if isMafia(player) and isMafia(target): continue

        # Jester can only target guilty voters
        if player.role == 'Jester':
            if len(player.guiltyVoters) == 0: continue
            if target.id not in player.guiltyVoters: continue

        # Doctor cannot heal revealed mayor
        if (player.role == 'Doctor' and target.role == 'Mayor' and target.revealed): continue

        possible.append(target)

    return possible

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