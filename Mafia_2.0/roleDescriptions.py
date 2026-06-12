import discord

from gamestate import GameState
from player import Player

leaveBlank = '\nType !action followed by the player number of your target (i.e. !action 1)'

def getRoleDescription(role):
    townsFolk = ' is a member of the Townsfolk, and wins the game by ridding the town of evil (any Serial Killer or Mafia member).\n'
    mafia = ' is a member of the Mafia, and wins the game if all the Townsfolk are killed.\n'
    if role == 'Doctor': return 'The Doctor' + townsFolk + 'The Doctor can select one Player to heal every night (including yourself). This will prevent that Player from dying if they are attacked.\nYou cannot heal the same person twice in a row, however.'
    if role == 'Framer': return 'The Framer' + mafia + 'The Framer can select one Player to frame every night. This will make the target appear suspicious if investigated by an Investigator.\n If the Mafioso dies, YOU will replace them and become the next Mafioso.'
    if role == 'Mafioso': return 'The Mafioso' + mafia + 'The Mafioso can select one Player to murder every night.\n'
    if role == 'Escort': return 'The Escort' + townsFolk + 'The Escort can select one Player to escort every night, preventing that Player from being able to perform their role.\nYou cannot escort the same person twice in a row, however.'
    if role == 'Detective': return 'The Detective' + townsFolk + 'The Detective can select one Player to investigate every night, and will receive the results of the investigation the next night.\nThe Detective searches for blood, which will appear on the Mafioso, Doctor, or anybody that was framed or murdered.'
    if role == 'Medium': return 'The Medium' + townsFolk + 'The Medium can speak to the dead at night'
    if role == 'Towny': return 'The Towny' + townsFolk + 'They do not have any special roles.'
    if role == 'Jailor': return 'The Jailor' + townsFolk
    if role == 'Executioner': return 'The Executioner wins the game by getting their target lynched. If their target is killed by another means, the Executioner will become a Jester.'
    if role == 'Jester': return 'The Jester wins the game by getting lynched, simple as that. After being lynched, you may choose to seek revenge on one player that condemned you at night.'
    if role == 'Mayor': return 'The Mayor' + townsFolk + 'The Mayor can reveal his role to the group before a round of voting begins. His vote will be worth 3 points from then on.'
    if role == 'Serial Killer': return 'The Serial Killer wins the game by being the last person alive. They can achieve this by killing. And lots of it!'
    if role == 'Veteran': return 'The Veteran' + townsFolk + "The Veteran can be on alert at night three times. You will kill any visitors on those nights"
    if role == 'GodFather': return 'The GodFather' + mafia + "The GodFather takes over the the murdering if the Mafioso dies."
    return 'oops no role Description, program brokey'
        
def getActionDescription(game: GameState, player: Player):
    role = player.role
    if role == 'Doctor': return 'Who would you like to heal?' + leaveBlank
    if role == 'Framer': return 'Who would you like to frame?' + leaveBlank
    if role == 'Mafioso': return 'Who would you like to murder?' + leaveBlank
    if role == 'Escort': return 'Who would you like to escort?' + leaveBlank
    if role == 'Detective':  return 'Who would you like to investigate?' + leaveBlank
    if role == 'Jailor': return 'Who would you like to jail?' + leaveBlank
    if role == 'Serial Killer': return 'Who would you like to kill?' + leaveBlank
    if role == 'Jester': 
        if player.alive == True: return 'The Jester has no night action yet'
        if len(player.guiltyVoters) == 0: 'The Jester can no longer seek revenge'
        targets = [f"{p.number}. {p.name}" for p in game.players.values() if p.id in player.guiltyVoters and p.alive]
        return ("Who would you like to seek revenge on?\n\n" "Possible targets:\n" + "\n".join(targets) + leaveBlank)
    
    if role == 'Veteran': 
        alerts = str(3 - player.alerts)
        message = 'You have used ' + alerts + ' alerts.'
        if player.alerts > 0:
            message+= "Type !action 1 if you would like to be on alert tonight"
        return message
    
    return 'This role does not have a night action'
 
async def sendNightInfo(guild, game):
    for player in game.players.values():
        channel_name = player.name.lower().replace(" ", "-")
        channel = discord.utils.get(guild.text_channels, name=channel_name)
        if channel is None: continue

        message = getActionDescription(game, player)
        await channel.send(message)