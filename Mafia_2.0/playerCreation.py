import random
from roleDescriptions import getRoleDescription
from player import Player
import discord
##roles = ['Doctor','Framer', 'Mafioso', 'Escort', 'Detective', 'Medium', 'Towny', 'Executioner', 'Mayor', 'Serial Killer', 'Veteran', 'Jester']
##names = ['byron', 'hayley', 'tristen', 'rhiannon', 'jordan', 'mary', 'james', 'gayan','gihara','jadelyn', 'prigg']

def setup_players(guild, game):
    for member in guild.members:
        if not member.bot:
            game.players[member.id] = Player(member)

    roles = makeRoles(len(game.players))
    for player, role in zip(game.players.values(), roles):
        player.role = role
    
    #Add integer
    ordered_players = sorted(
        game.players.values(),
        key=lambda p: p.name.lower()
    )
    for i, player in enumerate(ordered_players, start=1):
        player.number = i
    
    getExecutionerTarget(game.players)

def makeRoles(numOfPlayers):
    ## 11: 2 mafia, 2 chaos, 2 extra, 5 basic
    ## 10: 2 mafia, 1 chaos, 2 extra, 5 basic
    ## 9: 2 mafia, 1 chaos, 1 extra, 5 basic
    ## 8: 2 mafia, 1 chaos or 1 extra, 5 basic
    ## 7: 2 mafia, 1 exec or 1 extra, 4 basic
    ## 6: 1 mafia, 1 exec or 1 extra, 4 basic
    ## 5: 1 mafia, 1 extra, 3 basic
    ## 4: 1 mafia, 3 basic
    townBasic = ['Doctor','Escort', 'Medium', 'Towny']
    townExtra = ['Mayor', 'Veteran', 'Towny', 'Towny']
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
    return ['Mafioso', 'Escort', 'Medium']
    return roles

def getExecutionerTarget(players):
    # find executioner
    executioner = None
    for p in players.values():
        if p.role == "Executioner":
            executioner = p
            break

    if executioner is None:
        return

    # build valid targets
    valid_targets = [
        p for p in players.values()
        if p.alive
        and p.role not in [
            "Mafioso",
            "Framer",
            "Executioner",
            "Serial Killer",
            "Mayor"
        ]
    ]

    # no valid targets → convert to Jester
    if len(valid_targets) == 0:
        executioner.role = "Jester"
        executioner.executioner_target = None
        return

    target = random.choice(valid_targets)

    # store ID (IMPORTANT: not name)
    executioner.executioner_target = target
    
async def sendStarterInfo(guild, players):
    mafia_members = []
    print(players)

    # send messages
    for player in players.values():
        print('hmm')
        print(player.name)
        if player.role in ["Mafioso", "Framer"]:
            mafia_members.append(player)
        
        channel_name = player.name.lower().replace(" ", "-")
        channel = discord.utils.get(guild.text_channels, name=channel_name)

        if channel is None:
            continue

        message = f"**Your role is {player.role}**\n\n"
        message += getRoleDescription(player.role)
        message += "\n\n"

        # Mafia teammates
        if player.role in ["Mafioso", "Framer"]:
            teammates = [
                f"{m.name} : {m.role}"
                for m in mafia_members
            ]

            if teammates:
                message += "**Mafia Team:**\n"
                message += "\n".join(teammates)
                message += "\n\n"

        # Executioner target
        if player.role == "Executioner" and player.executioner_target is not None:
                message += f"**Your target is:** {player.executioner_target.name}\n\n"

        # Commands template
        message += (
            "**Commands**\n"
            "*(Work in progress)*\n\n"
            "!help - Show role information\n"
            "!role - Show your role\n"
            "!action <player> - Perform your night action\n"
            "!vote <player> - Vote during the day\n"
        )
        print(f"Sending starter info to {player.name} in channel {channel_name}")
        await channel.send(message)