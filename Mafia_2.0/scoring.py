import json
import os

STATS_FILE = "wins.json"

def loadWins():
    if not os.path.exists(STATS_FILE):
        return {}

    with open(STATS_FILE, "r") as f:
        return json.load(f)

def saveWins(data):
    with open(STATS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def updateWins(game):
    wins = loadWins()
    for player in game.players.values():
        if player.win:
            pid = str(player.id)

            if pid not in wins:
                wins[pid] = 0

            wins[pid] += 1

    saveWins(wins)

def initWinsFile():
    if not os.path.exists(STATS_FILE):
        with open(STATS_FILE, "w") as f:
            json.dump({}, f)