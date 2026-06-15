import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

from channelStuff import buildWinsLeaderboard, endChannels, setup_channels
from dayNight import day, passTime
from gamestate import GameState
from playerCreation import sendStarterInfo, setup_players
from debug import debugPlayers
from utils import getPlayerList, setMuderNote
from voting import castDecision, clear_vote, decideEnd, decidePhase, on_vote, sendVote
from roleActions import alertVeteran, jailorKill, sayJail, setTarget, revealMayor
from scoring import initWinsFile

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
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    global player_count
    player_count = sum(1 for member in bot.guilds[0].members if not member.bot)
    initWinsFile()
    print(f'Players: {player_count}\n Ready to rumble!')

@bot.command()
async def start(ctx):
    if ctx.author.id != BYRO_ID: return

    guild = ctx.guild
    setup_players(guild, game, BYRO_ID)
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
async def n(ctx): await passTime(ctx.guild, game)

@bot.command()
async def vote(ctx, number: int):
    feedback, voted_for = await sendVote(game, ctx, number)
    await ctx.send(feedback)
    if (voted_for): await on_vote(ctx, game)
    
@bot.command()
async def decide(ctx):
    feedback = await decidePhase(ctx, BYRO_ID, game)
    await ctx.send(feedback)

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
async def list(ctx): await ctx.send(getPlayerList(game))

@bot.command()
async def target(ctx, number: int):
    feedback = await setTarget(game, ctx, number)
    await ctx.send(feedback)

@bot.command() #Mayor
async def reveal(ctx): await ctx.send(await revealMayor(game, ctx))

@bot.command() #Veteran
async def alert(ctx): await ctx.send(await alertVeteran(game, ctx))

@bot.command() #Jailor execute
async def kill(ctx): 
    feedback = await jailorKill(game, ctx)
    if feedback: await ctx.send(feedback)

@bot.command() #Jail speak
async def say(ctx, *, message: str):
    feedback =await sayJail(game, ctx, message)
    if feedback: await ctx.send(feedback)

@bot.command() #Deathnote
async def m(ctx, *, message: str): await ctx.send(await setMuderNote(game, ctx, message))

@bot.command()
async def debugplayers(ctx):
    if ctx.author.id != BYRO_ID: return
    message = await debugPlayers(game)
    await ctx.send(message)

@bot.command() #Leaderboard
async def wins(ctx): await ctx.send(buildWinsLeaderboard(ctx))

player_count = 0
bot.run(token,log_handler=handler, log_level=logging.DEBUG) # type: ignore