import discord

async def setup_channels(guild, game, BYRO_ID):
    byron = guild.get_member(BYRO_ID)


    # Dead chat
    dead_role = discord.utils.get(guild.roles, name="Dead")
    game.dead_role_id = dead_role.id
    overwrites = {guild.default_role: discord.PermissionOverwrite(view_channel=False),
            dead_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True,send_messages=True,read_message_history=True)
        }
    dead_channel = await guild.create_text_channel(name="dead-chat", overwrites=overwrites)
    game.dead_channel_id = dead_channel.id

 
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


import discord

async def endChannels(ctx, game):
    guild = ctx.guild

    # -------------------------
    # Delete player channels
    # -------------------------
    for channel_id in game.player_channels.values():
        channel = guild.get_channel(channel_id)
        if channel:
            await channel.delete()

    # -------------------------
    # Delete category
    # -------------------------
    category = discord.utils.get(guild.categories, name="Mafia Players")
    if category:
        await category.delete()

    # -------------------------
    # Delete town channel
    # -------------------------
    if game.town_channel_id is not None:
        channel = guild.get_channel(game.town_channel_id)
        if channel:
            await channel.delete()

    # -------------------------
    # Delete dead chat
    # -------------------------
    if getattr(game, "dead_channel_id", None) is not None:
        dead_channel = guild.get_channel(game.dead_channel_id)
        if dead_channel:
            await dead_channel.delete()