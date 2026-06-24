import discord

from gamestate import GameState
from player import Player, Role
from utils import getByRole
from roleActions import getPossibleOptions

from UI.MayorReveal import MayorRevealView
from UI.TargetDropdowns import TargetView
from UI.AlertButton import AlertView
from UI.JailorButton import ExecuteView
from UI.JailSpeak import JailSpeakView

townsFolk = ' is a member of the Townsfolk.\n'
Uprising = ' is a member of the Uprising.\n'

def getRoleDescription(role: Role|None):
    if role == 'Healer': return 'The Healer' + townsFolk + 'The Healer can select one Player to heal each night (including yourself), saving them from mortal wounds.\nYou cannot heal the same person twice in a row, however.'
    if role == 'Insurgent': return 'The Insurgent' + Uprising + 'The Insurgent can select one Player to murder each night.\n'
    if role == 'Propagandist': return 'The Propagandist' + Uprising + 'The Propagandist can select one Player to frame each night. This will make the target appear suspicious if investigated by an Investigator.\n If the Insurgent dies, you will replace them and become the next Insurgent.'
    if role == 'Warden': return 'The Warden' + Uprising + 'The Warden can select one Player to clean on three night. If that player dies, only you can see their role and will.\n If the Insurgent dies, you will replace them and become the next Insurgent.'
    if role == 'Escort': return 'The Escort' + townsFolk + 'The Escort can select one Player to escort each night, preventing that Player from being able to perform their role.\nYou cannot escort the same person twice in a row, however.'
    if role == 'Inquisitor': return 'The Inquisitor' + townsFolk + 'The Inquisitor can select one Player to investigate each night, and will receive the results of the investigation the next night.\nThe Inquisitor searches for blood, which will appear on the Insurgent, Healer, or anybody that was framed or murdered.'
    if role == 'Medium': return 'The Medium' + townsFolk + 'The Medium can speak to the dead at night'
    if role == 'Peasant': return 'The Peasant' + townsFolk + 'They do not have any special roles.'
    if role == 'Jailor': return 'The Jailor' + townsFolk + "During the day, you can select someone to jail.\n That night, you can interrogate them and choose to execute them."
    if role == 'Executioner': return 'The Executioner wins the game by getting their target lynched. If their target is killed by another means, the Executioner will become a Jester.'
    if role == 'Jester': return 'The Jester wins the game by getting lynched, simple as that. After being lynched, you may choose to seek revenge on one player that condemned you at night.'
    if role == 'Chancellor': return 'The Chancellor' + townsFolk + 'The Chancellor can reveal his role to the group during the day. His vote will be worth 3 points from then on.'
    if role == 'Serial Killer': return 'The Serial Killer wins the game by being the last person alive. They can achieve this by killing. And lots of it!'
    if role == 'Wanderer': return 'The Wanderer wins by staying alive until the very end. You can be on alert 3 night,'
    if role == 'Knight': return 'The Knight' + townsFolk + "The Knight can be on alert for three nights. You will kill any visitors on those nights."
    if role == 'Watchman': return 'The Watchman' + townsFolk + "The Watchman can select a player's house each night to watch over, keeping track of who visits it."
    return 'oops no role Description, program brokey'
        
def getActionDescription(game: GameState, player: Player):
    role = player.role
    if role == 'Healer': return 'Who would you like to heal?'
    if role == 'Insurgent': return 'Who would you like to murder?'
    if role == 'Propagandist': return 'Who would you like to frame?'
    if role == 'Warden': return 'Who would you like to clean?'
    if role == 'Escort': return 'Who would you like to escort?'
    if role == 'Inquisitor':  return 'Who would you like to investigate?'
    if role == 'Serial Killer': return 'Who would you like to kill?'
    if role == 'Watchman': return "Who's house would you like to watch?"
    if role == 'Jester' and len(player.guiltyVoters) > 0 and not player.alive:  return 'Who would you like to seek revenge on?'
    if role in  ['Knight', 'Wanderer']:  return 'You have ' + str(player.alerts) + ' alerts remaining.'
 
async def sendNightInfo(guild, game):
    jailor = getByRole(game.players, 'Jailor')
    jail_prisoner = None
    if jailor and jailor.roundInput is not None: jail_prisoner = game.players.get(jailor.roundInput)

    for player in game.players.values():
        channel = guild.get_channel(game.player_channels.get(player.id))
        if not channel: continue
        if jailor and jail_prisoner:

            if player.id == jailor.id:
                await channel.send(f"⛓️ You have jailed **{jail_prisoner.name}** tonight",view=JailSpeakView(game, is_jailor=(player.role == "Jailor")))
                await channel.send(view=ExecuteView(game))
                continue

            if player.id == jail_prisoner.id:
                await channel.send("⛓️ You have been jailed tonight.",view=JailSpeakView(game, is_jailor=(player.role == "Jailor")))
                continue


        message = getActionDescription(game, player)
        if message: await channel.send(message)
        canTargetPlayers: list[Role] = ['Insurgent', 'Propagandist', 'Warden', 'Jester', 'Serial Killer', 'Healer', 'Escort', 'Inquisitor', 'Watchman']

        if player.role in canTargetPlayers:
            possibleOptions = getPossibleOptions(game, player)
            if len(possibleOptions) > 0: await channel.send(view=TargetView(game, possibleOptions))
        if player.role in ["Knight", "Wanderer"]:
            await channel.send(view=AlertView(game))


async def sendDayActions(guild, game: GameState):
    players = game.players

    for player in players.values():
        channel_name = player.name.lower().replace(" ", "-")
        channel = discord.utils.get(guild.text_channels, name=channel_name)
        if channel is None: continue

        if player.role == 'Chancellor' and not player.revealed and player.alive:
            await channel.send("🟢 Chancellor Action Available:", view=MayorRevealView(game))

        if player.role == 'Jailor' and player.alive:
            possibleOptions = getPossibleOptions(game, player)
            if len(possibleOptions) > 0: await channel.send("You can choose someone to jail tonight:", view=TargetView(game, possibleOptions))
