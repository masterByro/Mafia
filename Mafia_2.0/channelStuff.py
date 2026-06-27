import discord

from gamestate import GameState
from scoring import loadWins
from UI.VoteSelecter import VoteView

async def setup_channels(guild, game: GameState, ADMIN_ID):
    admin = guild.get_member(ADMIN_ID)

    # Courtyard
    town_channel = await guild.create_text_channel(
        name="courtyard",
        overwrites={
            guild.default_role: discord.PermissionOverwrite(view_channel=True, send_messages=False),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }
    )
    game.town_channel_id = town_channel.id

    ## Individual channels
    category = await guild.create_category("Players")
    for player in game.players.values():
        channel_name = player.name.lower().replace(" ", "-")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
        }

        # nofriends Mode 
        # player.member isn't always a valid discord user. 
        if not game.nofriends:
            overwrites[player.member] = discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True
        )

        channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites, category=category)
        game.player_channels[player.id] = channel.id
        will_channel = await guild.create_text_channel(name=f"{channel_name}-will", overwrites=overwrites, category=category)
        game.player_will_channels[player.id] = will_channel.id
        await will_channel.send("Use this channel to write your will. " "Anything written here may be revealed after your death.")
        
    # Dead chat
    dead_role = discord.utils.get(guild.roles, name="Dead")
    game.dead_role_id = dead_role.id
    overwrites = {guild.default_role: discord.PermissionOverwrite(view_channel=False),
            dead_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True,send_messages=True,read_message_history=True)
        }
    dead_channel = await guild.create_text_channel(name="dead-chat", overwrites=overwrites)
    game.dead_channel_id = dead_channel.id

    mafia_channel = await guild.create_text_channel(
        name="Uprising-chat",
        overwrites={guild.default_role: discord.PermissionOverwrite( view_channel=False),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }
    )
    game.mafia_channel_id = mafia_channel.id

async def endChannels(ctx, game: GameState):
    guild = ctx.guild

    # Delete player channels
    for channel_id in game.player_channels.values():
        channel = guild.get_channel(channel_id)
        if channel: await channel.delete()

    for channel_id in game.player_will_channels.values():
        channel = guild.get_channel(channel_id)
        if channel: await channel.delete()

    # Delete category
    category = discord.utils.get(guild.categories, name="Players")
    if category:
        await category.delete()

    courtyard = guild.get_channel(game.town_channel_id)
    if courtyard: await courtyard.delete()
    
    dead_channel = guild.get_channel(game.dead_channel_id)
    if dead_channel: await dead_channel.delete()
    
    mafia_channel = guild.get_channel(game.mafia_channel_id)
    if mafia_channel: await mafia_channel.delete()

async def sendVoteDropdown(guild, game):
    for player in game.players.values():
        if not player.alive: continue

        channel_name = player.name.lower().replace(" ", "-")
        channel = discord.utils.get(guild.text_channels, name=channel_name)

        if channel is None: continue
        await channel.send("🗳️ Vote for who should go on trial:", view=VoteView(game, player.id))

def buildWinsLeaderboard(ctx):
    wins = loadWins()
    if not wins: return "No wins recorded yet."

    sorted_wins = sorted(wins.items(), key=lambda x: x[1], reverse=True)
    lines = ["🏆 **Win Leaderboard**\n"]
    for i, (user_id, count) in enumerate(sorted_wins[:10], start=1):
        member = ctx.guild.get_member(int(user_id))
        name = member.display_name if member else f"Unknown ({user_id})"
        lines.append(f"{i}. {name} — {count} win(s)")

    return "\n".join(lines)