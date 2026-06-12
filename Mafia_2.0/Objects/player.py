from typing import Literal

Role = Literal[
    "Mafioso",
    "Framer",
    "Executioner",
    "Jester",
    "Serial Killer",
    "Mayor",
    "Doctor",
    "Escort",
    "Detective",
    "Veteran",
    "Medium"
]

class Player:
    def __init__(self, member):
        self.id = member.id
        self.member = member
        self.name = member.display_name
        self.number = 0

        self.role: Role | None = None
        self.alive = True

        # vote
        self.vote = None
        self.votedFor = None
        self.decision = None

        # action
        self.roundInput = None
        self.lastTarget = None

        # role specific
        self.executioner_target: int | None = None #Executioner target id
        self.revealed = False #Mayor revealed or not
        self.targetInfo = '' #Detective info
        self.alerts = 3 #Veteran bullets
        self.guiltyVoters = [] #Jester

    def reset_round(self):
        self.vote = None
        self.roundInput = None

