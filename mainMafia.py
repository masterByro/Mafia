import os
from playerCreation import autoCreatePlayers, createPlayers
from roleDescriptions import getActionDescription, getRoleDescription
from roleUtils import calculateResults, countAlivePlayers, gameOverText, isValidInput, mafiaInfo, checkForWin
from votingUtils import updateOnLynching, votingPlayer, votingRound, votingVerdict


def main():
    print("MAFIA")
    deadChat = 'DEAD CHAT: '
    
    ##players = createPlayers()
    players = autoCreatePlayers()
    
    global dayInt
    dayInt = 1
    deaths = []
    
    while(True):
        print("=== Day " + str(dayInt) + " ===")
        for x in deaths:
            print(players[x[0]].name + x[1])
        if len(deaths) == 0 and dayInt > 1: print("Nobody was murdered last night")
        if checkForWin(players):
            gameOverText(players)
            break
        
        input("Press Enter to begin the Day:")
        players = day(players)
        if checkForWin(players):
            gameOverText(players)
            break
        
        input("Press Enter to begin the Night:")
        os.system('cls||clear')
        players, deadChat = night(players, deadChat)
        players, deaths = calculateResults(players)
        
        dayInt += 1
        
def day(players):
    errorText = ''
    failedVotes = 0 if countAlivePlayers(players) > 2 else 3
    while (failedVotes < 3):
        os.system('cls||clear')
        print("Day: " + str(dayInt))
        print("You may openly discuss with the group")
        print("You can also openly vote to place a Player on Trial for lynching. If over half the Players agree, type VOTE below")
        textInput = input("Otherwise, type SKIP to move to nightfall" + errorText + "\n")
        textInput = textInput.lower()
        if textInput == 'skip': return players
        if textInput == 'vote':
            votedPlayer = votingPlayer(players)
            players = votingRound(players, votedPlayer)
            if votingVerdict(players):
                players = updateOnLynching(players, votedPlayer)
                return players
            else:
                input("\nThe townsfolk have voted against lynching " +  players[votedPlayer].name + "\nPress Enter to continue\n")
                failedVotes = failedVotes + 1
                errorText = ''
        else: 
            errorText = ' (Invalid input, try again)'
    if failedVotes >= 3: print("Lynching is no longer an option. Night is now falling.")
    return players
              
def night(players, deadChat):
    for x in range(0, len(players)):
        print("Night: " + str(dayInt))
        input("Hand the game over to player " + players[x].name + "\nPress Enter when you are ready, " + players[x].name + " \n")
        valdiatedInput = False
        errorMessage = ''
        
        while(valdiatedInput == False):
            os.system('cls||clear')
            print("Night: " + str(dayInt) + "\nPlayer: " + players[x].name + "\nRole: " + players[x].role)
                  ##+ "\nDescription: " + getRoleDescription(players[x].role))
            
            if players[x].role == "Medium" or players[x].alive == False and players[x].revenge != True:
                if players[x].alive == False:
                    print("You are dead, but you can still talk to the Medium or other dead people")
                print(deadChat)
                textInput = input("\nType message in dead chat, or press Enter to end your turn\n")
                if textInput != '': deadChat = deadChat + "\n[" + players[x].name + "] - " + textInput
                valdiatedInput = True
                
            elif players[x].role == "Towny" or  players[x].role == "Mayor" or players[x].role == "Executioner" or (players[x].role == "Jester" and players[x].revenge == False):
                if  players[x].role == "Executioner":
                    if  players[x].executionerWin == False: print("Your target to get lynched is " + players[x].executionerTarget)
                    else: print("You have won the game! Feel free to help whichever side you'd like")
                input("\nType anything below and Enter (typing stuff helps hide your role from others): \n")
                valdiatedInput = True
                
            else:
                if players[x].role == "Mafioso" or  players[x].role == "Framer":
                    print(mafiaInfo(players))
                if  players[x].role == "Detective" and players[x].targetInfo != '':
                    print(players[x].targetInfo)
                textInput = input("\n" + getActionDescription(players[x].role, players[x]) + errorMessage + "\n").lower()
                if isValidInput(textInput, players, x):
                    valdiatedInput = True   
                    players[x].roundInput = textInput
                    players[x].targetInfo = ''
                else:
                    errorMessage = " (Invalid name, try again)"
        os.system('cls||clear')
    os.system('cls||clear')
    return players, deadChat



if __name__ == "__main__":
    main()