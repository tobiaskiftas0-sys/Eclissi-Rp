import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- TICKET CON MENU A SCELTA ---
class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Supporto Generale", description="Assistenza generica", emoji="🎫"),
            discord.SelectOption(label="Segnalazione Player", description="Segnala un player / cheater", emoji="🚨"),
            discord.SelectOption(label="Problema Whitelist", description="Problemi con la whitelist", emoji="📝"),
            discord.SelectOption(label="Bug / Problema Tecnico", description="Hai trovato un bug", emoji="🐛"),
            discord.SelectOption(label="Candidatura Staff / Donazioni", description="Staff, donazioni, partnership", emoji="💎"),
        ]
        super().__init__(placeholder="Seleziona il tipo di assistenza...", options=options, custom_id="ticket_select")

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        categoria_scelta = self.values[0]
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        
        channel = await guild.create_text_channel(f"🎫-{interaction.user.name}-{categoria_scelta[:10]}", overwrites=overwrites)
        
        embed = discord.Embed(
            title=f"🎫 Ticket - {categoria_scelta}",
            description=f"Ciao {interaction.user.mention}, hai aperto un ticket per **{categoria_scelta}**.\n\n**Spiega dettagliatamente il tuo problema qui sotto.** Lo staff ti risponderà il prima possibile.\n\n> Si prega di non pingare lo staff, verrai assistito in ordine di arrivo.",
            color=0x5865F2
        )
        embed.add_field(name="Utente", value=interaction.user.mention, inline=True)
        embed.add_field(name="Categoria", value=categoria_scelta, inline=True)
        embed.set_footer(text="Eclissi RP - Support System")
        
        await channel.send(content=f"{interaction.user.mention}", embed=embed, view=CloseTicketView())
        await interaction.response.send_message(f"✅ Ticket aperto con successo: {channel.mention}", ephemeral=True)

class TicketSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="🔒 Chiudi Ticket", style=discord.ButtonStyle.red, emoji="🔒", custom_id="close_ticket")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Il ticket verrà chiuso in 3 secondi...")
        await discord.utils.sleep_until(discord.utils.utcnow() + discord.timedelta(seconds=3))
        await interaction.channel.delete(reason=f"Ticket chiuso da {interaction.user}")

@bot.event
async def on_ready():
    print(f"ONLINE {