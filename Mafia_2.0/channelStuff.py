import discord

async def setup_channels(guild, game, BYRO_ID):
    byron = guild.get_member(BYRO_ID)

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

    ## Individual channels
    category = await guild.create_category("Mafia Players")
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