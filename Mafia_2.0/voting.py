
from gamestate import GameState
from utils import getByRole, isGameOver, kill
from channelStuff import sendDecideInfo

async def sendVote(game: GameState, ctx, number):
    if not game.can_vote: return "You cannot vote right now.", None

    voter = game.players.get(ctx.author.id)
    if voter is None: return "You are not part of the game.", None
    if not voter.alive: return "Dead players cannot vote.", None

    # find target by number
    target = next((p for p in game.players.values() if p.number == number), None)
    if target is None: return "Invalid player number.", None
    #if target.id == voter.id: return "You cannot vote for yourself.", None TODO: UNCOMMENT
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

async def on_vote(ctx, game: GameState):
    votedOutPlayer = tally_votes(game)
    if votedOutPlayer:
        votedOutPlayer.votedFor = True
        game.can_vote = False
        channel = ctx.guild.get_channel(game.town_channel_id)
        if channel:
            await channel.send(f"The castlefolk have voted against {votedOutPlayer.name}!")
            await channel.send(f"{votedOutPlayer.name}, state your defence!")

def tally_votes(game: GameState):
    vote_count = {}

    for voter in game.players.values():
        if not voter.alive: continue
        if voter.vote is None: continue

        weight = 1
        if voter.role == "Mayor" and voter.revealed: weight = 3
        vote_count[voter.vote] = vote_count.get(voter.vote, 0) + weight

    # number of alive players
    alive_players = [p for p in game.players.values() if p.alive]
    alive_count = len(alive_players)

    if alive_count == 0: return None

    # majority rule: more than half alive (ceil)
    majority_needed = (alive_count // 2) + 1

    # find player who reached majority
    for player_id, count in vote_count.items():
        if count >= majority_needed:
            return game.players.get(player_id)

    return None

async def castDecision(game: GameState, ctx, choice):
    player = game.players.get(ctx.author.id)
    if game.canDecide == False: return "You cannot cast a decision right now."
    if player is None: return "You are not part of the game."
    if not player.alive: return "Dead players cannot vote."
    if player.votedFor: return "You cannot vote on yourself."

    if choice not in ["guilty", "innocent"]: return "Invalid vote."

    player.decision = choice
    channel = ctx.guild.get_channel(game.town_channel_id)
    if channel:
        await channel.send(f"🗳️ {player.name} has voted")

    return f"You voted {choice.upper()}."

async def decideEnd(ctx, game: GameState):
    game.canDecide = False
    guilty = 0
    innocent = 0
    lines = ["**🧾 Trial Results**\n"]

    channel = ctx.guild.get_channel(game.town_channel_id)
    ordered = sorted(game.players.values(), key=lambda p: p.number)
    lines = ["**🧾 Trial Results**\n"]

    accused = getVotedForPlayer(game)
    guilty_voters = []

    for p in ordered:
        if accused and p.id == accused.id: continue

        # abstained (never voted or cleared vote)
        if p.decision is None:
            lines.append(f"{p.name} abstained")
        else:
            weight = 1
            if p.role == "Mayor" and p.revealed: weight = 3
            lines.append(f"{p.name} voted {p.decision.upper()}")
            if p.decision == "guilty":
                guilty += weight
                guilty_voters.append(p.id)
            elif p.decision == "innocent":
                innocent += weight

    await channel.send("\n".join(lines))

    if accused is None: 
        await channel.send("Game is cooked. Should be an accused player at this point.")
        return

    if guilty > innocent:
        if accused.role == "Jester":
            accused.guiltyVoters = guilty_voters
            accused.win = True
            await channel.send(f"You FOOLS! {accused.name} is the Jester! He will seek revenge...")
        else: await channel.send(f"⚖️ The castlefolk have voted to lynch {accused.name}.\n"f"Any last words?")

        executioner = getByRole(game.players, 'Executioner')
        if executioner and executioner.executioner_target == accused.id:
            executioner.win = True
            await channel.send(f"🎯 The Executioner has succeeded! " f"{accused.name} was their target.")
        await kill(ctx.guild, game, accused, f"{accused.name} was lynched.")
        await isGameOver(ctx.game, game)
    else:
        game.can_vote = True 
        await channel.send(f"{accused.name} has been spared")

    #Reset voting
    for p in game.players.values():
        p.vote = None
        p.decision = None
        p.votedFor = False

async def decidePhase(ctx, BYRO_ID, game):
    if ctx.author.id != BYRO_ID: return
    accused = getVotedForPlayer(game)
    if accused is None: return "Nobody is currently on trial."
        
    game.canDecide = True
    channel = ctx.guild.get_channel(game.town_channel_id)
    await channel.send(f"Place your decision: Is {accused.name} guilty or innocent?")
    await sendDecideInfo(ctx.guild, game.players, accused)

def getVotedForPlayer(game):
    return next((p for p in game.players.values() if p.votedFor), None)
