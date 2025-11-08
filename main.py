# main.py
import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import io
from flask import Flask
from threading import Thread

# ---------------- Keep Alive ----------------
app = Flask('')

@app.route('/')
def home():
    return "I'm alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ---------------- Config ----------------
from config import (
    BOT_TOKEN,
    GUILD_ID,
    CATEGORY_TICKET_ID,
    ROLE_OWNER,
    ROLE_MODERATOR,
    ROLE_STAFF,
    TICKET_PREFIX,
)

# Panels
from quest_panel import RSNModal
from leveling_panel import LevelingStartView
from minigames_panel import MinigamesStartView
from bossing_panel import BossingStartView


# ---------- Utils ----------
def is_staff(member: discord.Member):
    return any(r.id in {ROLE_OWNER, ROLE_MODERATOR, ROLE_STAFF} for r in member.roles)


# ---------- Ticket Controls ----------
class CloseTicketButton(discord.ui.Button):
    def __init__(self, owner: discord.Member):
        super().__init__(style=discord.ButtonStyle.secondary, label="🔒 Close Ticket")
        self.owner = owner

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.owner.id and not is_staff(interaction.user):
            await interaction.response.send_message(
                "You don't have permission to close this ticket.", ephemeral=True
            )
            return

        view = ConfirmCloseView(self.owner)
        await interaction.response.send_message(
            "Are you sure you want to close this ticket?", view=view, ephemeral=True
        )


class ConfirmCloseView(discord.ui.View):
    def __init__(self, owner: discord.Member):
        super().__init__(timeout=30)
        self.owner = owner

    @discord.ui.button(label="✅ Yes", style=discord.ButtonStyle.success)
    async def confirm_yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.channel.set_permissions(self.owner, send_messages=False, view_channel=False)
        await interaction.channel.edit(name=f"closed-{self.owner.name.lower()}")

        await interaction.response.send_message(
            "✅ Ticket has been closed. Only staff can view it now.", ephemeral=True
        )

        staff_view = StaffAfterCloseView(self.owner)
        embed = discord.Embed(
            title="🎟 Ticket Closed",
            description=f"Ticket closed by {interaction.user.mention}\nStaff options below:",
            color=discord.Color.dark_grey(),
        )
        await interaction.channel.send(embed=embed, view=staff_view)

    @discord.ui.button(label="❌ No", style=discord.ButtonStyle.danger)
    async def confirm_no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Ticket close cancelled.", ephemeral=True)


class StaffAfterCloseView(discord.ui.View):
    def __init__(self, owner: discord.Member):
        super().__init__(timeout=None)
        self.owner = owner

    @discord.ui.button(label="🔓 Reopen Ticket", style=discord.ButtonStyle.primary)
    async def reopen_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_staff(interaction.user):
            await interaction.response.send_message("Only staff can reopen tickets.", ephemeral=True)
            return

        await interaction.channel.set_permissions(self.owner, view_channel=True, send_messages=True)
        await interaction.channel.edit(name=f"{TICKET_PREFIX}-{self.owner.name.lower()}")
        await interaction.response.send_message("🔓 Ticket reopened.", ephemeral=True)

    @discord.ui.button(label="🧾 Transcript", style=discord.ButtonStyle.secondary)
    async def transcript_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_staff(interaction.user):
            await interaction.response.send_message("Only staff can generate transcripts.", ephemeral=True)
            return

        messages = [f"--- Transcript for {interaction.channel.name} ---\n"]
        async for msg in interaction.channel.history(limit=None, oldest_first=True):
            messages.append(
                f"[{msg.created_at.strftime('%Y-%m-%d %H:%M:%S')}] {msg.author}: {msg.content}"
            )
        transcript_text = "\n".join(messages)

        file = discord.File(
            fp=io.BytesIO(transcript_text.encode()),
            filename=f"{interaction.channel.name}_transcript.txt",
        )
        await interaction.user.send(file=file)
        await interaction.response.send_message("🧾 Transcript sent to your DMs.", ephemeral=True)

    @discord.ui.button(label="❌ Delete Ticket", style=discord.ButtonStyle.danger)
    async def delete_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_staff(interaction.user):
            await interaction.response.send_message("Only staff can delete tickets.", ephemeral=True)
            return

        await interaction.response.send_message("Deleting ticket in 3 seconds...", ephemeral=True)
        await asyncio.sleep(3)
        await interaction.channel.delete(reason=f"Deleted by {interaction.user}")


class TicketControlView(discord.ui.View):
    def __init__(self, owner: discord.Member):
        super().__init__(timeout=None)
        self.add_item(CloseTicketButton(owner))


# ---------- Panel ----------
class PanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="💀 Bossing", style=discord.ButtonStyle.primary, custom_id="btn_bossing"))
        self.add_item(discord.ui.Button(label="🧙 Questing", style=discord.ButtonStyle.primary, custom_id="btn_questing"))
        self.add_item(discord.ui.Button(label="⚔️ Leveling", style=discord.ButtonStyle.primary, custom_id="btn_leveling"))
        self.add_item(discord.ui.Button(label="🎮 Minigames", style=discord.ButtonStyle.primary, custom_id="btn_minigames"))


# ---------- Bot Setup ----------
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID)) if GUILD_ID else await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Failed to sync: {e}")


# ---------- /panel command ----------
@bot.tree.command(name="panel", description="Open the OSRS Orders panel")
async def panel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="OSRS Orders Panel",
        description="Choose a service:",
        color=discord.Color.dark_teal(),
    )
    embed.add_field(name="💀 Bossing", value="Order Bossing services", inline=False)
    embed.add_field(name="🧙 Questing", value="Order quest completion services", inline=False)
    embed.add_field(name="⚔️ Leveling", value="Order leveling services", inline=False)
    embed.add_field(name="🎮 Minigames", value="Order minigame runs", inline=False)

    await interaction.response.send_message(embed=embed, view=PanelView())


# ---------- Button Interactions ----------
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if not interaction.type == discord.InteractionType.component:
        return

    cid = interaction.data.get("custom_id", "")

    # 🧙 Questing
    if cid == "btn_questing":
        await interaction.response.send_modal(RSNModal(interaction.user))

    # ⚔️ Leveling
    elif cid == "btn_leveling":
        embed = discord.Embed(
            title="⚔️ Leveling Services",
            description="Select a skill to view available methods:",
            color=discord.Color.dark_teal(),
        )
        await interaction.response.send_message(embed=embed, view=LevelingStartView(interaction.user), ephemeral=True)

    # 🎮 Minigames
    elif cid == "btn_minigames":
        embed = discord.Embed(
            title="🎮 Minigame Services",
            description="Select a minigame to begin:",
            color=discord.Color.dark_gold(),
        )
        await interaction.response.send_message(embed=embed, view=MinigamesStartView(interaction.user), ephemeral=True)

    # 💀 Bossing
    elif cid == "btn_bossing":
        embed = discord.Embed(
            title="💀 Bossing Services",
            description="Select a bossing category to begin (Slayer / Wilderness / Raids / Misc).",
            color=discord.Color.dark_red(),
        )
        await interaction.response.send_message(embed=embed, view=BossingStartView(interaction.user), ephemeral=True)

# ---------- Run Bot ----------
if __name__ == "__main__":
    keep_alive()  # ✅ keeps your bot 24/7 alive with UptimeRobot
    bot.run("MTQyMzc4Mzc1MTAxMTQwNTg2NQ.G6TwNj.8tjvH-mBWCA8NV3UAHJxHON7mDUC_Tv3vjKEy8")


