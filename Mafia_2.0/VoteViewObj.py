import discord

class VoteView(discord.ui.View):
    def __init__(self, game, voter_id):
        super().__init__(timeout=None)
        self.game = game
        self.voter_id = voter_id

    async def register_vote(self, interaction, choice):
        player = self.game.players.get(interaction.user.id)

        if not self.game.canDecide:
            return await interaction.response.send_message("You cannot cast a decision right now.", ephemeral=True)

        if player is None:
            return await interaction.response.send_message("You are not part of the game.", ephemeral=True)

        if not player.alive:
            return await interaction.response.send_message("Dead players cannot vote.", ephemeral=True)

        if player.votedFor:
            return await interaction.response.send_message("You cannot vote on yourself.", ephemeral=True)

        # Abstain clears their vote
        player.decision = None if choice == "abstain" else choice

        channel = interaction.guild.get_channel(self.game.town_channel_id)
        if channel:
            await channel.send(f"🗳️ {player.name} has voted")

        await interaction.response.send_message(f"You voted {choice.upper()}.",ephemeral=True)

    @discord.ui.button(label="Innocent", style=discord.ButtonStyle.success)
    async def innocent(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.register_vote(interaction, "innocent")
    
    @discord.ui.button(label="Abstain", style=discord.ButtonStyle.secondary, emoji="⚪")
    async def abstain(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.register_vote(interaction, "abstain")

    @discord.ui.button(label="Guilty", style=discord.ButtonStyle.danger)
    async def guilty(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.register_vote(interaction, "guilty")
