from types import SimpleNamespace
from gamestate import GameState
from playerCreation import sendStarterInfo, setup_players
from channelStuff import setup_channels

async def setup_no_friends(guild, game: GameState, ADMIN_ID):
    #Add more members
    members = list(guild.members)
    
    # Add fake members
    members.extend([
        SimpleNamespace(id=1, name="Thomas", display_name="Thomas", bot=False),
        SimpleNamespace(id=2, name="John", display_name="John", bot=False),
        SimpleNamespace(id=3, name="Philip", display_name="Philip", bot=False),
        # SimpleNamespace(id=4, name="Taylor", display_name="Taylor", bot=False),
        # SimpleNamespace(id=5, name="SillyWilly", display_name="SillyWilly", bot=False),

    ])  

    fake_guild = SimpleNamespace(
        members=members,
        id=guild.id,
        name=guild.name
    )

    setup_players(fake_guild, game, ADMIN_ID)
    await setup_channels(guild, game, ADMIN_ID)
    await sendStarterInfo(guild, game)
    