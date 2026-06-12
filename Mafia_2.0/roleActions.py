from gamestate import GameState
from utils import isMafia

async def setTarget(game: GameState, ctx, number: int):
    if game.is_day: return "Actions may only be performed at night.", False

    player = game.players.get(ctx.author.id)
    if player is None: return "You are not part of the game.", False

    if player.role == "Jester" and player.alive: return "Jester can only seek revenge once lynched", False
    if not player.alive and not player.role == "Jester": return "Dead players cannot perform actions.", False

    # Roles that dont have a target action
    if player.role in ["Towny", "Executioner", "Mayor", "Veteran"]:
        return f"The {player.role} cannot use this command.", False

    # Find target by player number
    target = next((p for p in game.players.values() if p.number == number),None)

    if target is None: return "Invalid player number.", False

    if not target.alive: return f"{target.name} is dead. You cannot perform actions on them.", False

    # Self-target restrictions
    if target.id == player.id:
        if player.role in [
            "Escort",
            "Mafioso",
            "Framer",
            "Detective",
            "Serial Killer",
            "Veteran",
            "Jester"
        ]:
            return f"The {player.role} cannot target themselves.", False

    # Cannot target same person twice in a row
    if player.role in ["Doctor", "Escort"] and player.lastTarget == target.id:
        return (f"The {player.role} cannot target the same player two nights in a row.",False,)

    # Mafia cannot target mafia
    if isMafia(player) and isMafia(target):
        return "You cannot target a fellow Mafia member.", False

    #Jester can only kill guilty voters the night after lynch
    if player.role == "Jester":
        if len(player.guiltyVoters) == 0: return "You can no longer seek revenge", False
        if target.id not in player.guiltyVoters: return "You can only target players who voted guilty against you", False

    # Success
    player.roundInput = target.id

    return (f"You will target {target.name} tonight.", True)

async def revealMayor(game: GameState, ctx):
    player = game.players.get(ctx.author.id)
    if player is None: return "You are not part of the game."
    if not player.role == 'Mayor': return "Nice Try bozo"
    if player.revealed: return "You have already revealed your role"
    if not player.alive: return "You are dead. Too late mate. So sad"
    if not game.is_day: return "You can only reveal your role during the day"
    
    player.revealed = True
    channel = ctx.guild.get_channel(game.town_channel_id)
    await channel.send((f"{player.name} has revealed themselves as the Mayor!"))
    return "You sucessfully reveal yourself"

async def alertVeteran(game: GameState, ctx):
    player = game.players.get(ctx.author.id)
    if player is None: return "You are not part of the game."
    if not player.role == 'Veteran': return "Nice Try bozo"
    if player.alerts == 0: return "You have already revealed your rolebeen on alert 3 times"
    if not player.alive: return "You are dead. Too late mate. So sad"
    if game.is_day: return "You can only go on alert at night"
    
    player.alerts -= 1
    player.onAlert = True
    return "You are now on alert"