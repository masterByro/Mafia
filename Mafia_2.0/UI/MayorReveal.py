import discord

from typing import Tuple

def reveal_mayor(game, player) -> Tuple[bool, str]:
    if player is None: return False, "You are not part of the game."
    if player.role != "Chancellor": return False, "Nice Try bozo"
    if player.revealed: return False, "You have already revealed your role"
    if not player.alive: return False, "You are dead. Too late mate. So sad"
    if not game.is_day: return False, "You can only reveal your role during the day"
    return True, "You successfully reveal yourself."

class MayorRevealView(discord.ui.View):
    def __init__(self, game):
        super().__init__(timeout=None)
        self.game = game

    @discord.ui.button(
        label="Reveal Role",
        style=discord.ButtonStyle.success,  # green
        emoji="🟢"
    )
    async def reveal(self, interaction: discord.Interaction, button: discord.ui.Button):
        game = self.game
        player = game.players.get(interaction.user.id)

        success, message = reveal_mayor(game, player)
        if not success:
            return await interaction.response.send_message(message, ephemeral=True)
        
        # SUCCESS
        player.revealed = True
        guild = interaction.guild
        if guild is None: return

        channel = guild.get_channel(game.town_channel_id)
        if isinstance(channel, discord.TextChannel) or isinstance(channel, discord.Thread):
            await channel.send(f"📢 {player.name} has revealed themselves as the Chancellor!")

        await interaction.response.send_message(message, ephemeral=True)

