import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

from channelStuff import endChannels, setup_channels
from dayNight import day, night
from gamestate import GameState
from playerCreation import sendStarterInfo, setup_players
from debug import debugPlayers
from utils import getPlayerList, getVotedForPlayer, setAction
from voting import castDecision, clear_vote, decideEnd, on_vote, sendVote

load_dotenv()

token = os.getenv('DISCORD_TOKEN')
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
BYRO_ID = 240752638273126400 
global game
game = GameState()

@bot.event
async def on_member_join(member):
    global player_count

    if not member.bot:
        player_count += 1


@bot.event
async def on_member_remove(member):
    global player_count

    if not member.bot:
        player_count -= 1
        

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    
    global player_count
    player_count = sum(
        1 for member in bot.guilds[0].members
        if not member.bot
    )
    print(f'Players: {player_count}')

@bot.command()
async def start(ctx):
    if ctx.author.id != BYRO_ID: return

    guild = ctx.guild
    setup_players(guild, game)
    await setup_channels(guild, game, BYRO_ID)
    await sendStarterInfo(guild, game.players)
    game.running = True
    await ctx.send("Game started!")
    await day(guild, game)


@bot.command()
async def end(ctx):
    if ctx.author.id != BYRO_ID: return
    
    await endChannels(ctx, game)
    dead_role = discord.utils.get(ctx.guild.roles, name="Dead")
    if dead_role:
            for member in dead_role.members:
                await member.remove_roles(dead_role)
    await ctx.send("Game ended!")

@bot.command()
async def n(ctx):
    game.is_day = not game.is_day
    game.day_number += 1
    if game.is_day:
        await day(ctx.guild, game)
    else:
        await night(ctx.guild, game)


@bot.command()
async def vote(ctx, number: int):
    feedback, voted_for = await sendVote(game, ctx, number)
    await ctx.send(feedback)
    if (voted_for):
        await on_vote(ctx, game)
    
@bot.command()
async def decide(ctx):
    if ctx.author.id != BYRO_ID: return
    accused = getVotedForPlayer(game)
    if accused is None:
        await ctx.send("Nobody is currently on trial.")
        return
    
    game.canDecide = True
    channel = ctx.guild.get_channel(game.town_channel_id)
    if channel:
        await channel.send(f"Place your decision: Is {accused.name} guilty or innocent?")

@bot.command()
async def guilty(ctx):
    response = await castDecision(game, ctx, "guilty")
    await ctx.send(response)

@bot.command()
async def innocent(ctx):
    response = await castDecision(game, ctx, "innocent")
    await ctx.send(response)

@bot.command()
async def decideend(ctx):
    if ctx.author.id != BYRO_ID: return
    
    await decideEnd(ctx, game)
    
    channel = ctx.guild.get_channel(game.town_channel_id)
    await channel.send(f"Place your decision: Is {player.votedFor.name} guilty or innocent?") # type: ignore
    
# TODO: Uplift user feedback 
@bot.command()
async def voteclear(ctx):
    player = game.players.get(ctx.author.id)
    clear_vote(player)

@bot.command()
async def list(ctx):
    await ctx.send(getPlayerList(game))

@bot.command()
async def action(ctx, number: int):
    feedback, success = await setAction(game, ctx, number)
    await ctx.send(feedback)

@bot.command()
async def debugplayers(ctx):
    if ctx.author.id != BYRO_ID: return
    message = await debugPlayers(game)
    await ctx.send(message)

player_count = 0
bot.run(token,log_handler=handler, log_level=logging.DEBUG) # type: ignore