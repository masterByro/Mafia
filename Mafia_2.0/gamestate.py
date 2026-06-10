class GameState:
    def __init__(self):
        self.running = False
        self.is_day = True
        self.day_number = 1
        self.can_vote = True
        self.canDecide = False

        self.town_channel_id = None
        # player_id -> Player object
        self.players = {}

        # role tracking (optional caches)
        self.mafia_ids = set()

        # channel tracking
        self.player_channels = {}  # player_id -> channel_id

        # special roles
        self.executioner_targets = {}  # player_id -> target_id