import random
import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

from dayNight import day
from gamestate import GameState
from playerCreation import makeRoles, sendStarterInfo, setup_players

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
    if ctx.author.id != BYRO_ID:
        return

    guild = ctx.guild
    byron = guild.get_member(BYRO_ID)
    
    setup_players(guild, game)

    town_channel = await guild.create_text_channel(
        name="courtyard",
        overwrites={
            guild.default_role: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=False
            ),
            guild.me: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )
        }
    )
    game.town_channel_id = town_channel.id

    category = await guild.create_category("Mafia Players")

    ## Channel creation and permission setup
    for player in game.players.values():
        channel_name = player.name.lower().replace(" ", "-")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            player.member: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            ),
            byron: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )
        }

        channel = await guild.create_text_channel(
                name=channel_name,
                overwrites=overwrites,
                category=category
            )
        game.player_channels[player.id] = channel.id

    await sendStarterInfo(guild, game.players)
    channel = guild.get_channel(game.town_channel_id)
    game.running = True
    await ctx.send("Game started!")
    await day(game)


@bot.command()
async def end(ctx):
    global game
    if ctx.author.id != BYRO_ID:
        return
    
    guild = ctx.guild
    for channel_id in game.player_channels.values():
        channel = guild.get_channel(channel_id)
        if channel:
            await channel.delete()
    category = discord.utils.get(guild.categories, name="Mafia Players")
    if category:
        await category.delete()
    game = GameState()
    await ctx.send("Game ended!")

player_count = 0

@bot.command()
async def n(ctx):
    game.is_day = not game.is_day
    game.day_number += 1
    if game.is_day:
        game.can_vote = True
        await ctx.send(f"Day {game.day_number} has begun!")

player_count = 0

bot.run(token,log_handler=handler, log_level=logging.DEBUG) # type: ignore