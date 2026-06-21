from types import SimpleNamespace
from gamestate import GameState
from playerCreation import sendStarterInfo, setup_players
from channelStuff import setup_channels

async def setup_no_friends(guild, game: GameState, BYRO_ID):
    #Add more members
    members = list(guild.members)
    
    # Add fake members
    members.extend([
        SimpleNamespace(id=1, name="Alice", display_name="Alice", bot=False),
        SimpleNamespace(id=2, name="Bob", display_name="Bob", bot=False),
        SimpleNamespace(id=3, name="Charlie", display_name="Charlie", bot=False),
    ])

    fake_guild = SimpleNamespace(
        members=members,
        id=guild.id,
        name=guild.name
    )

    setup_players(fake_guild, game, BYRO_ID)
    await setup_channels(guild, game, BYRO_ID)
    await sendStarterInfo(guild, game)
    