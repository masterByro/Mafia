import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

from channelStuff import buildWinsLeaderboard, endChannels, setup_channels
from dayNight import day, passTime
from gamestate import GameState
from playerCreation import sendStarterInfo, setup_players
from debug import debugPlayers, clear_debug
from utils import getPlayerList, setMurderNote
from voting import decideEnd, decidePhase
from scoring import initWinsFile
from noFriends import setup_no_friends

load_dotenv()

token = os.getenv('DISCORD_TOKEN')
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
ADMIN_ID = 1518055811278967005
BYRO_ID = 430972166364725249
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
@commands.check(lambda ctx: ctx.author.id in (ADMIN_ID, BYRO_ID))
async def start(ctx):
    guild = ctx.guild
    game.nofriends = False
    setup_players(guild, game, ADMIN_ID)
    await setup_channels(guild, game, ADMIN_ID)
    await sendStarterInfo(guild, game)
    game.running = True
    await ctx.send("Game started!")
    await day(guild, game)

@bot.command()
@commands.check(lambda ctx: ctx.author.id in (ADMIN_ID, BYRO_ID))
async def end(ctx):
    global game
    
    await endChannels(ctx, game)
    dead_role = discord.utils.get(ctx.guild.roles, name="Dead")
    if dead_role:
        for member in dead_role.members:
            await member.remove_roles(dead_role)
    
    # RESET GAME STATE COMPLETELY
    game = GameState()
    clear_debug()
    await ctx.send("Game ended! State reset.")

@bot.command()
@commands.check(lambda ctx: ctx.author.id in (ADMIN_ID, BYRO_ID))
async def n(ctx): 
    await passTime(ctx.guild, game)

@bot.command() #Depreacted
@commands.check(lambda ctx: ctx.author.id in (ADMIN_ID, BYRO_ID))
async def decide(ctx):
    feedback = await decidePhase(ctx.guild, game)
    await ctx.send(feedback)

@bot.command() #Depreacted
@commands.check(lambda ctx: ctx.author.id in (ADMIN_ID, BYRO_ID))
async def decideend(ctx):
    await decideEnd(ctx.guild, game)
    
@bot.command()
async def list(ctx): await ctx.send(getPlayerList(game))

@bot.command() #Deathnote
async def m(ctx, *, message: str): await ctx.send(await setMurderNote(game, ctx, message))

@bot.command()
@commands.check(lambda ctx: ctx.author.id in (ADMIN_ID, BYRO_ID))
async def debugplayers(ctx):
    message = await debugPlayers(game)
    await ctx.send(message)

@bot.command() #Leaderboard
async def wins(ctx): await ctx.send(buildWinsLeaderboard(ctx))

@bot.command()
@commands.check(lambda ctx: ctx.author.id in (ADMIN_ID, BYRO_ID))
async def test(ctx, seed: str = None):
    guild = ctx.guild
    game.nofriends = True
    await setup_no_friends(guild, game, ADMIN_ID, seed.lower())
    game.running = True
    await ctx.send(f"{seed.capitalize()} game started with no friends.")
    await day(guild, game)

player_count = 0
bot.run(token,log_handler=handler, log_level=logging.DEBUG) # type: ignore