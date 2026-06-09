import random
import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

from player import Player
from playerCreation import makeRoles, sendStarterInfo

load_dotenv()

token = os.getenv('DISCORD_TOKEN')
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
BYRO_ID = 240752638273126400 

players = {}
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
    print("hello world 2")
    if ctx.author.id != BYRO_ID:
        return

    guild = ctx.guild
    byron = guild.get_member(BYRO_ID)

    roles = makeRoles(len(players))
    random.shuffle(roles)

    for member in guild.members:
        if not member.bot:
            players[member.id] = Player(member)

    category = discord.utils.get(guild.categories, name="Mafia Players")
    if category is None:
        category = await guild.create_category("Mafia Players")

    ## Channel creation and permission setup
    for player, role in zip(players.values(), roles):
        
        player.role = role
        channel_name = player.name.lower().replace(" ", "-")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                view_channel=False
            ),
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

        await guild.create_text_channel(
            name=channel_name,
            overwrites=overwrites,
            category=category
        )
    await sendStarterInfo(guild, players)
    await ctx.send("Game started!")
    await ctx.send(players)


@bot.command()
async def end(ctx):
    if ctx.author.id != BYRO_ID:
        return
    
    players.clear()
    category = discord.utils.get(ctx.guild.categories, name="Mafia Players")

    if category is None:
        await ctx.send("No Mafia Players category found.")
        return

    # Delete all channels in the category
    for channel in category.channels:
        await channel.delete()

    # Delete the category itself
    await category.delete()
    await ctx.send("Game ended!")

player_count = 0



bot.run(token,log_handler=handler, log_level=logging.DEBUG) # type: ignore