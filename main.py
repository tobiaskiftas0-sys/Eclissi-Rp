import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="📩 Apri Ticket", style=discord.ButtonStyle.blurple, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        channel = await guild.create_text_channel(f"ticket-{interaction.user.name}", overwrites=overwrites)
        embed = discord.Embed(title="🎫 Ticket Aperto", description=f"{interaction.user.mention} lo staff ti risponderà a breve!", color=0x00ff00)
        await channel.send(embed=embed, view=CloseTicketView())
        await interaction.response.send_message(f"✅ Ticket creato: {channel.mention}", ephemeral=True)

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="🔒 Chiudi Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.channel.delete(reason="Ticket chiuso")

@bot.event
async def on_ready():
    print(f"ONLINE {bot.user}")
    bot.add_view(TicketView())
    bot.add_view(CloseTicketView())
    await bot.tree.sync()

@bot.tree.command(name="annuncio", description="Invia un annuncio ufficiale")
async def annuncio(interaction: discord.Interaction, testo: str):
    await interaction.response.defer(ephemeral=True)
    embed = discord.Embed(title="📢 ANNUNCIO UFFICIALE - ECLISSI RP", description=testo, color=0x2b2d31)
    await interaction.channel.send(embed=embed)
    await interaction.followup.send("✅ Annuncio inviato!", ephemeral=True)

@bot.tree.command(name="ssu", description="Annuncia apertura server")
async def ssu(interaction: discord.Interaction):
    embed = discord.Embed(title="🟢 SSU - SERVER APERTO", description="**Il server è ufficialmente APERTO!**\nEntra in città!", color=0x00ff00)
    await interaction.response.send_message(embed=embed, content="@everyone")

@bot.tree.command(name="ssd", description="Annuncia chiusura server")
async def ssd(interaction: discord.Interaction, motivo: str = "Riavvio"):
    embed = discord.Embed(title="🔴 SSD - SERVER CHIUSO", description=f"**Server CHIUSO.**\nMotivo: {motivo}", color=0xff0000)
    await interaction.response.send_message(embed=embed, content="@everyone")

@bot.tree.command(name="ticket", description="Manda pannello ticket")
@commands.has_permissions(administrator=True)
async def ticket_panel(interaction: discord.Interaction):
    embed = discord.Embed(title="🎫 SUPPORTO - ECLISSI RP", description="Clicca qui sotto per aprire un ticket privato con lo staff.", color=0x5865F2)
    await interaction.channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message("✅ Pannello inviato!", ephemeral=True)

bot.run(os.getenv("TOKEN"))