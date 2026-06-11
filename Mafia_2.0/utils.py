import discord


def getPlayerList(game):
    # Build ordered player list
    ordered = sorted(game.players.values(), key=lambda p: p.number)

    lines = ["**Current Players**\n"]

    for p in ordered:
        status = "🟢 Alive" if p.alive else "🔴 Dead"

        lines.append(
            f"{p.number}. {p.name} | {status}"
        )

    return "\n".join(lines)

async def setAction(game, ctx, number: int):
    if game.is_day: return "Actions may only be performed at night.", False

    player = game.players.get(ctx.author.id)
    if player is None: return "You are not part of the game.", False
    if not player.alive: return "Dead players cannot perform actions.", False

    # Roles with no night action
    if player.role in ["Towny", "Executioner", "Jester", "Mayor"]:
        return f"The {player.role} has no night action.", False

    # Veteran special actions //TODO
    if player.role == "Veteran":
        if number == 0:
            if player.hasMine:
                player.roundInput = "landmine"
                return "You will place a landmine tonight.", True

            return "You have already used your landmine.", False

        if not player.hasBullet:
            return "You have no bullets remaining.", False

    # Find target by player number
    target = next(
        (p for p in game.players.values() if p.number == number),
        None
    )

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
        ]:
            return f"The {player.role} cannot target themselves.", False

    # Cannot target same person twice in a row
    if player.lastTarget == target.id:
        if player.role in ["Doctor", "Escort"]:
            return (
                f"The {player.role} cannot target the same player two nights in a row.",
                False,
            )

    # Mafia cannot target mafia
    if player.role in ["Mafioso", "Framer"]:
        if target.role in ["Mafioso", "Framer"]:
            return "You cannot target a fellow Mafia member.", False

    # Success
    player.roundInput = target.id

    return (
        f"You will target {target.name} tonight.",
        True,
    )

def get_target(game, role):
    actor = next(
        (p for p in game.players.values()
         if p.role == role and p.alive),
        None
    )

    if actor is None:
        return None, None

    if actor.roundInput is None:
        return actor, None

    target = game.players.get(actor.roundInput)

    return actor, target

def checkWin(game):
    pass

def is_blocked(player, blocked):
    return player.id in blocked

def getVotedForPlayer(game):
    return next((p for p in game.players.values() if p.votedFor), None)

async def kill(ctx, game, player, reason):
    player.alive = False
    player.roundInput = None
    player.vote = None
    player.decision = None
    
    dead_role = ctx.guild.get_role(game.dead_role_id)
    if dead_role: await player.member.add_roles(dead_role)

    channel = ctx.guild.get_channel(game.town_channel_id)
    await channel.send(reason)
    await channel.send(f"{reason}. Their role was: {player.role}")
    
    if not checkWin(game):
    # TODO: check win conditions here and end game if met
        pass

async def update_dead_chat_visibility(guild, game):
    dead_channel = guild.get_channel(game.dead_channel_id)
    if not dead_channel: return

    overwrites = dict(dead_channel.overwrites)
    # Get Medium players
    medium_members = [p.member for p in game.players.values() if p.role == "Medium"]

    if game.is_day:
        # DAY → Medium cannot see
        for member in medium_members:
            overwrites[member] = discord.PermissionOverwrite(
                view_channel=False
            )
    else:
        # NIGHT → Medium can see
        for member in medium_members:
            overwrites[member] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )

    await dead_channel.edit(overwrites=overwrites)