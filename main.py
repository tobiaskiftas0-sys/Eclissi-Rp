import discord
from discord.ext import commands
from discord import app_commands

TOKEN = "METTI_TOKEN"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# ---------- MODAL CON DOMANDE ----------

class CittadinanzaModal(discord.ui.Modal, title="Richiesta Cittadinanza"):
    nome_ic = discord.ui.TextInput(label="Nome e Cognome IC", placeholder="Es. Luca Bianchi")
    data_nascita = discord.ui.TextInput(label="Data di nascita e Luogo IC", placeholder="Es. 01/01/2000 Hamburg")
    lavoro = discord.ui.TextInput(label="Che lavoro vuoi fare a Hamburg?", placeholder="Polizia, Medico, Meccanico...", style=discord.TextStyle.paragraph)
    background = discord.ui.TextInput(label="Breve storia del tuo PG (Background)", style=discord.TextStyle.paragraph, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📄 Nuova Richiesta Cittadinanza", color=0x00ff00)
        embed.add_field(name="Utente Discord", value=interaction.user.mention, inline=False)
        embed.add_field(name="Nome IC", value=self.nome_ic.value, inline=True)
        embed.add_field(name="Nascita IC", value=self.data_nascita.value, inline=True)
        embed.add_field(name="Lavoro Desiderato", value=self.lavoro.value, inline=False)
        embed.add_field(name="Background", value=self.background.value or "Non specificato", inline=False)
        embed.set_footer(text=f"ID: {interaction.user.id}")
        await interaction.channel.send(embed=embed, view=ApprovazioneView())
        await interaction.response.send_message("✅ Richiesta di cittadinanza inviata! Attendi la risposta dello staff.", ephemeral=True)

class PortoArmiModal(discord.ui.Modal, title="Richiesta Porto d'Armi"):
    nome_ic = discord.ui.TextInput(label="Nome e Cognome IC", placeholder="Es. Luca Bianchi")
    fedina = discord.ui.TextInput(label="Hai precedenti penali? (SI/NO)", placeholder="Se SI, quali?")
    tipo_arma = discord.ui.TextInput(label="Che tipo di arma vuoi? (Leggera/Pesante)", placeholder="Es. Pistola leggera")
    motivo = discord.ui.TextInput(label="Perchè vuoi il porto d'armi? (Motivo RP)", style=discord.TextStyle.paragraph, placeholder="Es. Mi serve per difesa personale...")

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🔫 Nuova Richiesta Porto d'Armi", color=0xffa500)
        embed.add_field(name="Utente Discord", value=interaction.user.mention, inline=False)
        embed.add_field(name="Nome IC", value=self.nome_ic.value, inline=True)
        embed.add_field(name="Fedina Penale", value=self.fedina.value, inline=True)
        embed.add_field(name="Tipo Arma", value=self.tipo_arma.value, inline=True)
        embed.add_field(name="Motivo RP", value=self.motivo.value, inline=False)
        embed.set_footer(text=f"ID: {interaction.user.id}")
        await interaction.channel.send(embed=embed, view=ApprovazioneView())
        await interaction.response.send_message("✅ Richiesta porto d'armi inviata alla Polizia!", ephemeral=True)

# ---------- VIEW CON BOTTONI ----------

class ApprovazioneView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="✅ Approva", style=discord.ButtonStyle.green, custom_id="approva")
    async def approva(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"Richiesta approvata da {interaction.user.mention} ✅")
    @discord.ui.button(label="❌ Rifiuta", style=discord.ButtonStyle.red, custom_id="rifiuta")
    async def rifiuta(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"Richiesta rifiutata da {interaction.user.mention} ❌")

class CittadinanzaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="📄 Richiedi Cittadinanza", style=discord.ButtonStyle.green, custom_id="btn_cittadinanza")
    async def cittadinanza_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CittadinanzaModal())

class PortoArmiView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="🔫 Richiedi Porto d'Armi", style=discord.ButtonStyle.blurple, custom_id="btn_porto")
    async def porto_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PortoArmiModal())

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="🎫 Apri Ticket RP - IA", style=discord.ButtonStyle.green, custom_id="ticket_rp")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        channel = await interaction.guild.create_text_channel(f"ticket-{interaction.user.name}", overwrites=overwrites)
        embed = discord.Embed(title="Ticket RP - IA Intelligente", description=f"Ciao {interaction.user.mention}, sono l'IA di Emergency Hamburg.\nSpiega il tuo problema in RP.", color=0x2b2d31)
        await channel.send(embed=embed)
        await interaction.response.send_message(f"Ticket aperto: {channel.mention}", ephemeral=True)

# ---------- COMANDI SLASH / ----------

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot online {bot.user}")

@bot.tree.command(name="setup_cittadinanza", description="Crea pannello con bottone cittadinanza")
async def setup_cittadinanza(interaction: discord.Interaction):
    embed = discord.Embed(title="📄 CITTADINANZA - Emergency Hamburg", description="Vuoi diventare cittadino di Hamburg?\nClicca il bottone qui sotto e compila il modulo con le domande RP!", color=0x00ff00)
    await interaction.channel.send(embed=embed, view=CittadinanzaView())
    await interaction.response.send_message("Pannello cittadinanza creato!", ephemeral=True)

@bot.tree.command(name="setup_porto_armi", description="Crea pannello con bottone porto d'armi")
async def setup_porto_armi(interaction: discord.Interaction):
    embed = discord.Embed(title="🔫 PORTO D'ARMI - Polizia Hamburg", description="Vuoi richiedere il porto d'armi?\nClicca il bottone e rispondi alle domande per la richiesta!", color=0xffa500)
    await interaction.channel.send(embed=embed, view=PortoArmiView())
    await interaction.response.send_message("Pannello porto d'armi creato!", ephemeral=True)

@bot.tree.command(name="setup_ticket", description="Crea pannello ticket IA")
async def setup_ticket(interaction: discord.Interaction):
    embed = discord.Embed(title="🚨 Supporto Emergency Hamburg RP", description="Apri un ticket, l'IA RP ti aiuta", color=0x2b2d31)
    await interaction.channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message("Pannello ticket creato!", ephemeral=True)

@bot.tree.command(name="annuncio", description="Fai un annuncio ufficiale")
async def annuncio(interaction: discord.Interaction, titolo: str, descrizione: str):
    embed = discord.Embed(title=f"📢 {titolo}", description=descrizione, color=0xff0000)
    embed.set_footer(text=f"Annuncio di {interaction.user.name}")
    await interaction.channel.send(content="@everyone", embed=embed)
    await interaction.response.send_message("Annuncio inviato!", ephemeral=True)

@bot.tree.command(name="bando_staff", description="Bando staff Emergency Hamburg")
async def bando_staff(interaction: discord.Interaction):
    await interaction.response.send_modal(BandoStaffModal())

# Bando modal veloce
class BandoStaffModal(discord.ui.Modal, title="Bando Staff"):
    nome = discord.ui.TextInput(label="Nome IC / Età")
    exp = discord.ui.TextInput(label="Esperienza RP", style=discord.TextStyle.paragraph)
    perche = discord.ui.TextInput(label="Perchè staff?", style=discord.TextStyle.paragraph)
    async def on_submit(self, interaction: discord.Interaction):
        e = discord.Embed(title="BANDO STAFF", color=0xff0000)
        e.description = f"**Utente:** {interaction.user.mention}\n**Nome:** {self.nome.value}\n**Exp:** {self.exp.value}\n**Motivo:** {self.perche.value}"
        await interaction.channel.send(embed=e)
        await interaction.response.send_message("Inviato!", ephemeral=True)

bot.run(TOKEN)