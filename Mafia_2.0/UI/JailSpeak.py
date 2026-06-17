import discord

from utils import getByRole, sendToPlayer

class JailSpeakView(discord.ui.View):
    def __init__(self, game, is_jailor: bool):
        super().__init__(timeout=None)
        self.game = game
        self.is_jailor = is_jailor

    @discord.ui.button(label="Speak", style=discord.ButtonStyle.primary)
    async def speak(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(
            JailSpeakModal(self.game, self.is_jailor)
        )
        
class JailSpeakModal(discord.ui.Modal, title="Jail Communication"):
    message = discord.ui.TextInput(
        label="Type your message",
        style=discord.TextStyle.paragraph,
        max_length=1000
    )

    def __init__(self, game, is_jailor: bool):
        super().__init__()
        self.game = game
        self.is_jailor = is_jailor

    async def on_submit(self, interaction: discord.Interaction):
        speaker = self.game.players.get(interaction.user.id)
        jailor = getByRole(self.game.players, 'Jailor')

        if self.game.is_day:
            return await interaction.response.send_message(
                "You can only use this at night",
                ephemeral=True
            )

        if jailor is None or speaker is None:
            return await interaction.response.send_message("Fail 1", ephemeral=True)

        prisoner_id = jailor.roundInput
        if prisoner_id is None:
            return await interaction.response.send_message(
                "No prisoner was selected during the day",
                ephemeral=True
            )

        prisoner = self.game.players.get(prisoner_id)
        if prisoner is None:
            return await interaction.response.send_message(
                "No prisoner to speak to",
                ephemeral=True
            )

        msg = self.message.value

        jailor_channel = self.game.player_channels.get(jailor.id)
        prisoner_channel = self.game.player_channels.get(prisoner.id)

        guild = interaction.guild

        if not jailor_channel or not prisoner_channel:
            return await interaction.response.send_message(
                "Missing jail channels.",
                ephemeral=True
            )

        if not (speaker.id == jailor.id or speaker.id == prisoner.id):
            return await interaction.response.send_message(
                "Not your command to use buster",
                ephemeral=True
            )

        # Format depending on speaker
        if speaker.id == jailor.id:
            formatted = f"**[Jailor]** {msg}"
        else:
            formatted = f"**[{speaker.name}]** {msg}"

        # Send to BOTH sides

        guild = interaction.guild
        if guild is None:
            return await interaction.response.send_message(
                "Guild not found.",
                ephemeral=True
            )
        
        for ch_id in (jailor_channel, prisoner_channel):
            channel = guild.get_channel(ch_id)
            if isinstance(channel, (discord.TextChannel, discord.Thread)):
                await channel.send(formatted)

        await interaction.response.defer()