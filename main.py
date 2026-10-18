import discord
from discord.ext import commands
import os
import asyncio

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- SISTEMA TICKET PROFESSIONALE CON MENU ---
class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Supporto Generale", description="Info e assistenza generale", emoji="🎫"),
            discord.SelectOption(label="Segnalazione Player", description="Segnala un player o cheater", emoji="🚨"),
            discord.SelectOption(label="Whitelist", description="Problemi con la whitelist", emoji="📝"),
            discord.SelectOption(label="Bug & Problemi Tecnici", description="Segnala un bug del server", emoji="🐛"),
            discord.SelectOption(label="Staff & Donazioni", description="Candidature, donazioni, partnership", emoji="💎"),
        ]
        super().__init__(placeholder="🔽 Seleziona il tipo di assistenza...", min_values=1, max_values=1, options=options, custom_id="ticket_select")

    async def callback(self, interaction: discord.Interaction):
        scelta = self.values[0]
        guild = interaction.guild
        try:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, read_message_history=True),
                guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
            }
            # Crea canale ticket
            channel_name = f"🎫・{interaction.user.name}".lower().replace(" ", "-")
            ticket