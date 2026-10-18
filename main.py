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
            ticket_channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites, reason=f"Ticket {scelta} di {interaction.user}")

            embed_ticket = discord.Embed(
                title="🎫 TICKET APERTO - ECLISSI RP",
                description=f"Ciao {interaction.user.mention}, grazie per aver contattato lo staff.\n\n**Categoria selezionata:** `{scelta}`\n\n**Spiega dettagliatamente il tuo problema qui sotto.** Un membro dello staff ti risponderà il prima possibile.\n\n> ⏳ Non menzionare lo staff, verrai assistito in ordine di arrivo.\n> 📸 Se necessario, invia screen o video.",
                color=0x5865F2
            )
            embed_ticket.add_field(name="👤 Utente", value=interaction.user.mention, inline=True)
            embed_ticket.add_field(name="📂 Categoria", value=scelta, inline=True)
            embed_ticket.set_footer(text="Eclissi RP • Sistema di Supporto", icon_url=guild.icon.url if guild.icon else None)

            await ticket_channel.send(content=f"{interaction.user.mention}", embed=embed_ticket, view=CloseView())
            await interaction.response.send_message(f"✅ Ticket creato con successo in {ticket_channel.mention} - Categoria: **{scelta}**", ephemeral=True)
        except Exception as e:
            print(f"ERRORE TICKET: {e}")
            await interaction.response.send_message(f"❌ Errore nella creazione del ticket: {e}", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

class CloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="Chiudi Ticket", style=discord.ButtonStyle.red, emoji="🔒", custom_id="close_ticket")
    async def callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 Il ticket verrà chiuso in 3 secondi...")
        await asyncio.sleep(3)
        try:
            await interaction.channel.delete(reason=f"Ticket chiuso da {interaction.user}")
        except:
            pass

@bot.event
async def on_ready():
    print(f"BOT ONLINE {bot.user}")
    bot.add_view(TicketView())
    bot.add_view(CloseView())
    await bot.tree.sync()
    print("Comandi sincronizzati!")

# --- SSU LUNGO E PROFESSIONALE CON CODICE ---
@bot.tree.command(name="ssu", description="Annuncia l'apertura del server (SSU)")
async def ssu(interaction: discord.Interaction, codice_server: str, ip_server: str = "Non specificato"):
    embed = discord.Embed(
        title="🟢 ECLISSI ROLEPLAY - SERVER START UP",
        description=(
            f"**Cittadini di Eclissi, la città apre le sue porte!**\n\n"
            f"Siamo lieti di annunciarvi che il server è ora **UFFICIALMENTE APERTO** e pronto ad accogliervi per una nuova, intensa giornata di RolePlay.\n\n"
            f"Il nostro staff ha lavorato per garantirvi la migliore esperienza possibile. Preparatevi a scrivere la vostra storia!\n\n"
            f"**━━━━━━━━━━━━━━━━━━━━━━━━━━**\n"
            f"**📡 INFORMAZIONI DI CONNESSIONE**\n"
            f"**━━━━━━━━━━━━━━━━━━━━━━━━━━**\n\n"
            f"🔹 **Codice Server:**\n```{codice_server}```\n"
            f"🔹 **Indirizzo IP / F8 Connect:**\n```connect {ip_server}```\n"
            f"🔹 **Metodo Alternativo:**\n> Apri F8 in gioco e scrivi `{codice_server}`\n\n"
            f"**━━━━━━━━━━━━━━━━━━━━━━━━━━**\n"
            f"**📜 REGOLE FONDAMENTALI**\n"
            f"**━━━━━━━━━━━━━━━━━━━━━━━━━━**\n\n"
            f"• Rispetta il regolamento e lo staff\n"
            f"• Mantieni un RolePlay serio e di qualità\n"
            f"• Divertiti e crea la tua storia unica\n\n"
            f"Vi aspettiamo numerosi in città, buon divertimento a tutti!\n"
        ),
        color=0x2ecc71
    )
    if interaction.guild.icon:
        embed.set_thumbnail(url=interaction.guild.icon.url)
    embed.set_footer(text="Eclissi RP • Buon divertimento!", icon_url=interaction.user.display_avatar.url)
    
    await interaction.response.send_message(content="@everyone", embed=embed)

# --- SSD LUNGO E PROFESSIONALE ---
@bot.tree.command(name="ssd", description="Annuncia la chiusura del server (SSD)")
async def ssd(interaction: discord.Interaction, motivo: str, riapertura: str = "Verrà comunicata a breve"):
    embed = discord.Embed(
        title="🔴 ECLISSI ROLEPLAY - SERVER SHUT DOWN",
        description=(
            f"**Attenzione a tutti i cittadini di Eclissi.**\n\n"
            f"Vi informiamo che la città è stata **TEMPORANEAMENTE CHIUSA** e il server è ora in stato di **SHUTDOWN**.\n\n"
            f"**━━━━━━━━━━━━━━━━━━━━━━━━━━**\n"
            f"**📋 MOTIVO DELLA CHIUSURA**\n"
            f"**━━━━━━━━━━━━━━━━━━━━━━━━━━**\n\n"
            f"> {motivo}\n\n"
            f"**━━━━━━━━━━━━━━━━━━━━━━━━━━**\n"
            f"**⏰ RIAPERTURA**\n"
            f"**━━━━━━━━━━━━━━━━━━━━━━━━━━**\n\n"
            f"**Orario Previsto:** {riapertura}\n\n"
            f"La riapertura verrà annunciata ufficialmente tramite un nuovo annuncio di **SSU**. Vi invitiamo a restare sintonizzati in questo canale.\n\n"
            f"Ringraziamo tutti i player che hanno giocato con noi oggi. È stato un piacere avervi in città e non vediamo l'ora di rivedervi alla prossima apertura per continuare le vostre storie!\n"
        ),
        color=0xe74c3c
    )
    if interaction.guild.icon:
        embed.set_thumbnail(url=interaction.guild.icon.url)
    embed.set_footer(text="Eclissi RP • A presto!", icon_url=interaction.user.display_avatar.url)

    await interaction.response.send_message(content="@everyone", embed=embed)

# --- ANNUNCIO E TICKET PANNELLO ---
@bot.tree.command(name="annuncio", description="Invia un annuncio ufficiale")
async def annuncio(interaction: discord.Interaction, testo: str):
    embed = discord.Embed(title="📢 ANNUNCIO UFFICIALE - ECLISSI RP", description=testo, color=0x3498db)
    embed.set_footer(text=f"Annuncio di {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ticket-panel", description="[ADMIN] Manda il pannello ticket professionale")
async def ticket_panel(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Solo gli admin possono usare questo comando!", ephemeral=True)
        return

    embed = discord.Embed(
        title="🎫 CENTRO ASSISTENZA - ECLISSI RP",
        description=(
            "**Benvenuto nel centro di supporto ufficiale di Eclissi RP!**\n\n"
            "Il nostro staff è a tua completa disposizione per qualsiasi problema o informazione. Per ricevere assistenza, seleziona dal **menu qui sotto** la categoria più adatta al tuo problema.\n\n"
            "**━━━━━━━━━━━━━━━━━━━━**\n"
            "**📂 CATEGORIE DISPONIBILI**\n"
            "**━━━━━━━━━━━━━━━━━━━━**\n\n"
            "🎫 **Supporto Generale**\n> Per domande generiche e informazioni\n\n"
            "🚨 **Segnalazione Player**\n> Per segnalare un player scorretto o un cheater\n\n"
            "📝 **Whitelist**\n> Per problemi con la whitelist o l'accesso\n\n"
            "🐛 **Bug & Problemi Tecnici**\n> Per segnalare bug, crash o problemi tecnici\n\n"
            "💎 **Staff & Donazioni**\n> Per candidature staff, donazioni e partnership\n\n"
            "**━━━━━━━━━━━━━━━━━━━━**\n"
            "_⚠️ **ATTENZIONE:** Aprire ticket senza motivo valido o abusare del sistema comporterà sanzioni._"
        ),
        color=0x5865F2
    )
    if interaction.guild.icon:
        embed.set_thumbnail(url=interaction.guild.icon.url)
    
    await interaction.response.send_message(embed=embed, view=TicketView())

bot.run(os.getenv("TOKEN"))