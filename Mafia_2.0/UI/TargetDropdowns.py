import discord

from roleActions import getPossibleOptions


class TargetView(discord.ui.View):
    def __init__(self, game, possibleOptions):
        super().__init__(timeout=None)
        self.add_item(TargetSelect(game, possibleOptions))

class TargetSelect(discord.ui.Select):
    def __init__(self, game, possibleOptions):
        self.game = game

        options = [discord.SelectOption(label=p.name, value=str(p.id)) for p in possibleOptions]


        super().__init__(
            placeholder="🗳️ Choose a player to target...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        game = self.game
        player = game.players.get(interaction.user.id)
        possibleOptions = getPossibleOptions(game, player)

        target_id = int(self.values[0])
        target = game.players.get(target_id)
        if target in possibleOptions:
            player.roundInput = target.id
            await interaction.response.send_message(f"You will target {target.name} tonight.", ephemeral=True)
        else: 
            await interaction.response.send_message("I think you're trolling mate", ephemeral=True)
