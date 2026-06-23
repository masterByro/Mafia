import discord
from gamestate import GameState
from player import Player

async def onAlert(game: GameState, player: Player):
    if player is None: return "You are not part of the game."
    if player.role not in ['Veteran', 'Survivor']: return "Nice Try bozo"
    if player.onAlert: return "You already have selected to be on alert"
    if player.alerts == 0: return "You have already been on alert 3 times"
    if not player.alive: return "You are dead. Too late mate. So sad"
    if game.is_day: return "You can only go on alert at night"
    
    player.alerts -= 1
    player.onAlert = True
    return "You are now on alert"

class AlertView(discord.ui.View):
    def __init__(self, game):
        super().__init__(timeout=None)
        self.game = game

    @discord.ui.button(
        label="Go on Alert",
        style=discord.ButtonStyle.secondary,  # grey
        emoji="🛡️"
    )
    async def alert(self, interaction: discord.Interaction, button: discord.ui.Button):
        game = self.game
        player = game.get_player_from_interaction(interaction)

        message = await onAlert(game, player)
        await interaction.response.send_message(message, ephemeral=True)