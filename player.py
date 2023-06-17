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
        
        self.revenge = False ##Jester
        
        self.hasMine = True
        self.hasBullet = True
        
    def reset(self):
        self.roundInput = ''
        self.targetInfo = ''