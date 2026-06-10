class Player:
    def __init__(self, member):
        self.id = member.id
        self.member = member
        self.name = member.display_name

        self.role = None
        self.alive = True

        # per-round
        self.vote = None
        self.round_action = None

        # special roles
        self.executioner_target = None
        self.revealed = False

        # utility items
        self.has_mine = True
        self.has_bullet = True

    def reset_round(self):
        self.vote = None
        self.round_action = None