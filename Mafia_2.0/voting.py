from utils import checkWin
async def sendVote(game, ctx, number):
    if not game.can_vote: return "You cannot vote right now.", None

    voter = game.players.get(ctx.author.id)
    if voter is None: return "You are not part of the game.", None
    if not voter.alive: return "Dead players cannot vote.", None

    # find target by number
    target = next((p for p in game.players.values() if p.number == number), None)
    if target is None: return "Invalid player number.", None
    if target.id == voter.id: return "You cannot vote for yourself.", None
    if not target.alive: return "You cannot vote for a dead player.", None

    # success
    voter.vote = target.id

    # announce in town channel
    channel = ctx.guild.get_channel(game.town_channel_id)
    if channel:
        await channel.send(
            f"🗳️ {voter.name} has voted for {target.name}!"
        )

    return (
        f"You voted for {target.name}.",
        target.name
    )


def clear_vote(player):
    player.vote = None

async def on_vote(ctx, game):
    votedOutPlayer = tally_votes(game)
    if votedOutPlayer:
        votedOutPlayer.votedFor = True
        game.can_vote = False
        channel = ctx.guild.get_channel(game.town_channel_id)
        if channel:
            await channel.send(f"The castlefolk have voted against {votedOutPlayer.name}!")
            await channel.send(f"{votedOutPlayer.name}, state your defence!")

def tally_votes(game):
    # count votes
    vote_count = {}

    for voter in game.players.values():
        if not voter.alive:
            continue
        if voter.vote is None:
            continue

        vote_count[voter.vote] = vote_count.get(voter.vote, 0) + 1

    # number of alive players
    alive_players = [p for p in game.players.values() if p.alive]
    alive_count = len(alive_players)

    if alive_count == 0:
        return None

    # majority rule: more than half alive (ceil)
    majority_needed = (alive_count // 2) + 1

    # find player who reached majority
    for player_id, count in vote_count.items():
        if count >= majority_needed:
            return game.players.get(player_id)

    return None

async def castDecision(game, ctx, choice):
    player = game.players.get(ctx.author.id)

    if player is None: return "You are not part of the game."
    if not player.alive: return "Dead players cannot vote."
    if player.votedFor: return "You cannot vote on yourself."

    if choice not in ["guilty", "innocent"]: return "Invalid vote."

    player.decision = choice
    channel = ctx.guild.get_channel(game.town_channel_id)
    if channel:
        await channel.send(f"🗳️ {player.name} has voted")

    return f"You voted {choice.upper()}."

async def decideEnd(ctx, game):
    game.canDecide = False
    guilty = 0
    innocent = 0
    lines = ["**🧾 Trial Results**\n"]

    channel = ctx.guild.get_channel(game.town_channel_id)
    ordered = sorted(game.players.values(), key=lambda p: p.number)
    lines = ["**🧾 Trial Results**\n"]

    for p in ordered:
        # abstained (never voted or cleared vote)
        if p.decision is None:
            lines.append(f"{p.name} abstained")
        else:
            lines.append(f"{p.name} voted {p.decision.upper()}")
            if p.decision == "guilty":
                guilty += 1
            elif p.decision == "innocent":
                innocent += 1

    await channel.send("\n".join(lines))

    accused = next((p for p in game.players.values() if getattr(p, "votedFor", False)), None)
    if accused is None: 
        await channel.send("Game is cooked. Should be an accused player at this point.")
        return

    if guilty > innocent:
        await channel.send(
                f"⚖️ The castlefolk have voted to lynch {accused.name}.\n" # type: ignore
                f"Any last words?"
            )
        accused.alive = False
        await channel.send(
                f"{accused.name}'s role was: {accused.role}"
            )
        if not checkWin(game):
            game.isDay = False
    else:
        game.can_vote = True
        await channel.send(
            f"{accused.name} has been spared"
        )

    #Reset voting
    for p in game.players.values():
        p.vote = None
        p.decision = None
        p.votedFor = False
