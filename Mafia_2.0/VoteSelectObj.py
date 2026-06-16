import discord
from voting import on_vote

class VoteView(discord.ui.View):
    def __init__(self, game, voter_id):
        super().__init__(timeout=None)
        self.add_item(VoteSelect(game, voter_id))

class VoteSelect(discord.ui.Select):
    def __init__(self, game, voter_id):
        self.game = game

        options = [discord.SelectOption(label=p.name, value=str(p.id)) for p in game.players.values() if p.alive and p.id != voter_id]

        super().__init__(
            placeholder="🗳️ Choose a player to vote for...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        game = self.game

        voter = game.players.get(interaction.user.id)

        if game.can_vote == False:
            return await interaction.response.send_message("You cannot vote right now.", ephemeral=True)

        if voter is None:
            return await interaction.response.send_message("You are not part of the game.", ephemeral=True)

        if not voter.alive:
            return await interaction.response.send_message("Dead players cannot vote.", ephemeral=True)

        target_id = int(self.values[0])
        target = game.players.get(target_id)

        if target is None:
            return await interaction.response.send_message("Invalid player selection.", ephemeral=True)

        if target.id == voter.id:
            return await interaction.response.send_message("You cannot vote for yourself.", ephemeral=True)

        if not target.alive:
            return await interaction.response.send_message("You cannot vote for a dead player.", ephemeral=True)

        # SUCCESS (your original logic preserved)
        voter.vote = target.id

        guild = interaction.guild
        if guild is None: return
        channel = guild.get_channel(self.game.town_channel_id)
        if isinstance(channel, discord.TextChannel) or isinstance(channel, discord.Thread):
            await channel.send(f"🗳️ {voter.name} has voted for {target.name}")

        await interaction.response.send_message(f"You voted for **{target.name}**.", ephemeral=True)
        await on_vote(guild, game)