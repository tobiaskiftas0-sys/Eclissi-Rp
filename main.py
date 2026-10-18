import discord
from discord.ext import commands
import os
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- TICKET CON MENU ---
class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Supporto Generale", emoji="🎫"),
            discord.SelectOption(label="Segnalazione Player", emoji="🚨"),
            discord.SelectOption(label="Whitelist", emoji="📝"),
            discord.SelectOption(label="Bug / Tecnico", emoji="🐛"),
            discord.SelectOption(label="Staff / Donazioni", emoji="💎"),
        ]
        super().__init__(placeholder="Scegli il tipo di assistenza...", options=options, custom_id="ticket_select")
    async def callback(self, interaction: discord.Interaction):
        try:
            guild = interaction.guild
            scelta = self.values[0]
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
            }
            channel = await guild.create_text_channel(f"ticket-{interaction.user.name}", overwrites=overwrites)
            embed = discord.Embed(title=f"🎫 {scelta}", description=f"Ciao {interaction.user.mention}\nCategoria: **{scelta}**\nSpiega il tuo problema, lo staff ti risponderà.", color=0x5865F2)
            await channel.send(embed=embed, view=CloseTicketView())
            await interaction.response.send_message(f"✅ Ticket creato: {channel.mention}", ephemeral=True)
        except Exception as e:
            print(f"Errore ticket: {e}")
            await interaction.response.send_message(f"❌ Errore: {e}", ephemeral=True)

class TicketSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="🔒 Chiudi Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Chiusura in 3 secondi...")
        await asyncio.sleep(3)
        await interaction.channel.delete()

@bot.event
async def on_ready():
    print(f"ONLINE {bot.user}")
    bot.add_view(TicketSelectView())
    bot.add_view(CloseTicketView())
    try:
        await bot.tree.sync()
        print("Sync ok")
    except Exception as e:
        print(f"Sync error: {e}")

@bot.tree.command(name="ssu", description="Annuncia apertura server")
async def ssu(interaction: discord.Interaction, codice_server: str, f8_connect: str = None):
    await interaction.response.defer()
    if f8_connect is None:
        f8_connect = f"connect {codice_server}"
    embed = discord.Embed(title="🟢 ECLISSI RP - SERVER APERTO", description=f"**La città di Eclissi ha aperto le sue porte!**\n\nSiamo lieti di annunciarvi che il server è ufficialmente **ONLINE**.\n\n**📡 CONNESSIONE:**\n**Codice:** `{codice_server}`\n**F8:** `{f8_connect}`\n\n**📜 Regole:**\n• Rispetta il regolamento\n• RP serio e di qualità\n• Divertiti!\n\nVi aspettiamo in città!", color=0x00ff00)
    embed.set_footer(text="Eclissi RP")
    await interaction.followup.send(content="@everyone", embed=embed)

@bot.tree.command(name="ssd", description="Annuncia chiusura server")
async def ssd(interaction: discord.Interaction, motivo: str):
    await interaction.response.defer()
    embed = discord.Embed(title="🔴 E