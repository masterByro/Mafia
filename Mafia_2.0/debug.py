import json
import os
from datetime import datetime
from gamestate import GameState
from player import Role

DEBUG_FILE = "debugInfo.json"

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

def save_night_debug_start(game: GameState):
    """Save game state at beginning of calculateResults."""
    from utils import get_target
    
    debug_data = {
        "timestamp": datetime.now().isoformat(),
        "day_number": game.day_number,
        "is_day": game.is_day,
        "players_at_start": {},
        "actions": {}
    }
    
    # Capture all players and their targeting info
    for player_id, player in game.players.items():
        debug_data["players_at_start"][str(player_id)] = {
            "name": player.name,
            "role": player.role,
            "alive": player.alive,
            "roundInput": player.roundInput
        }
    
    # Capture who is targeting who for each role
    targeting_roles: list[Role] = ['Jester', 'Jailor', 'Knight', 'Healer', 'Escort', 'Insurgent', 'Serial Killer', 'Propagandist', 'Inquisitor', 'Warden', 'Wanderer', 'Watchman', 'Executioner']
    
    for role in targeting_roles:
        actor, target = get_target(game, role)
        
        # Special handling for roles with specific fields
        if role == 'Knight' or role == 'Wanderer':
            # Knight/Wanderer use onAlert instead of targeting
            for player in game.players.values():
                if player.alive and player.role == role:
                    debug_data["actions"][role] = {
                        "actor": player.name,
                        "actor_id": player.id,
                        "on_alert": player.onAlert
                    }
                    break
        elif role == 'Executioner':
            # Executioner target is set at game start
            for player in game.players.values():
                if player.role == 'Executioner':
                    target_player = game.players.get(player.executioner_target) if player.executioner_target else None
                    debug_data["actions"][role] = {
                        "actor": player.name,
                        "actor_id": player.id,
                        "target": target_player.name if target_player else None,
                        "target_id": target_player.id if target_player else None
                    }
                    break
        elif actor:
            debug_data["actions"][role] = {
                "actor": actor.name,
                "actor_id": actor.id,
                "target": target.name if target else None,
                "target_id": target.id if target else None
            }
            # Add role-specific info
            if role == 'Jailor' and actor.willExecute:
                debug_data["actions"][role]["will_execute"] = True
            elif role == 'Inquisitor' and actor.targetInfo:
                debug_data["actions"][role]["result"] = actor.targetInfo
            elif role == 'Warden' and actor.cleaned:
                debug_data["actions"][role]["cleaned"] = True
            elif role == 'Propagandist' and actor.framed:
                debug_data["actions"][role]["framed"] = True
            elif role == 'Watchman' and actor.visits:
                debug_data["actions"][role]["visits"] = actor.visits
            elif role == 'Jester' and actor.guiltyVoters:
                debug_data["actions"][role]["guilty_voters"] = [str(v) for v in actor.guiltyVoters]
    
    # Save to file
    _save_debug_file(debug_data)
    return debug_data

def save_night_debug_end(game: GameState, deaths, blocked, healed, attacked):
    """Save night results at end of calculateResults."""
    debug_data = _load_debug_file()
    
    debug_data["results"] = {
        "deaths": [[str(victim_id), msg, note] for victim_id, msg, note in deaths],
        "blocked": [str(player_id) for player_id in blocked],
        "healed": [str(player_id) for player_id in healed],
        "attacked": [[str(victim_id), msg, note] for victim_id, msg, note in attacked],
        "watchman_visits": {}
    }
    
    # Add watchman visits if available
    watchman = None
    for player in game.players.values():
        if player.role == 'Watchman' and player.alive:
            watchman = player
            break
    
    if watchman and watchman.visits:
        debug_data["results"]["watchman_visits"][watchman.name] = watchman.visits
    
    _save_debug_file(debug_data)

def _load_debug_file():
    """Load existing debug file or return empty template."""
    if os.path.exists(DEBUG_FILE):
        with open(DEBUG_FILE, "r") as f:
            return json.load(f)
    return {}

def _save_debug_file(data):
    """Save debug data to JSON file."""
    with open(DEBUG_FILE, "w") as f:
        json.dump(data, f, indent=4)

def clear_debug():
    """Clear the debug file when game ends."""
    if os.path.exists(DEBUG_FILE):
        os.remove(DEBUG_FILE)