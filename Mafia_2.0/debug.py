from gamestate import GameState

async def debugPlayers(game: GameState):
    ordered = sorted(game.players.values(), key=lambda p: p.number)
    lines = ["**Current Players**\n"]

    for p in ordered:
        status = "🟢" if p.alive else "🔴"

        lines.append(
            f"{p.number}. {p.name} | "
            f"Role: `{p.role}` | "
            f"{status}"
        )

    message = "**Current Players**\n\n" + "\n".join(lines)
    return message