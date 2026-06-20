from typing import Dict
from player import Player

class GameState:
    def __init__(self):
        self.running = False
        self.is_day = True
        self.day_number = 1
        self.can_vote = True
        self.canDecide = False
        self.voteAttempts = 3

        #Discord channels
        self.town_channel_id = None
        self.dead_channel_id = None
        self.mafia_channel_id = None

        self.dead_role_id = None #Discord role

        # player_id -> Player object
        self.players: Dict[int, Player] = {}

        # channel tracking
        self.player_channels: Dict[int, int] = {} # player_id -> channel_id
        self.player_will_channels: Dict[int, int]  = {}