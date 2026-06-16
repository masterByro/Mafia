from typing import Literal


Role = Literal['Mafioso', 'Mafioso (Dead)', 'Framer', 'Janitor', 'Executioner', 'Jester', 'Serial Killer','Survivor', 'Mayor', 'Doctor', 'Escort', 'Detective', 'Veteran', 'Medium', 'Towny','Jailor']
mafiaRoles: list[Role] = ['Mafioso', 'Mafioso (Dead)', 'Framer', 'Janitor']
townRoles: list[Role] = ['Mayor', 'Doctor', 'Escort', 'Detective', 'Veteran', 'Medium', 'Towny', 'Jailor']
neutralEvil: list[Role] = ['Executioner', 'Jester']
neutralNeutral: list[Role] = ['Survivor']
neutralKiller: list[Role] = ['Serial Killer']
class Player:
    def __init__(self, member):
        self.id: int = member.id
        self.member = member
        self.name = member.display_name
        self.number = 0

        self.role: Role | None = None
        self.alive = True
        self.win = False
        self.originalRole: Role | None = None

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
        self.targetInfo: str|None = '' #Detective info
        self.alerts = 3 #Veteran bullets / Survivor vests
        self.onAlert = False
        self.guiltyVoters = [] #Jester
        self.willExecute = False #Jailor
        self.framed = False #Framer
        self.murderNote: str|None = None
        self.cleaned = False #Janitor

    def reset_round(self): #Don't reset framed
        self.lastTarget = self.roundInput
        self.roundInput = None
        self.vote = None
        self.votedFor = False
        self.decision = None
        self.targetInfo = None
        self.onAlert = False
        self.guiltyVoters = []
        self.willExecute = False
        self.cleaned = False