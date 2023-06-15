class Player:
    def __init__(self):
        self.name = ''
        self.role = ''
        self.roundInput = ''
        self.alive = True
    
        self.targetInfo = '' ##info about previous round target
        
        self.vote = ''
        self.revealed = False ##Mayor
        
        self.executionerTarget = ''
        self.executionerWin = False
        
    def reset(self):
        self.roundInput = ''
        self.targetInfo = ''