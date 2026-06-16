import discord

from gamestate import GameState
from utils import getByRole, isGameOver, kill
from timing import countdown
from UI.JudgeViewer import JudgeView

async def on_vote(guild, game: GameState):
    votedOutPlayer = tally_votes(game)
    if votedOutPlayer:
        votedOutPlayer.votedFor = True
        game.can_vote = False
        channel = guild.get_channel(game.town_channel_id)
        if channel:
            await channel.send(f"The castlefolk have voted against {votedOutPlayer.name}!")
            await channel.send(f"{votedOutPlayer.name}, state your defence!")
            await countdown(channel, 2, prefix="Defence statement: ")
            await decidePhase(guild, game)

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

async def decideEnd(guild, game: GameState):
    game.canDecide = False
    guilty = 0
    innocent = 0
    lines = ["**🧾 Trial Results**\n"]

    channel = guild.get_channel(game.town_channel_id)
    ordered = sorted(game.players.values(), key=lambda p: p.number)

    accused = getVotedForPlayer(game)
    for p in ordered:
        if accused and p.id == accused.id: continue

        # abstained (never voted or cleared vote)
        if p.decision is None:
            lines.append(f"⚪ {p.name} abstained")
        else:
            weight = 1
            if p.role == "Mayor" and p.revealed: weight = 3
            if p.decision == "guilty":
                lines.append(f"🟥 {p.name} voted GUILTY")
                guilty += weight
                
            elif p.decision == "innocent":
                lines.append(f"🟩 {p.name} voted INNOCENT")
                innocent += weight

    await channel.send("\n".join(lines))

    if accused is None: 
        await channel.send("Game is cooked. Should be an accused player at this point.")
        return

    if guilty > innocent:
        if accused.role == "Jester":
            guilty_voters = [p.id for p in ordered if p.alive and p.decision != "innocent" and (not accused or p.id != accused.id)]
            accused.guiltyVoters = guilty_voters
            accused.win = True
            await channel.send(f"You FOOLS! {accused.name} is the Jester! He will seek revenge...")
        else:
            await channel.send(f"⚖️ The castlefolk have voted to lynch {accused.name}.\n"f"Any last words?")
            await countdown(channel, 12, prefix="Last words: ")

        executioner = getByRole(game.players, 'Executioner')
        if executioner and executioner.executioner_target == accused.id:
            executioner.win = True
            await channel.send(f"🎯 The Executioner has succeeded! " f"{accused.name} was their target.")
        await kill(guild, game, accused, f"{accused.name} was lynched.", None)
        await isGameOver(guild, game)
    else:
        game.can_vote = True 
        await channel.send(f"{accused.name} has been spared")

    #Reset voting
    for p in game.players.values():
        p.vote = None
        p.decision = None
        p.votedFor = False

async def decidePhase(guild, game):
    accused = getVotedForPlayer(game)
    if accused is None: return "Nobody is currently on trial."
        
    game.canDecide = True
    channel = guild.get_channel(game.town_channel_id)
    await channel.send(f"Place your decision: Is {accused.name} guilty or innocent?")
    await sendDecision(guild, game)
    await countdown(channel, 20, prefix="Place your decision: ")
    await decideEnd(guild, game)

def getVotedForPlayer(game):
    return next((p for p in game.players.values() if p.votedFor), None)

async def sendDecision(guild, game):
    for player in game.players.values():
        if not player.alive or player.votedFor: continue

        channel_name = player.name.lower().replace(" ", "-")
        channel = discord.utils.get(guild.text_channels, name=channel_name)

        if channel is None: continue

        view = JudgeView(game, player.id)
        await channel.send("⚖️ Place your decision: Guilty or Innocent?", view=view)