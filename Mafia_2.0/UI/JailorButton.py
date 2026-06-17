import discord
from gamestate import GameState
from player import Player

async def onExecute(game: GameState, player: Player):
    if player is None or player.roundInput is None: return "You are not part of the game or you have no target."
    if player.role != 'Jailor': return "Nice Try bozo"
    if game.is_day or not player.alive: return '2 late mate'

    target = game.players.get(player.roundInput)
    if target is None or not target.alive: return "Your jailed target is no longer valid."

    player.willExecute = not player.willExecute

    if player.willExecute:
        message = f"⚔️ You have decided to execute **{target.name}** tonight. Press again to change your mind"
        target_message = "⚔️ The Jailor has decided to execute you tonight."
    else:
        message = f"You have decided NOT to execute **{target.name}**."
        target_message = "The Jailor has changed their mind."

    return message, target_message

class ExecuteView(discord.ui.View):
    def __init__(self, game):
        super().__init__(timeout=None)
        self.game = game

    @discord.ui.button(
        label="Execute",
        style=discord.ButtonStyle.danger, 
        emoji="💀"
    )
    async def execute(self, interaction: discord.Interaction, button: discord.ui.Button):
        game = self.game
        player = game.players.get(interaction.user.id)

        message, target_message = await onExecute(game, player)
        await interaction.response.send_message(message, ephemeral=True)

        guild = interaction.guild
        if guild is None: return
        channel = guild.get_channel(game.player_channels.get(player.roundInput))
        if isinstance(channel, discord.TextChannel) or isinstance(channel, discord.Thread):
            await channel.send(target_message)