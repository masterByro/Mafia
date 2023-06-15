import sys

def isValidInput(userInput, players, playerIndex):
    if userInput == '' : return True
    player = players[playerIndex]
    for target in players:
        if target.name.lower() == userInput and target.alive == True:
            if target == player:
                if player.role == 'Escort': return False
                if player.role == 'Murderer': return False
                if player.role == 'Jailor': return False
                if player.role == 'Framer': return False
                if player.role == 'Detective': return False
                if player.role == 'Serial Killer': return False
            if target.name == player.roundInput:
                if player.role == 'Escort': return False
                if player.role == 'Doctor': return False
            if player.role == 'Murderer' or player.role == 'Framer':
                if target.role == 'Murderer' or target.role == 'Framer': return False
            return True
    return False

def getTarget(players, role):
    player = findPlayerByRoleObj(role, players)
    if player is not None:
        roundInput = player.roundInput
        if roundInput != '':
            target = findPlayerByName(roundInput, players)
            print(player.name + ' ' + player.role + " --> " + players[target].name + ' ' + players[target].role)
            return target
    return -1
            
def calculateResults(players):
    deaths = []
    ##Jailkeeper
    jailKeeperTarget = getTarget(players, "Jailkeeper")
    if jailKeeperTarget != -1:
        players[jailKeeperTarget].roundInput = ''
            ##add Jailkeeper stuff
            
    ##Escort      
    escortTarget = getTarget(players, "Escort")
    if escortTarget != -1:
        players[escortTarget].roundInput = ''
    
    ##Serial Killer    
    sKTarget = getTarget(players, "Serial Killer")
    if sKTarget != -1:
        deaths.append(sKTarget)
    
    ##Murderer
    murdererTarget = getTarget(players, "Murderer")
    if murdererTarget != -1:
        deaths.append(murdererTarget)

    ##Doctor      
    doctorTarget = getTarget(players, "Doctor")
    if doctorTarget != -1:
        if doctorTarget in deaths:
            deaths.remove(doctorTarget)
                
    ##Framer      
    framerTarget = getTarget(players, "Framer")

    ##Detective
    detective = findPlayerByRole("Detective", players)
    detectiveTarget = getTarget(players, "Detective")
    if detectiveTarget != -1:
        if players[detectiveTarget].role == "Doctor" or players[detectiveTarget].role == "Murderer" or detectiveTarget == framerTarget or detectiveTarget in deaths: 
            targetFeedback = ", had blood on them last night"
        else: targetFeedback =  ", did NOT have blood on them last night"
        players[detective].targetInfo =  "Your target, " +  players[detectiveTarget].name + targetFeedback
    elif detective != -1:
        players[detective].targetInfo = "You either did not select anyone to investigate last night, or were blocked" 
    
    ##Add Deaths
    for x in deaths:
        killPlayer(players, x, 'night')
        
    return players, deaths
    
def findPlayerByRole(role, players):
    for x in range(0, len(players)):
        if players[x].role == role:
            return x
    return -1

def findPlayerByName(name, players):
    for x in range(0, len(players)):
        if players[x].name.lower() == name.lower():
            return x
    sys.exit()
    
def findPlayerByRoleObj(role, players):
    for player in players:
        if player.role == role:
            return player
    return None

def findPlayerByNameObj(name, players):
    for player in players:
        if player.name.lower() == name.lower():
            return player
    sys.exit()
    
def checkForWin(players):
    ##If townys all dead, mafia all dead, executioner gets target (end of day)
    murderer = findPlayerByRoleObj("Murderer", players)
    serialK = findPlayerByRoleObj("Serial Killer", players)
    if murderer is not None and murderer.alive == False and serialK is not None and serialK.alive == False:
        print("Congratulations! The Townfolk have defeated all the threats to their town!")
        return True
    townyAlive = False
    for x in players:
        if x.alive == True and x.role != "Murderer" and x.role != "Framer":
            townyAlive = True
    if townyAlive == False:
        print("The Mafia have defeated all the Townfolk!")
        return True
    anyAlive = False
    if serialK is not None and serialK.alive == True:
        for x in players:
            if x.alive == True and x.role != "Serial Killer":
                anyAlive = True
        if anyAlive == False:
            print("The Serial Killer has won!")
        return True
    return False

def mafiaInfo(players):
    mafiaText = "MAFIA GANG:"
    murderer = findPlayerByRoleObj("Murderer", players)
    framer = findPlayerByRoleObj("Framer", players)
    exMurderer = findPlayerByRoleObj("Ex-Murderer", players)
    if murderer is not None: mafiaText += "\n Murderer: " + murderer.name
    if framer is not None: mafiaText += "\n Framer: " + framer.name
    if exMurderer is not None: mafiaText += "\n Ex-Murderer: " + exMurderer.name
    return mafiaText

def upgradeFramer(players):
    murderer = findPlayerByRole("Murderer", players)
    if murderer != -1:
        if players[murderer].alive == False:
            framer = findPlayerByRole("Framer", players)
            if framer != -1 and players[framer].alive == True:
                players[murderer].role = "Ex-Murderer"
                players[framer].role = "Murderer"
    return players

def updateExecutioner(players, player, method):
    executioner = findPlayerByRole("Executioner", players)
    if executioner != -1:
        if players[executioner].executionerTarget == players[player].name:
            if method == 'lynch':
                players[executioner].executionerWin = True
                print('The Executioner has lynched their Target ' + players[player].name + " and won! The Game is not over yet though, the town is still plagued with evil...")
            else: 
                players[executioner].role = 'Jester'
    return players

def killPlayer(players, player, method):
    players[player].alive = False
    players[player].reset()
    players = upgradeFramer(players)
    players = updateExecutioner(players, player, method)

def countAlivePlayers(players):
    count = 0
    for player in players:
        if player.alive == True:
            count += 1
    return count

def gameOverText(players):
    print("Thanks for playing")
    for x in players:
        deadText = "Alive" if x.alive == True else "Dead"
        print(x.name + "  :  " + x.role + "  :  " + deadText)