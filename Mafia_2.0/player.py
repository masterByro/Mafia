class Player:
    def __init__(self, member):
        self.member = member
        self.id = member.id
        self.name = member.display_name
        self.role = ''
        self.roundInput = ''
        self.alive = True
    
        self.targetInfo = '' ##info about previous round target
        
        self.vote_target_id = None
        self.revealed = False ##Mayor
        
        self.executioner_target = None
        self.executionerWin = False
        
        self.revenge = False ##Jester
        
        self.hasMine = True
        self.hasBullet = True
        
    def reset(self):
        self.roundInput = ''
        self.targetInfo = ''

    def is_mafia(self):
        return self.role in ['Mafioso', 'Framer']
