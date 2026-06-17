from gamestate import GameState
from utils import getByRole, isMafia, sendToPlayer
from player import Player


def getPossibleOptions(game: GameState, player: Player) -> list[Player]:
    if player is None: return []
    if game.is_day and player.role != 'Jailor': return []
    if player.role == 'Jester' and player.alive: return []
    if not player.alive and player.role != 'Jester': return []
    if player.role in ['Towny', 'Executioner', 'Mayor', 'Veteran', 'Survivor']: return []

    possible = []
    noSelfTarget = ['Mafioso', 'Framer', 'Serial Killer', 'Jester', 'Jailor']

    for target in game.players.values():
        if not target.alive: continue

        # Self-target restrictions
        if target.id == player.id and player.role in noSelfTarget: continue

        # Cannot target same person twice in a row
        if player.role in ['Doctor', 'Escort'] and player.lastTarget == target.id: continue

        # Mafia cannot target mafia
        if isMafia(player) and isMafia(target): continue

        # Jester can only target guilty voters
        if player.role == 'Jester':
            if len(player.guiltyVoters) == 0: continue
            if target.id not in player.guiltyVoters: continue

        # Doctor cannot heal revealed mayor
        if (player.role == 'Doctor' and target.role == 'Mayor' and target.revealed): continue

        possible.append(target)

    return possible