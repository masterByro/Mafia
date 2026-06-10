def getPlayerList(game):
    # Build ordered player list
    ordered = sorted(game.players.values(), key=lambda p: p.number)

    lines = ["**Current Players**\n"]

    for p in ordered:
        status = "🟢 Alive" if p.alive else "🔴 Dead"

        lines.append(
            f"{p.number}. {p.name} | {status}"
        )

    return "\n".join(lines)


def checkWin(game):
    pass