import os
from roleUtils import findPlayerByRole, killPlayer

def votingPlayer(players):
    votedPlayer = -1
    errorMessage = ''
    while(votedPlayer == -1):
        votedInput = input( "Who is being voted for trial?" + errorMessage + "\n").lower()
        for x in range(0, len(players)):
            if players[x].name.lower() == votedInput and players[x].alive == True:
                votedPlayer = x
            else: 
                errorMessage = " (Invalid name, try again)"
                os.system('cls||clear')
    os.system('cls||clear')
    print(players[votedPlayer].name + ' has been voted to trial!\n' + players[votedPlayer].name + ', please argue your defence')
    return votedPlayer

def votingRound(players, votedPlayer):
    input('Press Enter when everybody is ready to begin voting')
    for x in range(0, len(players)):
        if players[x].alive == True and votedPlayer != x:
            os.system('cls||clear')
            players = mayorReveal(players)
            input("Hand the game over to player " + players[x].name + "\nPress Enter when you are ready, " + players[x].name + " \n")
            validInput = False
            errorMessage = ''
            while(validInput == False):
                os.system('cls||clear')
                voteInput = input("Player " + players[x].name + ":\nYou are voting whether or not " + players[votedPlayer].name + " is Guilty or Innocent \n Enter below: 'g', 'i', or 'a' to abstain" + errorMessage + "\n")
                voteInput = voteInput.lower()
                if voteInput == 'g' or voteInput == 'i' or voteInput == 'a':
                    validInput = True
                    players[x].vote = voteInput
                else:
                    errorMessage = " (Invalid name, try again)"
    os.system('cls||clear')
    return players

def mayorReveal(players):
    mayor = findPlayerByRole("Mayor", players)
    if mayor != -1:
        if players[mayor].revealed == False:
            validInput = False
            errorMessage = ''
            while(validInput == False):
                mayorInput = input("Would the mayor like to reveal himself? \nAnswer 'yes' or 'no'" + errorMessage + "\n")
                if mayorInput == 'yes' or mayorInput == 'no':
                    validInput = True
                    if mayorInput == 'yes':
                        print(players[mayor].name + " has revealed themselves as the Mayor!")
                        players[mayor].revealed = True
                else:
                    errorMessage = " (Invalid name, try again)"
    return players

def votingVerdict(players):
    guiltyVotes = 0
    innocentVotes = 0
    for x in players:  
        if  x.vote == 'g':
            print(x.name + " has voted Guilty")
            if x.role == 'Mayor' and x.revealed == True:
                guiltyVotes += 3
            else: guiltyVotes += 1
        if  x.vote == 'i':
            print(x.name + " has voted Innocent")
            if x.role == 'Mayor' and x.revealed == True:
                innocentVotes += 3
            else: innocentVotes += 1
        if  x.vote == 'a':
            print(x.name + " has abstained from voting")
    print("\n" + str(guiltyVotes) + " Guilty votes to " + str(innocentVotes) + " Innocent votes")
    if guiltyVotes > innocentVotes:
        return True
    return False

def updateOnLynching(players, votedPlayer):
    print("\nThe townsfolk have voted in favour of lynching " +  players[votedPlayer].name)
    killPlayer(players, votedPlayer, 'lynch')
    
    ##Jester
    if players[votedPlayer].role == "Jester":
            print('The Jester, ' + players[votedPlayer].name + ", will get his revenge from the grave!")
    return players