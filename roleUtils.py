import sys

def isValidInput(userInput, players, playerIndex):
    if userInput == '' : return True
    player = players[playerIndex]
    if player.role == 'Veteran':
        if userInput == 'landmine': return player.hasMine
        if player.hasBullet == False: return False
        
    for target in players:
        if target.name.lower() == userInput and target.alive == True:
            if target == player:
                if player.role == 'Escort': return False
                if player.role == 'Mafioso': return False
                if player.role == 'Jailor': return False
                if player.role == 'Framer': return False
                if player.role == 'Detective': return False
                if player.role == 'Serial Killer': return False
                if player.role == 'Veteran': return False
            if target.name == player.roundInput:
                if player.role == 'Escort': return False
                if player.role == 'Doctor': return False
            if player.role == 'Mafioso' or player.role == 'Framer':
                if target.role == 'Mafioso' or target.role == 'Framer': return False
            if player.role == 'Jester':
                if target.vote == 'g': return True
                else: return False
            return True
    return False

def getTarget(players, role):
    player = findPlayerByRoleObj(role, players)
    if player is not None:
        roundInput = player.roundInput
        if roundInput != '' and roundInput != 'landmine':
            target = findPlayerByName(roundInput, players)
            ##print(player.name + ' ' + player.role + " --> " + players[target].name + ' ' + players[target].role)
            return target
    return -1
            
def calculateResults(players):
    deaths = []
    ##Jailkeeper
    ##jailKeeperTarget = getTarget(players, "Jailkeeper")
    ##if jailKeeperTarget != -1:
        ##players[jailKeeperTarget].roundInput = ''
            ##add Jailkeeper stuff
    
    ##Jester 
    jester = findPlayerByRole("Jester", players) 
    if jester != -1:
        players[jester].revenge = False
    jesterTarget = getTarget(players, "Jester")
    if jesterTarget != -1:
        death = [jesterTarget, ' is dead! The Jester gets their revenge from the grave!']
        players[jesterTarget].roundInput = ''
        deaths.append(death)
        
    ##Veteran     
    veteran = findPlayerByRole("Veteran", players) 
    vetTarget = getTarget(players, "Veteran")
    if vetTarget != -1:
            death = [vetTarget, ' was shot in the chest last night!']
            players[veteran].hasBullet = False
            players[vetTarget].roundInput = ''
            deaths.append(death)
            
    ##Escort     
    escort = findPlayerByRole("Escort", players) 
    escortTarget = getTarget(players, "Escort")
    if escortTarget != -1:
        players, deaths, killed = visitVet(players, deaths, "Escort", escortTarget)
        if killed == False:
            players[escortTarget].roundInput = ''
            ##visit SK
            if players[escortTarget].role == "Serial Killer":
                death = [escort, ' was horifically stabbed to death while out visiting last night!']
                deaths.append(death)
     
    ##Doctor Self Heal
    doctorImmune = False
    doctor = findPlayerByRole("Doctor", players)  
    doctorTarget = getTarget(players, "Doctor")
    if doctorTarget != -1 and doctorTarget == doctor:
        doctorImmune = True
                            
    ##Serial Killer    
    sKTarget = getTarget(players, "Serial Killer")
    if sKTarget != -1:
        players, deaths, killed = visitVet(players, deaths, "Serial Killer", sKTarget)
        if killed == False:  
            death = [sKTarget, ' was horifically stabbed to death last night!']
            players[sKTarget].roundInput = ''
            deaths.append(death)
    
    ##Mafioso
    mafiosoTarget = getTarget(players, "Mafioso")
    if mafiosoTarget != -1:
        players, deaths, killed = visitVet(players, deaths,  "Mafioso", mafiosoTarget)
        if killed == False:  
            death = [mafiosoTarget, ' was murdered last night!']
            players[mafiosoTarget].roundInput = ''
            deaths.append(death)

    ##Doctor      
    doctorTarget = getTarget(players, "Doctor")
    if doctorTarget != -1:
        players, deaths, killed = visitVet(players, deaths, "Doctor", doctorTarget)
        if killed == False:
            for death in deaths:
                if death[0] == doctorTarget:
                    deaths.remove(death)
                
    ##Framer      
    framerTarget = getTarget(players, "Framer")
    if framerTarget != -1:
        players, deaths, killed = visitVet(players, deaths, "Framer", doctorTarget)
        if killed == True:
            framerTarget = -1
        
    ##Detective
    detective = findPlayerByRole("Detective", players)
    detectiveTarget = getTarget(players, "Detective")
    if detectiveTarget != -1:
        players, deaths, killed = visitVet(players, deaths, "Detective", doctorTarget)
        if killed == False: 
            if players[detectiveTarget].role == "Doctor" or players[detectiveTarget].role == "Mafioso" or detectiveTarget == framerTarget or players[detectiveTarget].role == "Serial Killer" or detectiveTarget in deaths: 
                targetFeedback = ", had blood on them last night"
            else: targetFeedback =  ", did NOT have blood on them last night"
            players[detective].targetInfo =  "Your target, " +  players[detectiveTarget].name + targetFeedback
        elif detective != -1:
            players[detective].targetInfo = "You either did not select anyone to investigate last night, or were blocked" 
    
    if doctorImmune == True:
        deaths = [row for row in deaths if row[0] != doctor]
    ##Add Deaths
    for x in deaths:
        killPlayer(players, x[0], 'night')
        
    return players, deaths

def visitVet(players, deaths, playerRole, target):
    killed = False
    player = findPlayerByRole(playerRole, players) 
    if players[target].role == "Veteran" and players[target].roundInput == 'landmine':
        death = [player, ' was blown up last night!']
        players[target].hasMine = False
        deaths.append(death)
        killed = True
    return players, deaths, killed

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

def checkAlive(players):
    aliveRoles = []
    for player in players:
        if player.alive: aliveRoles.append(player.role)
    return aliveRoles
    
def checkForWin(players):
    ##If townys all dead, mafia all dead, executioner gets target (end of day)
    printMsg = ''
    evil = ['Mafioso', 'Framer', 'Serial Killer']
    aliveRoles = checkAlive(players)
    if "Serial Killer" in aliveRoles and len(aliveRoles) == 1: 
        print("The Serial Killer has won!")
        return True
    if "Mafioso" in aliveRoles and len(aliveRoles) == 1 or "Framer" in aliveRoles and len(aliveRoles) == 2: 
        print("The Mafia have defeated all the Townfolk!")
        return True
    if all(item not in aliveRoles for item in evil):
        print("Congratulations! The Townfolk have defeated all the threats to their town!")
        return True
    return False

def mafiaInfo(players):
    mafiaText = "MAFIA GANG:"
    mafioso = findPlayerByRoleObj("Mafioso", players)
    framer = findPlayerByRoleObj("Framer", players)
    exMafioso = findPlayerByRoleObj("Ex-Mafioso", players)
    if mafioso is not None: mafiaText += "\n Mafioso: " + mafioso.name
    if framer is not None: mafiaText += "\n Framer: " + framer.name
    if exMafioso is not None: mafiaText += "\n Ex-Mafioso: " + exMafioso.name
    return mafiaText

def upgradeFramer(players):
    mafioso = findPlayerByRole("Mafioso", players)
    if mafioso != -1:
        if players[mafioso].alive == False:
            framer = findPlayerByRole("Framer", players)
            if framer != -1 and players[framer].alive == True:
                players[mafioso].role = "Ex-Mafioso"
                players[framer].role = "Mafioso"
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
        