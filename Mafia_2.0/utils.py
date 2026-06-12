import discord

from gamestate import GameState
from player import Player, Role

def getPlayerList(game: GameState):
    # Build ordered player list
    ordered = sorted(game.players.values(), key=lambda p: p.number)

    lines = ["**Current Players**\n"]

    for p in ordered:
        status = "🟢 Alive" if p.alive else "🔴 Dead"

        lines.append(
            f"{p.number}. {p.name} | {status}"
        )

    return "\n".join(lines)

def getByRole(players: dict[int, Player], role: Role):
    return next((p for p in players.values()if p.role == role),None)

def get_target(game: GameState, role: Role):
    actor = getByRole(game.players, role)

    if actor is None: return None, None
    if actor.roundInput is None: return actor, None

    target = game.players.get(int(actor.roundInput))

    return actor, target

async def isGameOver(guild, game: GameState):
    gameWon, message =  checkWin(game)
    if gameWon:
        game.running = False
        channel = guild.get_channel(game.town_channel_id)
        await channel.send(message)

def checkWin(game):
    alive_players = [p for p in game.players.values() if p.alive]

    alive_mafia = [p for p in alive_players if isMafia(p)]
    alive_town = [p for p in alive_players if not isMafia(p) and p.role != "Serial Killer"]
    alive_sk = [p for p in alive_players if p.role == "Serial Killer"]

    #TODO: UNCOMMENT
    # if len(alive_players) == 1 and alive_sk:
    #     return True, "The Serial Killer has won!"

    # if len(alive_mafia) > 0 and len(alive_mafia) >= len(alive_town) and not alive_sk:
    #     return True, "The Mafia have defeated the Townfolk!"

    # if not alive_mafia and not alive_sk:
    #     return True, "The Townfolk have defeated all threats!"

    return False, None

def is_blocked(player, blocked):
    return player.id in blocked

async def kill(guild, game: GameState, player: Player, reason):
    player.alive = False
    player.roundInput = None
    player.vote = None
    player.decision = None
    
    dead_role = guild.get_role(game.dead_role_id)
    if dead_role: await player.member.add_roles(dead_role)

    channel = guild.get_channel(game.town_channel_id)
    await channel.send(f"{reason}. Their role was: {player.role}")
    await isGameOver(guild, game)

async def update_dead_chat_visibility(guild, game):
    dead_channel = guild.get_channel(game.dead_channel_id)
    if not dead_channel: return

    overwrites = dict(dead_channel.overwrites)
    # Get Medium players
    medium_members = [p.member for p in game.players.values() if p.role == "Medium"]

    if game.is_day:
        for member in medium_members:
            overwrites[member] = discord.PermissionOverwrite(view_channel=False)
    else:
        for member in medium_members:
            overwrites[member] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

    await dead_channel.edit(overwrites=overwrites)

def isMafia(player: Player): return player.role in ["Mafioso", "Framer"]

async def update_mafia_chat_visibility(guild, game: GameState):
    mafia_channel = guild.get_channel(game.mafia_channel_id)

    overwrites = dict(mafia_channel.overwrites)

    for player in game.players.values():
        if not  isMafia(player): continue
        if game.is_day:
            overwrites[player.member] = discord.PermissionOverwrite(view_channel=False)
        else:
            overwrites[player.member] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

    await mafia_channel.edit(overwrites=overwrites)

async def checkExecutionerTargetDeaths(guild, game, deaths):
    executioner = getByRole(game.players, 'Executioner')
    if executioner is None: return
    
    dead_ids = {victim_id for victim_id, _ in deaths}
    if executioner.executioner_target not in dead_ids: return

    target = game.players[executioner.executioner_target]
    executioner.role = "Jester"
    executioner.executioner_target = None
    channel = guild.get_channel(game.player_channels[executioner.id])
    if channel:
        await channel.send(
            f"Your target, **{target.name}**, died before they could be lynched.\n\n"
            "You have become the **Jester**.\n"
            "Your objective is now to be lynched by the town."
        )
