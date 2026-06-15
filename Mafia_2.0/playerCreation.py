import random
import discord

from gamestate import GameState
from roleDescriptions import getRoleDescription
from player import Player, Role
from utils import getByRole, isMafia

ALLOW_BYRO_AS_PLAYER = False

def setup_players(guild, game: GameState, BYRO_ID):
    for member in guild.members:
        if member.bot: continue
        if not ALLOW_BYRO_AS_PLAYER and member.id == BYRO_ID: continue
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

def makeRoles(numOfPlayers: int) -> list[Role]:
    ## 11: 2 mafia, 2 chaos, 2 extra, 5 basic
    ## 10: 2 mafia, 1 chaos, 2 extra, 5 basic
    ## 9: 2 mafia, 1 chaos, 1 extra, 5 basic
    ## 8: 2 mafia, 1 chaos or 1 extra, 5 basic
    ## 7: 2 mafia, 1 exec or 1 extra, 4 basic
    ## 6: 1 mafia, 1 exec or 1 extra, 4 basic
    ## 5: 1 mafia, 1 extra, 3 basic
    ## 4: 1 mafia, 3 basic
    townBasic = ['Doctor','Escort', 'Medium', 'Towny']
    townExtra = ['Mayor', 'Veteran', 'Jailor' 'Towny', 'Towny']
    mafia = ['Mafioso', 'Framer']
    chaos = ['Executioner', 'Jester']
    chaosWithSK = ['Executioner', 'Jester','Serial Killer']

    random.shuffle(chaos)
    random.shuffle(townExtra)
    random.shuffle(townBasic)
    random.shuffle(chaosWithSK)
    
    roles = ['Mafioso']
    if numOfPlayers >= 6: roles.append(chaos[0])
    if numOfPlayers >= 7: 
        roles.append('Framer')
        roles.append('Detective')
    if numOfPlayers >= 8: 
        roles.pop(1)
        roles.append(chaosWithSK[0])
    if numOfPlayers >= 9: roles.append(townExtra[1])
    if numOfPlayers >= 10: roles.append(townExtra[2])
    if numOfPlayers >= 11: 
        roles.pop(3)
        roles.append(chaos[0])
        roles.append('Serial Killer')
    
    i = 0
    while len(roles) < numOfPlayers:
        if i <= 4: 
            roles.append(townBasic[i])
            i += 1
        else: roles.append('Towny')

    random.shuffle(roles)
    return ['Detective' , 'Mafioso', 'Escort',  'Janitor']
    return roles

def getExecutionerTarget(players: dict[int, Player]):
    executioner = getByRole(players, 'Executioner')
 
    if executioner is None: return
    possibleTargets = ['Doctor','Escort', 'Medium', 'Towny', 'Veteran']
    valid_targets = [p for p in players.values() if p.role in possibleTargets]
    target = random.choice(valid_targets)

    executioner.executioner_target = target.id
    
async def sendStarterInfo(guild, players: dict[int, Player]):
    #Mafia blob
    mafia_members = []
    mafia_members = [p for p in players.values() if isMafia(p)]
    mafia_teammate_text = ""
    if mafia_members:
        mafia_teammate_text = "**Mafia Team:**\n" + "\n".join(f"{m.name} : {m.role}" for m in mafia_members) + "\n\n"

# send messages
    for player in players.values():
        channel_name = player.name.lower().replace(" ", "-")
        channel = discord.utils.get(guild.text_channels, name=channel_name)
        if channel is None: continue

        message = f"**Your role is {player.role}**\n\n"
        message += getRoleDescription(player.role)
        message += "\n\n"

        # Mafia teammates
        if isMafia(player): message += mafia_teammate_text

        # Executioner target
        if player.role == 'Executioner' and player.executioner_target is not None:
                target = players.get(player.executioner_target)
                if target: message += f"**Your target is:** {target.name}\n\n"
                
        await channel.send(message)