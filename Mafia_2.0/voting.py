import discord

from gamestate import GameState
from utils import getByRole, isGameOver, kill
from timing import countdown
from UI.JudgeViewer import JudgeView
from dayNight import passTime

async def on_vote(guild, game: GameState):
    votedOutPlayer = tally_votes(game)
    if votedOutPlayer:
        votedOutPlayer.votedFor = True
        game.can_vote = False
        channel = guild.get_channel(game.town_channel_id)
        if channel:
            await channel.send(f"The castlefolk have voted against {votedOutPlayer.name}!")
            await channel.send(f"{votedOutPlayer.name}, state your defence!")
            # nofriends Mode - disable countdown
            if not game.nofriends: await countdown(channel, 15, prefix="Defence statement")
            await decidePhase(guild, game)

def tally_votes(game: GameState):
    vote_count = {}

    for voter in game.players.values():
        if not voter.alive: continue
        if voter.vote is None: continue

        weight = 1
        if voter.role == "Chancellor" and voter.revealed: weight = 3
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

async def display_trial_results(guild, game: GameState):
    """Display trial voting results and return vote counts."""
    lines = ["**🧾 Trial Results**\n"]
    guilty = 0
    innocent = 0

    channel = guild.get_channel(game.town_channel_id)
    ordered = sorted(game.players.values(), key=lambda p: p.number)
    accused = getVotedForPlayer(game)

    for p in ordered:
        if accused and p.id == accused.id: continue
        if not p.alive: continue

        if p.decision is None:
            lines.append(f"⚪ {p.name} abstained")
        else:
            weight = 1
            if p.role == "Chancellor" and p.revealed: 
                weight = 3
            
            if p.decision == "guilty":
                lines.append(f"🟥 {p.name} voted GUILTY")
                guilty += weight
            elif p.decision == "innocent":
                lines.append(f"🟩 {p.name} voted INNOCENT")
                innocent += weight

    await channel.send("\n".join(lines))
    return guilty, innocent

async def handle_guilty_verdict(guild, game: GameState, accused):
    """Handle verdict when player is lynched."""
    channel = guild.get_channel(game.town_channel_id)
    ordered = sorted(game.players.values(), key=lambda p: p.number)

    if accused.role == "Jester":
        guilty_voters = [p.id for p in ordered if p.alive and p.decision != "innocent" and p.id != accused.id]
        accused.guiltyVoters = guilty_voters
        accused.win = True
        await channel.send(f"You FOOLS! {accused.name} is the Jester! He will seek revenge...")
    else:
        await channel.send(f"⚖️ The castlefolk have voted to lynch {accused.name}.\n"f"Any last words?")
        # nofriends Mode - disable countdown        
        if not game.nofriends: await countdown(channel, 12, prefix="Last words")

    executioner = getByRole(game.players, 'Executioner')
    if executioner and executioner.executioner_target == accused.id:
        executioner.win = True
        await channel.send(f"🎯 The Executioner has succeeded! " f"{accused.name} was their target.")
    
    await kill(guild, game, accused, f"{accused.name} was lynched.", None)
    await isGameOver(guild, game)
    await passTime(guild, game)

async def handle_innocent_verdict(guild, game: GameState, accused):
    """Handle verdict when player is spared."""
    channel = guild.get_channel(game.town_channel_id)
    
    game.voteAttempts -= 1
    await channel.send(f"{accused.name} has been spared")
    
    if game.voteAttempts > 0:
        await channel.send(f"Vote attempts remaining: {game.voteAttempts}")
        from channelStuff import sendVoteDropdown
        await sendVoteDropdown(guild, game)
        game.can_vote = True
    else:
        await channel.send("No more voting attempts. Moving to night...")
        await passTime(guild, game)

def reset_voting(game: GameState):
    """Reset all voting state for next round."""
    for p in game.players.values():
        p.vote = None
        p.decision = None
        p.votedFor = False

async def decideEnd(guild, game: GameState):
    """Main trial verdict orchestrator."""
    game.canDecide = False
    channel = guild.get_channel(game.town_channel_id)
    accused = getVotedForPlayer(game)

    # Display votes and get counts
    guilty, innocent = await display_trial_results(guild, game)

    # Validate accused exists
    if accused is None: 
        await channel.send("Game is cooked. Should be an accused player at this point.")
        return

    # Determine verdict
    if guilty > innocent:
        await handle_guilty_verdict(guild, game, accused)
    else:
        await handle_innocent_verdict(guild, game, accused)

    # Reset voting
    reset_voting(game)

async def decidePhase(guild, game):
    accused = getVotedForPlayer(game)
    if accused is None: return "Nobody is currently on trial."
        
    game.canDecide = True
    channel = guild.get_channel(game.town_channel_id)
    await channel.send(f"Place your decision: Is {accused.name} guilty or innocent?")
    await sendDecision(guild, game)
    # nofriends Mode - disable countdown       
    if not game.nofriends: await countdown(channel, 20, prefix="Place your decision")
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