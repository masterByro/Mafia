import discord

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

        message = None
        if player is None: message = "You are not part of the game."
        if player.role != "Mayor": message = "Nice Try bozo"
        if player.revealed: message = "You have already revealed your role"
        if not player.alive: message = "You are dead. Too late mate. So sad"
        if not game.is_day: message = "You can only reveal your role during the day"
        if message:
            return await interaction.response.send_message(message, ephemeral=True)

        # SUCCESS
        player.revealed = True
        guild = interaction.guild
        if guild is None: return

        channel = guild.get_channel(game.town_channel_id)
        if isinstance(channel, discord.TextChannel) or isinstance(channel, discord.Thread):
            await channel.send(f"📢 {player.name} has revealed themselves as the Mayor!")

        await interaction.response.send_message("You successfully reveal yourself.", ephemeral=True)

