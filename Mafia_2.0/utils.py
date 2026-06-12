import discord

from gamestate import GameState
from player import Player

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

async def setAction(game: GameState, ctx, number: int):
    if game.is_day: return "Actions may only be performed at night.", False

    player = game.players.get(ctx.author.id)
    if player is None: return "You are not part of the game.", False

    if player.role == "Jester" and player.alive: return "Jester can only seek revenge once lynched", False
    if not player.alive and not player.role == "Jester": return "Dead players cannot perform actions.", False

    # Roles with no night action
    if player.role in ["Towny", "Executioner", "Mayor"]:
        return f"The {player.role} has no night action.", False

    if player.role == "Veteran":
        if number == 1:
            if player.alerts > 0:
                player.roundInput = "alert"
                return "You will be on alert tonight.", True
            return "You have already been on alert three times.", False
        else:
            return "Bro can you read? Either type 1 to be on alert, or don't type at all", False

    # Find target by player number
    target = next((p for p in game.players.values() if p.number == number),None)

    if target is None: return "Invalid player number.", False

    if not target.alive: return f"{target.name} is dead. You cannot perform actions on them.", False

    # Self-target restrictions
    if target.id == player.id:
        if player.role in [
            "Escort",
            "Mafioso",
            "Framer",
            "Detective",
            "Serial Killer",
            "Veteran",
            "Jester"
        ]:
            return f"The {player.role} cannot target themselves.", False

    # Cannot target same person twice in a row
    if player.lastTarget == target.id:
        if player.role in ["Doctor", "Escort"]:
            return (f"The {player.role} cannot target the same player two nights in a row.",False,)

    # Mafia cannot target mafia
    if player.role in ["Mafioso", "Framer"]:
        if target.role in ["Mafioso", "Framer"]:
            return "You cannot target a fellow Mafia member.", False

    #Jester can only kill guilty voters the night after lynch
    if player.role == "Jester":
        if len(player.guiltyVoters) == 0: return "You can no longer seek revenge", False
        if target.id not in player.guiltyVoters: return "You can only target players who voted guilty against you", False

    # Success
    player.roundInput = target.id

    return (f"You will target {target.name} tonight.", True)

def get_target(game: GameState, role):
    actor = next((p for p in game.players.values()if p.role == role),None)

    if actor is None: return None, None
    if actor.roundInput is None: return actor, None

    if (actor.role == "Veteran"): return actor, actor.roundInput

    target = game.players.get(actor.roundInput)

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
