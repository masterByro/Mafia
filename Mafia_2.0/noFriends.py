from types import SimpleNamespace
from gamestate import GameState
from playerCreation import sendStarterInfo, setup_players
from channelStuff import setup_channels
import json
from types import SimpleNamespace
from pathlib import Path

async def setup_no_friends(guild, game: GameState, ADMIN_ID, seed):
    members = []
    seed = seed if seed else "base"
    # Load fake users from seed file
    seed_path = Path(f"seeds/{seed}.json")
    if seed_path.exists():
        with seed_path.open("r", encoding="utf-8") as f:
            fake_users = json.load(f)

        members.extend([
            SimpleNamespace(
                id=u["id"],
                name=u["name"],
                display_name=u.get("display_name", u["name"]),
                bot=False
            )
            for u in fake_users
        ])

    fake_guild = SimpleNamespace(
        members=members,
        id=guild.id,
        name=guild.name
    )

    setup_players(fake_guild, game, ADMIN_ID)
    apply_overrides(game, fake_users)
    await setup_channels(guild, game, ADMIN_ID)
    await sendStarterInfo(guild, game)


def apply_overrides(game, overrides):
    players = game.players

    for entry in overrides:
        try:
            player = players[entry["id"]]
        except (KeyError, TypeError):
            continue

        for key, value in entry.items():
            if key == "id":
                continue

            setattr(player, key, value)