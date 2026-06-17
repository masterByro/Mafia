import discord

from gamestate import GameState
from player import Player, Role, mafiaRoles, townRoles, neutralEvil, neutralKiller
from scoring import updateWins

def getPlayerList(game: GameState):
    ordered = sorted(game.players.values(), key=lambda p: p.number)

    lines = ["**Current Players**\n"]

    for p in ordered:
        if p.alive:
            lines.append(f"{p.number}. {p.name} | 🟢 Alive")
        else:
            lines.append(f"{p.number}. {p.name} | 🔴 Dead ({p.role})")

    return "\n".join(lines)

def getPlayerListEndgame(game: GameState):
    ordered = sorted(game.players.values(), key=lambda p: p.number)
    lines = ["**🏁 Final Player Results**\n"]

    for p in ordered:
        status = "🟢 Alive" if p.alive else "🔴 Dead"
        win = "🏆 Win" if p.win else "❌ Loss"

        lines.append(
            f"{p.number}. {p.name} | {status} | { p.originalRole} | {win}"
        )

    return "\n".join(lines)


def getByRole(players: dict[int, Player], role: Role):
    return next((p for p in players.values() if p.role == role),None)

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
        message = getPlayerListEndgame(game)
        await channel.send(message)
        updateWins(game)

def checkWin(game):
    alive_players = [p for p in game.players.values() if p.alive and p.role != 'Wanderer']

    alive_mafia = [p for p in alive_players if p.role in mafiaRoles]
    alive_town = [p for p in alive_players if p.role in townRoles]
    alive_neutral_evil = [p for p in alive_players if p.role in neutralEvil]
    alive_sk = [p for p in alive_players if p.role in neutralKiller]

    def set_winners(players):
        for p in players:
            p.win = True
        for p in game.players.values():
            if p.alive and p.role == 'Wanderer':
                p.win = True

    if len(alive_players) == 1 and alive_sk:
        set_winners(alive_sk)
        return True, "The Serial Killer has won!"

    if alive_mafia and not alive_town and not alive_neutral_evil and not alive_sk:
        set_winners([p for p in game.players.values() if p.role in mafiaRoles])
        return True, "The Uprising have eliminated all opposition!"

    if not alive_mafia and not alive_sk:
        set_winners([p for p in game.players.values() if p.role in townRoles])
        return True, "The Townfolk have defeated all threats!"

    return False, None

async def kill(guild, game: GameState, player: Player, reason, note):
    player.alive = False

    dead_role = guild.get_role(game.dead_role_id)
    if dead_role: await player.member.add_roles(dead_role)

    channel = guild.get_channel(game.town_channel_id)
    Warden = getByRole(game.players, "Warden")

    await channel.send(f"{reason} Their role was: { player.role}")
    if note: await channel.send(f"Their killer left this message: {note}")
    await handleMafiosoDeathTransfer(guild, game, player)
    
    will_channel = guild.get_channel(game.player_will_channels.get(player.id))
    if will_channel:
        
        if player.cleaned and Warden:
            await will_channel.set_permissions(Warden.member, view_channel=True, send_messages=False, read_message_history=True)
            await will_channel.set_permissions(player.member, view_channel=False, send_messages=False, read_message_history=False)
        else:
            await will_channel.set_permissions(guild.default_role, view_channel=True, send_messages=False, read_message_history=True)
            await will_channel.set_permissions(player.member, view_channel=True, send_messages=False, read_message_history=True)

    if player.cleaned and Warden and Warden.alive:
        janitor_channel = guild.get_channel(game.player_channels.get(Warden.id))

        if janitor_channel:
            await janitor_channel.send(f":broom: You have cleaned a body.\n" f"Target: **{player.name}**\n" f"Role: **{player.role}**")

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

def isMafia(player: Player): return player.role in ['Insurgent', 'Propagandist', 'Warden']

async def update_mafia_chat_visibility(guild, game: GameState):
    mafia_channel = guild.get_channel(game.mafia_channel_id)

    overwrites = dict(mafia_channel.overwrites)
    jailor = getByRole(game.players, "Jailor")
    jailed_id = jailor.roundInput if jailor else None

    for player in game.players.values():
        if not isMafia(player) or jailed_id == player.id: continue
        if game.is_day:
            overwrites[player.member] = discord.PermissionOverwrite(view_channel=False)
        else:
            overwrites[player.member] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

    await mafia_channel.edit(overwrites=overwrites)

async def checkExecutionerTargetDeaths(guild, game: GameState, deaths):
    executioner = getByRole(game.players, 'Executioner')
    if executioner is None: return
    
    dead_ids = {death[0] for death in deaths}
    target_id = executioner.executioner_target
    if  target_id is None or target_id not in dead_ids: return

    target = game.players[target_id]
    executioner.role = "Jester"
    executioner.executioner_target = None
    channel = guild.get_channel(game.player_channels[executioner.id])
    if channel:
        await channel.send(f"Your target, **{target.name}**, died before they could be lynched.\n\n" "You have become the **Jester**.\n" "Your objective is now to be lynched by the town.")

async def sendToPlayer(guild, game, player_id, message):
    channel_id = game.player_channels.get(player_id)
    if channel_id is None: return

    channel = guild.get_channel(channel_id)
    if channel: await channel.send(message)


async def handleMafiosoDeathTransfer(guild, game: GameState, dead_player: Player):
    if dead_player.role != 'Insurgent': return
    promoted = None
    Propagandist = getByRole(game.players, 'Propagandist')
    Warden = getByRole(game.players, 'Warden')

    if Propagandist is not None and Propagandist.alive: promoted = Propagandist
    elif Warden is not None and Warden.alive: promoted = Warden
    if promoted is None: return

    # promote
    dead_player.role = 'Insurgent (Dead)'
    promoted.role = 'Insurgent'
    channel = guild.get_channel(game.player_channels.get(promoted.id))
    if channel: await channel.send("🩸 The Insurgent has died. You have taken their place as the new Insurgent.")

async def sendDetectiveInfo(guild, game):
    Inquisitor = getByRole(game.players, "Inquisitor")
    if Inquisitor is None or not Inquisitor.alive: return
    channel = guild.get_channel(game.player_channels.get(Inquisitor.id))

    if Inquisitor.targetInfo and channel:
        await channel.send(Inquisitor.targetInfo)
        Inquisitor.targetInfo = None

async def setMuderNote(game: GameState, ctx, message: str):
    player = game.players.get(ctx.author.id)
    killRoles: list[Role] = ['Insurgent', 'Serial Killer', 'Jester', 'Jailor']

    if player is None or player.role not in killRoles: return 'You must be a role that kills to use this'
    player.murderNote = message
    return 'Saved'
    
