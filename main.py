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
        if "log-bot" in ch.name.lower():
            return ch
    return None

async def manda_log(guild, titolo, desc, colore=0x2b2d31):
    ch = get_log_channel(guild)
    if ch:
        try:
            e = discord.Embed(title=titolo, description=desc, color=colore)
            await ch.send(embed=e)
        except: pass

async def risposta_ia(testo):
    t = testo.lower()
    if "whitelist" in t or "wl" in t: return "Per WL serve 16 anni + microfono + domanda. Dimmi nome in game!"
    if "cittadinanza" in t: return "Per cittadinanza devi essere WL e andare in Comune in città!"
    if "porto" in t or "pda" in t or "arma" in t: return "Per porto d'armi serve cittadinanza + corso in Questura + fedina pulita!"
    if "codice" in t or "entra" in t or "connect" in t or "ip" in t: return "Codice nell'ultimo SSU! Se non lo trovi clicca bottone rosso e chiamo staff!"
    if "staff" in t: return "Vuoi diventare staff? Scrivi in ticket e ti mando i requisiti!"
    if "ban" in t: return "Se sei bannato dimmi cosa ti esce quando provi ad entrare!"
    if "bug" in t or "crash" in t: return "Mandami video + F8 così ti aiuto subito!"
    if "ciao" in t or "salve" in t: return "Ciao! Sono l'IA di Eclissi, dimmi pure!"
    return f"Ho capito: '{testo}'. Spiegami con ID/video/dettagli!"

class AIView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Chiudi Ticket", style=discord.ButtonStyle.green, emoji="✅", custom_id="close_final_all")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        try: await interaction.channel.delete()
        except: pass
    @discord.ui.button(label="CHIAMA STAFF UMANO 🚨", style=discord.ButtonStyle.red, custom_id="staff_call_final_all")
    async def staff(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        ai_attivi[interaction.channel.id] = False
        role = discord.utils.get(interaction.guild.roles, name="Staff") or discord.utils.get(interaction.guild.roles, name="STAFF")
        ping = role.mention if role else "@here"
        e = discord.Embed(title="🚨 STAFF RICHIESTO", description=f"{interaction.user.mention} ha chiesto staff umano. IA OFF.", color=0xff0000)
        await interaction.followup.send(content=ping, embed=e)

class TicketSelect(discord.ui.Select):
    def __init__(self):
        opts = [
            discord.SelectOption(label="Supporto Generale", emoji="🎫", description="IA ti risponde subito"),
            discord.SelectOption(label="Whitelist", emoji="📝"),
            discord.SelectOption(label="Cittadinanza", emoji="🏛️"),
            discord.SelectOption(label="Porto d'Armi", emoji="🔫"),
            discord.SelectOption(label="Bando / Sban", emoji="🔨"),
            discord.SelectOption(label="Staff / Candidatura", emoji="👮"),
            discord.SelectOption(label="Bug / Crash", emoji="🐛"),
        ]
        super().__init__(placeholder="Seleziona motivo - IA ATTIVA...", options=opts, custom_id="ticket_final_all")
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        scelta = self.values[0]
        guild = interaction.guild
        overw = {guild.default_role: discord.PermissionOverwrite(view_channel=False), interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True), guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)}
        ch = await guild.create_text_channel(name=f"ticket-{interaction.user.name}".lower().replace(" ","-")[:20], overwrites=overw)
        ai_attivi[ch.id] = True
        embed = discord.Embed(title="🤖 ECLISSI RP - IA ATTIVA", description=f"{interaction.user.mention}\nHai scelto **{scelta}**\n\n**SCRIVI QUI SOTTO E TI RISPONDO SUBITO!**\n\nEsempi:\n`info cittadinanza`\n`info porto d'armi`\n`non entro codice`\n`voglio staff`\n\nSe non ti aiuto -> Bottone ROSSO chiama staff umano!", color=0x5865F2)
        await ch.send(embed=embed, view=AIView())
        await interaction.followup.send(f"✅ Ticket aperto: {ch.mention} - L'IA ti aspetta!", ephemeral=True)
        await manda_log(guild, "🎫 TICKET APERTO", f"{interaction.user.mention} -> {scelta} -> {ch.mention}", 0x5865F2)

class TicketView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None); self.add_item(TicketSelect())

@bot.event
async def on_ready():
    print(f"ONLINE {bot.user}")
    bot.add_view(TicketView())
    bot.add_view(AIView())
    await bot.tree.sync()

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild: return
    if message.channel.id in ai_attivi and ai_attivi[message.channel.id] and "ticket-" in message.channel.name:
        async with message.channel.typing():
            await asyncio.sleep(1)
            risp = await risposta_ia(message.content)
            e = discord.Embed(description=risp, color=0x2ecc71)
            e.set_author(name="🤖 Eclissi AI", icon_url=bot.user.display_avatar.url)
            await message.channel.send(embed=e, view=AIView())
    await bot.process_commands(message)

# --- COMANDI ---

@bot.tree.command(name="ssu", description="SSU LUNGO")
async def ssu(interaction: discord.Interaction, codice_server: str, ip_server: str, note: str = ""):
    await interaction.response.defer()
    embed = discord.Embed(title="🟢 ECLISSI RP - SERVER APERTO | SSU", description=f"**CITTADINI SIAMO ONLINE!**\n\n**📡 CODICE FIVEM:**\n```{codice_server}```\n**📡 CONNECT F8:**\n```connect {ip_server}```\n\n**📝 Note:** {note if note else 'Nessuna'}\n\nBuon RP a tutti!", color=0x2ecc71)
    if interaction.guild.icon: embed.set_thumbnail(url=interaction.guild.icon.url)
    embed.set_footer(text=f"Aperto da {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
    await interaction.followup.send(content="@everyone", embed=embed)
    await manda_log(interaction.guild, "🟢 SSU", f"Da {interaction.user.mention} - {codice_server}", 0x2ecc71)

@bot.tree.command(name="ssd", description="SSD LUNGO")
async def ssd(interaction: discord.Interaction, motivo: str, riapertura: str, note: str = ""):
    await interaction.response.defer()
    embed = discord.Embed(title="🔴 ECLISSI RP - SERVER CHIUSO | SSD", description=f"**CITTA' CHIUSA**\n\n**Motivo:** {motivo}\n\n**Riapertura:** {riapertura}\n\n**Note:** {note if note else 'Nessuna'}", color=0xe74c3c)
    if interaction.guild.icon: embed.set_thumbnail(url=interaction.guild.icon.url)
    await interaction.followup.send(content="@everyone", embed=embed)
    await manda_log(interaction.guild, "🔴 SSD", f"Da {interaction.user.mention} - {motivo}", 0xe74c3c)

@bot.tree.command(name="annuncio", description="Annuncio personalizzabile")
async def annuncio(interaction: discord.Interaction, titolo: str, descrizione: str, colore: str = "blu", immagine: str = ""):
    await interaction.response.defer()
    colori = {"blu":0x3498db,"verde":0x2ecc71,"rosso":0xe74c3c,"giallo":0xf1c40f,"viola":0x9b59b6,"arancio":0xe67e22}
    e = discord.Embed(title=titolo, description=descrizione, color=colori.get(colore.lower(),0x3498db))
    if immagine.startswith("http"): e.set_image(url=immagine)
    if interaction.guild.icon: e.set_thumbnail(url=interaction.guild.icon.url)
    e.set_footer(text=f"Da {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
    await interaction.followup.send(embed=e)

@bot.tree.command(name="whitelist", description="Esito whitelist")
async def whitelist(interaction: discord.Interaction, utente: discord.Member, esito: str, motivo: str = ""):
    await interaction.response.defer()
    col = 0x2ecc71 if "approv" in esito.lower() else 0xe74c3c
    e = discord.Embed(title="📝 ESITO WHITELIST", description=f"{utente.mention}\n**Esito:** {esito}\n**Motivo:** {motivo}", color=col)
    await interaction.followup.send(content=utente.mention, embed=e)
    await manda_log(interaction.guild, "📝 WL", f"{utente.mention} -> {esito}", col)

@bot.tree.command(name="cittadinanza", description="Esito cittadinanza")
async def cittadinanza(interaction: discord.Interaction, utente: discord.Member, esito: str, motivo: str = ""):
    await interaction.response.defer()
    col = 0x2ecc71 if "approv" in esito.lower() else 0xe74c3c
    e = discord.Embed(title="🏛️ ESITO CITTADINANZA - COMUNE", description=f"{utente.mention}\n**Esito:** {esito}\n**Motivo:** {motivo}\n\nPresentarsi in Comune.", color=col)
    await interaction.followup.send(content=utente.mention, embed=e)
    await manda_log(interaction.guild, "🏛️ CITTADINANZA", f"{utente.mention} -> {esito}", col)

@bot.tree.command(name="portodarmi", description="Esito porto d'armi")
async def portodarmi(interaction: discord.Interaction, utente: discord.Member, esito: str, motivo: str = "", tipo_arma: str = ""):
    await interaction.response.defer()
    col = 0x2ecc71 if "approv" in esito.lower() else 0xe74c3c
    e = discord.Embed(title="🔫 PORTO D'ARMI - QUESTURA", description=f"{utente.mention}\n**Tipo:** {tipo_arma if tipo_arma else 'Non specificato'}\n**Esito:** {esito}\n**Motivo:** {motivo}", color=col)
    await interaction.followup.send(content=utente.mention, embed=e)
    await manda_log(interaction.guild, "🔫 PDA", f"{utente.mention} -> {esito} {tipo_arma}", col)

@bot.tree.command(name="bando", description="Bando utente")
async def bando(interaction: discord.Interaction, utente: discord.Member, motivo: str, durata: str, prova: str = ""):
    await interaction.response.defer()
    e = discord.Embed(title="🔨 BANDO UFFICIALE", description=f"{utente.mention} ({utente.id})\n**Motivo:** {motivo}\n**Durata:** {durata}\n**Prova:** {prova if prova else 'Allegata'}", color=0xff0000)
    e.set_footer(text=f"Da {interaction.user.display_name}")
    await interaction.followup.send(embed=e)
    await manda_log(interaction.guild, "🔨 BANDO", f"{utente.mention} - {motivo} - {durata}", 0xff0000)

@bot.tree.command(name="sban", description="Sban utente")
async def sban(interaction: discord.Interaction, utente: discord.Member, motivo: str = ""):
    await interaction.response.defer()
    e = discord.Embed(title="✅ SBAN", description=f"{utente.mention} sbannato!\n**Motivo:** {motivo}", color=0x2ecc71)
    await interaction.followup.send(embed=e)
    await manda_log(interaction.guild, "✅ SBAN", f"{utente.mention} - {motivo}", 0x2ecc71)

@bot.tree.command(name="staff", description="Gestione staff")
async def staff(interaction: discord.Interaction, azione: str, utente: discord.Member, ruolo: str = ""):
    await interaction.response.defer()
    e = discord.Embed(title="👮 GESTIONE STAFF", description=f"**Azione:** {azione}\n**Utente:** {utente.mention}\n**Ruolo:** {ruolo}", color=0x9b59b6)
    await interaction.followup.send(embed=e)
    await manda_log(interaction.guild, "👮 STAFF", f"{azione} -> {utente.mention} {ruolo} da {interaction.user.mention}", 0x9b59b6)

@bot.tree.command(name="ticket-panel", description="[ADMIN] Pannello ticket con IA")
async def ticket_panel(interaction: discord.Interaction):
    await interaction.response.defer()
    if not interaction.user.guild_permissions.administrator:
        await interaction.followup.send("Solo admin!", ephemeral=True)
        return
    e = discord.Embed(title="🎫 ECLISSI RP - ASSISTENZA IA 🤖", description="**Seleziona qui sotto!**\n\nIA ti risponde SUBITO in ticket!\n- WL / Cittadinanza / PDA\n- Bando / Bug\n- Staff\n\nBottone rosso = Chiama staff umano!", color=0x5865F2)
    await interaction.followup.send(embed=e, view=TicketView())

bot.run(os.getenv("TOKEN"))