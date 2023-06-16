import os
from player import Player
from roleUtils import findPlayerByRoleObj
import random

makePlayers = []

def createPlayers(): 
    numOfPlayers = int(input("Enter number of players:\n"))
    roles = ['Mafioso','Escort', 'Medium', 'Doctor', 'Executioner', 'Detective']
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
    numOfPlayers = 6
    names = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h','i','j', 'k', 'l']
    ##roles = ['Doctor','Framer', 'Mafioso', 'Escort', 'Detective', 'Medium', 'Towny', 'Executioner', 'Mayor', 'Serial Killer', 'Veteran']
    roles = ['Veteran','Escort', 'Mafioso', 'Mayor', 'Serial Killer', 'Towny']
    
    for x in range(0, numOfPlayers):
        p = Player()
        p.role = roles[x]
        p.name = str(names[x])
        print(p.name  + "  :  " + p.role)
        makePlayers.append(p)
        
    getExecutionerTarget()
    return makePlayers    

def getExecutionerTarget():
    executioner = findPlayerByRoleObj("Executioner", makePlayers)
    if executioner is not None:
        townies = []
        for x in makePlayers:
            if x.alive == True and x.role != "Mafioso" and x.role != "Framer" and x.role != "Executioner" and x.role != "Serial Killer":
                townies.append(x)
            if (len(townies) == 0):
                x.role = 'Jester'
        else:
            random.shuffle(townies)
            executioner.executionerTarget = townies[0].name