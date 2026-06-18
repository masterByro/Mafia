import random
from typing import List
import discord

from gamestate import GameState
from roleDescriptions import getRoleDescription
from player import Player, Role
from utils import getByRole, isMafia

ALLOW_BYRO_AS_PLAYER = True

def setup_players(guild, game: GameState, BYRO_ID):
    for member in guild.members:
        if member.bot: continue
        if not ALLOW_BYRO_AS_PLAYER and member.id == 710078079049007155: continue
        game.players[member.id] = Player(member)
        
    roles = makeRoles(len(game.players))
    for player, role in zip(game.players.values(), roles):
        player.role = role
        player.originalRole = role
    
    #Add integer
    ordered_players = sorted(game.players.values(), key=lambda p: p.name.lower())
    for i, player in enumerate(ordered_players, start=1):
        player.number = i
    
    getExecutionerTarget(game.players)

ALL_ROLES: List[Role] = ['Insurgent', 'Propagandist', 'Warden', 'Executioner', 'Jester', 'Serial Killer','Wanderer', 'Chancellor', 'Healer', 'Escort', 'Inquisitor', 'Knight', 'Medium', 'Jailor', 'Peasant', 'Peasant', 'Peasant']

def generate_roles(num_players: int):
    while True:
        pool = ALL_ROLES.copy()

        # If you want guaranteed Peasants as filler:
        while len(pool) < num_players:
            pool.append("Peasant")

        random.shuffle(pool)
        roles = pool[:num_players]

        if validate_roles(roles, num_players):
            return roles

def validate_roles(roles: list[Role], playerNum) -> bool:
    townBasic = ['Healer','Escort', 'Medium', 'Peasant']
    townExtra = ['Chancellor', 'Knight', 'Jailor', 'Inquisitor']
    Uprising = ['Insurgent', 'Propagandist', 'Warden']
    chaos = ['Executioner', 'Jester', 'Wanderer']
    chaosWithSK = ['Executioner', 'Jester','Serial Killer', 'Wanderer']

    if 'Insurgent' not in roles: return False
    if 'Propagandist' in roles and 'Inquisitor' not in roles: return False
    if 'Executioner' in roles and  'Jester' in roles: return False
    if playerNum > 6 and not ( 'Propagandist' in roles or 'Warden' in roles): return False
    return True

def makeRoles(playerNum: int) -> list[Role]:
    #15 roles
    #return  ['Healer', 'Jailor','Serial Killer', 'Chancellor']

    while True: 
        pool = ALL_ROLES.copy()

        random.shuffle(pool)
        roles = pool[:playerNum]

        if validate_roles(roles, playerNum):
            return roles
        

def getExecutionerTarget(players: dict[int, Player]):
    executioner = getByRole(players, 'Executioner')
 
    if executioner is None: return
    possibleTargets = ['Healer','Escort', 'Medium', 'Peasant', 'Knight']
    valid_targets = [p for p in players.values() if p.role in possibleTargets]
    #Fails here if no townmember. Shouldnt happen, so not fixing. Fix would be to flip to Jester
    target = random.choice(valid_targets)

    executioner.executioner_target = target.id
    
async def sendStarterInfo(guild, game: GameState):
    players = game.players

    #Uprising blob
    mafia_members = []
    mafia_members = [p for p in players.values() if isMafia(p)]
    mafia_teammate_text = ""
    if mafia_members:
        mafia_teammate_text = "**Uprising Team:**\n" + "\n".join(f"{m.name} : {m.role}" for m in mafia_members) + "\n\n"

# send messages
    for player in players.values():
        channel_name = player.name.lower().replace(" ", "-")
        channel = discord.utils.get(guild.text_channels, name=channel_name)
        if channel is None: continue

        message = f"**Your role is {player.role}**\n\n"
        message += getRoleDescription(player.role)
        message += "\n\n"

        # Uprising teammates
        if isMafia(player): message += mafia_teammate_text

        # Executioner target
        if player.role == 'Executioner' and player.executioner_target is not None:
                target = players.get(player.executioner_target)
                if target: message += f"**Your target is:** {target.name}\n\n"
                
        await channel.send(message)