import os
from player import Player
from roleUtils import findPlayerByRoleObj
import random
##roles = ['Doctor','Framer', 'Mafioso', 'Escort', 'Detective', 'Medium', 'Towny', 'Executioner', 'Mayor', 'Serial Killer', 'Veteran', 'Jester']
    
makePlayers = []

def createPlayers():
    
    numOfPlayers = int(input("Enter number of players:\n"))
    roles = makeRoles(numOfPlayers)
    random.shuffle(roles)
    
    for x in range(0, numOfPlayers):
        p = Player()
        p.name = input("Enter name of player " + str(x+1) + ": \n")
        p.role = roles[x]
        makePlayers.append(p)
        os.system('cls||clear')
        
    getExecutionerTarget()
    return makePlayers     

def autoCreatePlayers():
    ##names = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h','i','j', 'k', 'l']
    ##roles = ['Veteran', 'Mafioso', 'Framer']
    
    names = ['byron', 'hayley', 'tristen', 'rhiannon', 'jordan', 'mary', 'james', 'gayan','gihara','jadelyn', 'prigg']

    
    numOfPlayers = len(names)
    roles = makeRoles(numOfPlayers)
    
    random.shuffle(roles)
    for x in range(0, numOfPlayers):
        p = Player()
        p.role = roles[x]
        p.name = str(names[x])
        ##print(p.name  + "  :  " + p.role)
        makePlayers.append(p)
        
    getExecutionerTarget()
    return makePlayers    

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

    return roles

def getExecutionerTarget():
    executioner = findPlayerByRoleObj("Executioner", makePlayers)
    if executioner is not None:
        townies = []
        for x in makePlayers:
            if x.alive == True and x.role != "Mafioso" and x.role != "Framer" and x.role != "Executioner" and x.role != "Serial Killer" and x.role != "Mayor":
                townies.append(x)
        if (len(townies) == 0):
            executioner.role = 'Jester'
        else:
            random.shuffle(townies)
            executioner.executionerTarget = townies[0].name