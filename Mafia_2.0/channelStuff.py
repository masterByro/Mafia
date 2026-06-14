import discord

from gamestate import GameState

async def setup_channels(guild, game: GameState, BYRO_ID):
    byron = guild.get_member(BYRO_ID)

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
    category = await guild.create_category("Mafia Players")
    for player in game.players.values():
        channel_name = player.name.lower().replace(" ", "-")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            player.member: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            byron: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }

        channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites, category=category)
        game.player_channels[player.id] = channel.id

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
        name="mafia-chat",
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
        if channel:
            await channel.delete()

    # Delete category
    category = discord.utils.get(guild.categories, name="Mafia Players")
    if category:
        await category.delete()

    courtyard = guild.get_channel(game.town_channel_id)
    if courtyard: await courtyard.delete()
    
    dead_channel = guild.get_channel(game.dead_channel_id)
    if dead_channel: await dead_channel.delete()
    
    mafia_channel = guild.get_channel(game.mafia_channel_id)
    if mafia_channel: await mafia_channel.delete()

async def sendVoteInfo(guild, players):
    message = f"\nDuring the day you can vote to place a player on trial, by typing the command  `!vote <player id>`"
    await sendPlayersInfo(guild, players, message)

async def sendDecideInfo(guild, players, onTrialPlayer):
    message = (f"Place your decision: Is {onTrialPlayer.name} guilty or innocent?\nType `!guilty`, `!innocent` or abstain from voting")
    await sendPlayersInfo(guild, players, message)

async def sendPlayersInfo(guild, players, message):
    # send messages
    for player in players.values():
        if not player.alive: continue
        channel_name = player.name.lower().replace(" ", "-")
        channel = discord.utils.get(guild.text_channels, name=channel_name)
        if channel is None: continue
        await channel.send(message)
