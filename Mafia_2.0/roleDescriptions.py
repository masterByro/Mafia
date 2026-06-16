from gamestate import GameState
from player import Player, Role
from utils import getByRole
from UI.AlertButton import AlertView

leaveBlank = '\nType `!target <player Id>` to target a player.'
townsFolk = ' is a member of the Townsfolk.\n'
mafia = ' is a member of the Mafia.\n'

def getRoleDescription(role: Role|None):
    if role == 'Doctor': return 'The Doctor' + townsFolk + 'The Doctor can select one Player to heal each night (including yourself). This will prevent that Player from dying if they are attacked.\nYou cannot heal the same person twice in a row, however.'
    if role == 'Mafioso': return 'The Mafioso' + mafia + 'The Mafioso can select one Player to murder each night.\n'
    if role == 'Framer': return 'The Framer' + mafia + 'The Framer can select one Player to frame each night. This will make the target appear suspicious if investigated by an Investigator.\n If the Mafioso dies, you will replace them and become the next Mafioso.'
    if role == 'Janitor': return 'The Janitor' + mafia + 'The Janitor can select one Player to clean on three night. If that player dies, only you can see their role and will.\n If the Mafioso dies, you will replace them and become the next Mafioso.'
    if role == 'Escort': return 'The Escort' + townsFolk + 'The Escort can select one Player to escort each night, preventing that Player from being able to perform their role.\nYou cannot escort the same person twice in a row, however.'
    if role == 'Detective': return 'The Detective' + townsFolk + 'The Detective can select one Player to investigate each night, and will receive the results of the investigation the next night.\nThe Detective searches for blood, which will appear on the Mafioso, Doctor, or anybody that was framed or murdered.'
    if role == 'Medium': return 'The Medium' + townsFolk + 'The Medium can speak to the dead at night'
    if role == 'Towny': return 'The Towny' + townsFolk + 'They do not have any special roles.'
    if role == 'Jailor': return 'The Jailor' + townsFolk + "During the day, you can select someone to jail with command `!target <player Id>`.\n That night, you can interrogate them and execute them with the command `!kill`. Type the command again to cancel the execution"
    if role == 'Executioner': return 'The Executioner wins the game by getting their target lynched. If their target is killed by another means, the Executioner will become a Jester.'
    if role == 'Jester': return 'The Jester wins the game by getting lynched, simple as that. After being lynched, you may choose to seek revenge on one player that condemned you at night.'
    if role == 'Mayor': return 'The Mayor' + townsFolk + 'The Mayor can reveal his role to the group during the day. His vote will be worth 3 points from then on.'
    if role == 'Serial Killer': return 'The Serial Killer wins the game by being the last person alive. They can achieve this by killing. And lots of it!'
    if role == 'Survivor': return 'The Survivor wins by staying alive until the very end. You can be on alert 3 night,'
    if role == 'Veteran': return 'The Veteran' + townsFolk + "The Veteran can be on alert for three nights. You will kill any visitors on those nights."
    return 'oops no role Description, program brokey'
        
def getActionDescription(game: GameState, player: Player):
    role = player.role
    if role == 'Doctor': return 'Who would you like to heal?' + leaveBlank
    if role == 'Mafioso': return 'Who would you like to murder?' + leaveBlank
    if role == 'Framer': return 'Who would you like to frame?' + leaveBlank
    if role == 'Janitor': return 'Who would you like to clean?' + leaveBlank
    if role == 'Escort': return 'Who would you like to escort?' + leaveBlank
    if role == 'Detective':  return 'Who would you like to investigate?' + leaveBlank
    if role == 'Serial Killer': return 'Who would you like to kill?' + leaveBlank
    if role == 'Jester': 
        if player.alive == True: return 'The Jester has no night action yet'
        if len(player.guiltyVoters) == 0: 'The Jester can no longer seek revenge'
        targets = [f"{p.number}. {p.name}" for p in game.players.values() if p.id in player.guiltyVoters and p.alive]
        return ("Who would you like to seek revenge on?\n\n" "Possible targets:\n" + "\n".join(targets) + leaveBlank)
    if role in  ['Veteran', 'Survivor']: 
        return 'You have ' + str(player.alerts) + ' alerts remaining.'
 
async def sendNightInfo(guild, game):
    jailor = getByRole(game.players, 'Jailor')
    jail_prisoner = None
    if jailor and jailor.roundInput is not None: jail_prisoner = game.players.get(jailor.roundInput)

    for player in game.players.values():
        channel = guild.get_channel(game.player_channels.get(player.id))
        if not channel: continue
        if jailor and jail_prisoner:

            if player.id == jailor.id:
                await channel.send(f"⛓️ You have jailed **{jail_prisoner.name}** tonight.\n" f"Use `!say <message>` to interrogate them.\n" f"Use `!kill` if you wish to execute them.")
                continue

            if player.id == jail_prisoner.id:
                await channel.send("⛓️ You have been jailed tonight.\n" f"Use `!say <message>` to respond to the Jailor")
                continue


        message = getActionDescription(game, player)
        if message: await channel.send(message)
        
        if player.role in ["Veteran", "Survivor"]:
            await channel.send(view=AlertView(game))