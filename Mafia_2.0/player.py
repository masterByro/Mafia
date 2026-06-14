from typing import Literal

Role = Literal['Mafioso', 'Framer', 'Executioner', 'Jester', 'Serial Killer', 'Mayor', 'Doctor', 'Escort', 'Detective', 'Veteran', 'Medium', 'Towny','Jailor']
class Player:
    def __init__(self, member):
        self.id: int = member.id
        self.member = member
        self.name = member.display_name
        self.number = 0

        self.role: Role | None = None
        self.alive = True
        self.win = False

        # vote
        self.vote: int|None = None
        self.votedFor = False
        self.decision = None

        # action
        self.roundInput: int|None = None
        self.lastTarget: int|None = None

        # role specific
        self.executioner_target: int | None = None #Executioner target id
        self.revealed = False #Mayor revealed or not
        self.targetInfo = '' #Detective info
        self.alerts = 3 #Veteran bullets
        self.onAlert = False
        self.guiltyVoters = [] #Jester
        self.willExecute = False

    def reset_round(self):
        self.vote = None
        self.roundInput = None

