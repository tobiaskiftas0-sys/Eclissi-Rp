import discord
from discord.ext import commands
import os
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)

STAFF_ROLE_NAME = "Staff"

# --- TICKET SYSTEM ---
class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Supporto Generale", emoji="🛠️", description="Info, domande generiche"),
            discord.SelectOption(label="Supporto In-Game", emoji="🎮", description="Problemi in città, item, veicoli"),
            discord.SelectOption(label="Segnalazione Bug", emoji="🐛", description="Segnala bug con prove"),
            discord.SelectOption(label="Richiesta Fondazione", emoji="🏢", description="Fondare azienda/gang/org"),
            discord.SelectOption(label="Richiesta Gradi Alti", emoji="⭐", description="Gradi alti LSPD/EMS/Meccanici"),
            discord.SelectOption(label="Porto d'Armi", emoji="🔫", description="Richiesta porto d'armi"),
        ]
        super().__init__(placeholder="📩 Seleziona motivo ticket...", options=options, custom_id="ticket_final_v4")

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user
        label = self.values[0]

        for ch in guild.text_channels:
            if ch.topic and str(user.id) in ch.topic:
                await interaction.response.send_message(f"Hai già un ticket: {ch.mention}", ephemeral=True)
                return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        staff_role = discord.utils.get(guild.roles, name=STAFF_ROLE_NAME)
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        channel = await guild.create_text_channel(f"ticket-{user.name}", overwrites=overwrites, topic=f"{user.id} | {label}")
        
        embed = discord.Embed(title=f"🎫 {label}", description=f"{user.mention} Descrivi il problema con prove.\n**Tipo:** {label}", color=0x5865F2)
        ping = staff_role.mention if staff_role else "@Staff"
        await channel.send(content=f"{ping} Nuovo ticket {label} - {user.mention}", embed=embed, view=CloseView())
        await interaction.response.send_message(f"Ticket creato: {channel.mention} ✅", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

class CloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="🔒 Chiudi Ticket", style=discord.ButtonStyle.red, custom_id="close_final_v4")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.channel.delete(reason=f"Chiuso da {interaction.user}")

# --- COMANDI ---
@bot.tree.command(name="ticket", description="Pannellone ticket Eclissi")
@commands.has_permissions(administrator=True)
async def ticket_panel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎫 ECLISSI RP - ASSISTENZA",
        description="**Hai bisogno di aiuto? Seleziona dal menu:**\n\n🛠️ Supporto Generale\n🎮 Supporto In-Game\n🐛 Segnalazione Bug\n🏢 Richiesta Fondazione\n⭐ Richiesta Gradi Alti\n🔫 Porto d'Armi\n\n👇 Seleziona per aprire",
        color=0x2b2d31
    )
    if interaction.guild.icon:
        embed.set_thumbnail(url=interaction.guild.icon.url)
    await interaction.channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message("Inviato ✅", ephemeral=True)

@bot.tree.command(name="ssu", description="SSU lungo")
async def ssu(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🟢 ECLISSI RP - SERVER APERTO [SSU]",
        description="**@everyone LA CITTÀ È APERTA!**\n\n📥 **F8:** Eclissi RP\n📜 Leggi regolamento in #regolamento\n📍 Cittadinanza in Comune\n💼 Lavoro al Centro Impiego\n\n**RP serio - No RDM/VDM/Meta**\nStaff online!\nBuon RP!",
        color=0x00ff00
    )
    await interaction.response.send_message(content="@everyone", embed=embed)

@bot.tree.command(name="ssd", description="SSD lungo")
async def ssd(interaction: discord.Interaction, motivo: str = "Riavvio / Manutenzione"):
    embed = discord.Embed(
        title="🔴 ECLISSI RP - SERVER CHIUSO [SSD]",
        description=f"**@everyone SERVER CHIUSO**\n\n**Motivo:** {motivo}\n\n• Dati salvati\n• Non entrare\n• Resta in Discord per prossimo SSU\n\n**- Staff Eclissi RP**",
        color=0xff0000
    )
    await interaction.response.send_message(content="@everyone", embed=embed)

@bot.tree.command(name="portodarmi", description="Annuncio porto d'armi")
async def portodarmi(interaction: discord.Interaction, stato: str):
    color = 0x00ff00 if "apert" in stato.lower() else 0xff0000
    embed = discord.Embed(
        title=f"🔫 PORTO D'ARMI {stato.upper()}",
        description=f"**@everyone PORTO D'ARMI {stato.upper()}**\n\n📍 Armeria / Commissariato\n💰 $15.000\n📋 Requisiti: Cittadinanza + Fedina Pulita\n\nRecati in armeria ORA se APERTO!",
        color=color
    )
    await interaction.response.send_message(content="@everyone", embed=embed)

@bot.tree.command(name="annuncio", description="Annuncio lungo custom")
async def annuncio(interaction: discord.Interaction, titolo: str, descrizione: str):
    embed = discord.Embed(title=f"📢 {titolo.upper()}", description=descrizione, color=0x2b2d31, timestamp=datetime.now())
    embed.set_footer(text=f"Di {interaction.user.display_name}")
    await interaction.response.send_message(content="@everyone", embed=embed)

@bot.event
async def on_ready():
    print(f"ONLINE {bot.user}")
    bot.add_view(TicketView())
    bot.add_view(CloseView())
    await bot.tree.sync()

bot.run(os.getenv("TOKEN"))