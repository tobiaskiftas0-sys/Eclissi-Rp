import discord
from discord.ext import commands
import os
import asyncio

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

ai_attivi = {}

def get_log_channel(guild):
    for ch in guild.text_channels:
        if "log-bot" in ch.name.lower() or "log" in ch.name.lower():
            return ch
    return None

async def manda_log(guild, titolo, desc, colore=0x2b2d31):
    ch = get_log_channel(guild)
    if ch:
        embed = discord.Embed(title=titolo, description=desc, color=colore)
        try: await ch.send(embed=embed)
        except: pass

async def risposta_ia(testo):
    t = testo.lower()
    if "whitelist" in t or "wl" in t: return "Per whitelist devi avere 16 anni + microfono + domanda fatta. Dimmi nome in game e ti controllo!"
    if "cittadinanza" in t: return "Per cittadinanza devi essere whitelistato e andare in Comune in città con documento RP. Vuoi sapere dove è il Comune?"
    if "porto" in t or "pda" in t or "arma" in t: return "Per porto d'armi serve cittadinanza + corso in Questura/Armeria + fedina pulita. Hai già cittadinanza?"
    if "codice" in t or "entra" in t or "connect" in t: return "Codice server nell'ultimo SSU! Se non lo trovi clicca bottone rosso e chiamo staff umano subito."
    if "bug" in t or "crash" in t: return "Mandami video + cosa dice F8 così ti aiuto subito!"
    if "ciao" in t or "salve" in t: return "Ciao! Sono IA di Eclissi, dimmi il tuo problema e ti rispondo!"
    return f"Ho capito: '{testo}'. Spiegami meglio con ID/video/dettagli e ti aiuto!"

class AIView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Chiudi Ticket", style=discord.ButtonStyle.green, emoji="✅", custom_id="close_final_2")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Chiudo...", ephemeral=True)
        await asyncio.sleep(2)
        try: await interaction.channel.delete()
        except: pass
    @discord.ui.button(label="CHIAMA STAFF UMANO", style=discord.ButtonStyle.red, emoji="🚨", custom_id="call_staff_final_2")
    async def staff(self, interaction: discord.Interaction, button: discord.ui.Button):
        ai_attivi[interaction.channel.id] = False
        role = discord.utils.get(interaction.guild.roles, name="Staff") or discord.utils.get(interaction.guild.roles, name="STAFF")
        ping = role.mention if role else "@here"
        embed = discord.Embed(title="🚨 STAFF RICHIESTO", description=f"{interaction.user.mention} vuole staff umano. IA off.", color=0xff0000)
        await interaction.response.send_message(content=ping, embed=embed)

class TicketSelect(discord.ui.Select):
    def __init__(self):
        opts = [
            discord.SelectOption(label="Supporto Generale", emoji="🎫"),
            discord.SelectOption(label="Whitelist / Cittadinanza", emoji="📝"),
            discord.SelectOption(label="Porto d'Armi", emoji="🔫"),
            discord.SelectOption(label="Segnalazione / Ban", emoji="🚨"),
            discord.SelectOption(label="Bug / Crash", emoji="🐛"),
        ]
        super().__init__(placeholder="Seleziona e parla con IA...", options=opts, custom_id="ticket_all_final")
    async def callback(self, interaction: discord.Interaction):
        scelta = self.values[0]
        guild = interaction.guild
        overw = {guild.default_role: discord.PermissionOverwrite(view_channel=False), interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True), guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)}
        ch = await guild.create_text_channel(name=f"ticket-{interaction.user.name}".lower().replace(" ","-"), overwrites=overw)
        ai_attivi[ch.id] = True
        embed = discord.Embed(title="