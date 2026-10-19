import discord
from discord.ext import commands
import os
import asyncio

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# --- VIEW PER CHIAMARE STAFF ---
class AIStaffView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Ho risolto, Chiudi Ticket", style=discord.ButtonStyle.green, emoji="✅", custom_id="ai_close")
    async def close_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 Chiusura in 3 secondi...", ephemeral=True)
        await asyncio.sleep(3)
        try: await interaction.channel.delete(reason="Chiuso da utente")
        except: pass

    @discord.ui.button(label="Non ho capito, Chiama Staff Umano", style=discord.ButtonStyle.red, emoji="🚨", custom_id="call_staff")
    async def staff_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        # Cerca ruolo staff
        staff_role = None
        for name in ["Staff", "STAFF", "Moderatore", "Admin", "ADMIN", "Supporto"]:
            staff_role = discord.utils.get(guild.roles, name=name)
            if staff_role: break
        
        ping = staff_role.mention if staff_role else "@Staff"
        
        embed = discord.Embed(
            title="🚨 RICHIESTA STAFF UMANO",
            description=f"{interaction.user.mention} ha bisogno di un membro dello staff umano.\n\nL'assistente IA non è riuscito ad aiutare.",
            color=0xff0000
        )
        await interaction.response.send_message(content=f"{ping} {interaction.user.mention}", embed=embed)
        # Sblocca canale per staff
        try:
            if staff_role:
                await interaction.channel.set_permissions(staff_role, view_channel=True, send_messages=True)
        except: pass

# --- SELECT TICKET ---
class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Supporto Generale", emoji="🎫"),
            discord.SelectOption(label="Whitelist", description="Problemi whitelist", emoji="📝"),
            discord.SelectOption(label="Segnalazione Player", emoji="🚨"),
            discord.SelectOption(label="Bug Tecnici", emoji="🐛"),
            discord.SelectOption(label="Donazioni & Candidature", emoji="💎"),
        ]
        super().__init__(placeholder="Seleziona assistenza...", options=options, custom_id="ticket_select_v6")

    async def callback(self, interaction: discord.Interaction):
        scelta = self.values[0]
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
        }
        channel_name = f"ticket-{interaction.user.name}".lower().replace(" ", "-")
        ticket_ch = await guild.create_text_channel(name=channel_name, overwrites=overwrites)

        # MESSAGGIO CON AI
        embed_ai = discord.Embed(
            title="🤖 ASSISTENTE IA - ECLISSI RP",
            description=f"Ciao {interaction.user.mention}!\n\nSono l'assistente virtuale di **Eclissi RP**.\nHai selezionato: **{scelta}**\n\n**Ecco come posso aiutarti:**\n"
            "• **Whitelist:** Controlla di aver fatto domanda sul nostro sito e di avere più di 16 anni.\n"
            "• **Bug:** Invia video/screenshot e descrivi quando succede.\n"
            "• **Segnalazione:** Invia ID del player, video prova e orario.\n"
            "• **Supporto:** Descrivi il tuo problema in modo dettagliato qui sotto.\n\n"
            "Se non riesco ad aiutarti, clicca il bottone rosso qui sotto per chiamare uno **STAFF UMANO**.",
            color=0x5865F2
        )
        embed_ai.set_footer(text="Eclissi RP - Supporto Automatico")
        
        await ticket_ch.send(f"{interaction.user.mention}", embed=embed_ai, view=AIStaffView())
        await interaction.response.send_message(f"✅ Ticket creato: {ticket_ch.mention}", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

@bot.event
async def on_ready():
    print(f"ONLINE {bot.user}")
    bot.add_view(TicketView())
    bot.add_view(AIStaffView())
    await bot.tree.sync()

# --- SSU LUNGO CON CODICE ---
@bot.tree.command(name="ssu", description="Annuncia apertura server con codice")
async def ssu(interaction: discord.Interaction, codice_server: str, ip_server: str = ""):
    embed = discord.Embed(
        title="🟢 ECLISSI RP - SERVER APERTO [SSU]",
        description=f"**CITTADINI, LA CITTÀ È APERTA!**\n\nSiamo lieti di annunciare che Eclissi RP è ora **ONLINE**.\nLo staff vi augura buon RolePlay e tanto divertimento!\n\n**━━━━━━━━━━━━━━━━━━**\n**📡 CONNESSIONE**\n**━━━━━━━━━━━━━━━━━━**\n\n**🔹 Codice Server:**\n```{codice_server}```\n\n**🔹 IP / F8 Connect:**\n```connect {ip_server if ip_server else codice_server}```\n\n**Metodo 2:** Scrivi in F8 `{codice_server}`\n\n**━━━━━━━━━━━━━━━━━━**\n**📜 REGOLE**\nRispetta regolamento, fai RP serio e divertiti!\n\nVi aspettiamo in città!",
        color=0x2ecc71
    )
    if interaction.guild.icon: embed.set_thumbnail(url=interaction.guild.icon.url)
    await interaction.response.send_message(content="@everyone", embed=embed)

# --- SSD LUNGO ---
@bot.tree.command(name="ssd", description="Annuncia chiusura server")
async def ssd(interaction: discord.Interaction, motivo: str, riapertura: str = "A breve"):
    embed = discord.Embed(
        title="🔴 ECLISSI RP - SERVER CHIUSO [SSD]",
        description=f"**ATTENZIONE, CITTÀ CHIUSA**\n\nIl server è attualmente in **SHUTDOWN**.\n\n**━━━━━━━━━━━━━━━━━━**\n**📋 MOTIVO**\n> {motivo}\n\n**⏰ RIAPERTURA PREVISTA**\n> {riapertura}\n\nRimanete sintonizzati per il prossimo SSU. Grazie a tutti per aver giocato oggi!",
        color=0xe74c3c
    )
    if interaction.guild.icon: embed.set_thumbnail(url=interaction.guild.icon.url)
    await interaction.response.send_message(content="@everyone", embed=embed)

@bot.tree.command(name="annuncio", description="Annuncio ufficiale")
async def annuncio(interaction: discord.Interaction, testo: str):
    embed = discord.Embed(title="📢 ANNUNCIO UFFICIALE", description=testo, color=0x3498db)
    embed.set_footer(text=f"Da {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="whitelist", description="Annuncia esito whitelist")
async def whitelist(interaction: discord.Interaction, utente: discord.Member, esito: str, motivo: str = ""):
    color = 0x2ecc71 if "approv" in esito.lower() else 0xe74c3c
    embed = discord.Embed(title="📝 ESITO WHITELIST", description=f"**Utente:** {utente.mention}\n**Esito:** **{esito}**\n**Motivazione:** {motivo}", color=color)
    await interaction.response.send_message(content=utente.mention, embed=embed)

@bot.tree.command(name="bando", description="Annuncia un ban")
async def bando(interaction: discord.Interaction, utente: discord.Member, motivo: str, durata: str, prova: str = "Allegata"):
    embed = discord.Embed(title="🔨 BANDO UFFICIALE - ECLISSI RP", description=f"**Utente Bannato:** {utente.mention} ({utente.id})\n**Motivo:** {motivo}\n**Durata:** {durata}\n**Prova:** {prova}", color=0xff0000)
    embed.set_footer(text=f"Bannato da {interaction.user.display_name}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ticket-panel", description="[ADMIN] Pannello ticket con AI")
async def ticket_panel(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Solo admin!", ephemeral=True)
        return
    embed = discord.Embed(
        title="🎫 CENTRO ASSISTENZA - ECLISSI RP",
        description="**Benvenuto nel supporto di Eclissi RP!**\n\nSeleziona dal menu qui sotto il tipo di problema.\n\nSi aprirà un ticket dove troverai il nostro **Assistente IA** che proverà ad aiutarti subito.\n\n**Se l'IA non ti aiuta, clicca il bottone ROSSO per chiamare lo STAFF UMANO che ti pingherà subito.**",
        color=0x5865F2
    )
    await interaction.response.send_message(embed=embed, view=TicketView())

bot.run(os.getenv("TOKEN"))