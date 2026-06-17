from typing import Literal


Role = Literal['Insurgent', 'Insurgent (Dead)', 'Propagandist', 'Warden', 'CLEANED', 'Executioner', 'Jester', 'Serial Killer','Wanderer', 'Chancellor', 'Healer', 'Escort', 'Inquisitor', 'Knight', 'Medium', 'Peasant','Jailor']
mafiaRoles: list[Role] = ['Insurgent', 'Insurgent (Dead)', 'Propagandist', 'Warden']
townRoles: list[Role] = ['Chancellor', 'Healer', 'Escort', 'Inquisitor', 'Knight', 'Medium', 'Peasant', 'Jailor']
neutralEvil: list[Role] = ['Executioner', 'Jester']
neutralNeutral: list[Role] = ['Wanderer']
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
        self.revealed = False #Chancellor revealed or not
        self.targetInfo: str|None = '' #Inquisitor info
        self.alerts = 3 #Knight bullets / Wanderer vests
        self.onAlert = False
        self.guiltyVoters = [] #Jester
        self.willExecute = False #Jailor
        self.framed = False #Propagandist
        self.murderNote: str|None = None
        self.cleaned = False #Warden

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