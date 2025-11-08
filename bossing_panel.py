# bossing_panel.py
import io
import discord
from discord.ui import View, Select, Modal, TextInput, Button
from config import CATEGORY_TICKET_ID
from bossing_data import BOSSING_RATES

# ---------------- Helper ----------------
def format_currency(pkr):
    try:
        return f"{pkr:,.0f} PKR"
    except Exception:
        return f"{pkr} PKR"

def usd_from_string(usd_str):
    try:
        return float(usd_str.strip().strip("$"))
    except Exception:
        return 0.0

# ---------------- Start View ----------------
class BossingStartView(View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=None)
        self.user = user
        self.add_item(CategorySelect(user))

class CategorySelect(Select):
    def __init__(self, user: discord.User):
        self.user = user
        categories = list(BOSSING_RATES.keys())
        options = [discord.SelectOption(label=c, description=f"View {c}") for c in categories]
        super().__init__(placeholder="Select a bossing category...", options=options)

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        bosses = BOSSING_RATES.get(category, {})
        embed = discord.Embed(
            title=f"💀 {category}",
            description="Choose a boss/service below:",
            color=discord.Color.dark_gold()
        )
        await interaction.response.edit_message(embed=embed, view=BossSelectView(self.user, category, bosses))

# ---------------- Boss Select ----------------
class BossSelectView(View):
    def __init__(self, user: discord.User, category: str, bosses: dict):
        super().__init__(timeout=None)
        self.user = user
        self.category = category
        self.bosses = bosses
        options = []
        for name, (pkr, usd) in bosses.items():
            label = name
            desc = f"{pkr} PKR" if pkr else "Open ticket for quote"
            if isinstance(usd, str) and usd != "$0.00":
                desc += f" ({usd})"
            options.append(discord.SelectOption(label=label, description=desc[:100]))
        options = options[:25]
        self.add_item(BossSelect(self.user, category, bosses, options))

class BossSelect(Select):
    def __init__(self, user: discord.User, category: str, bosses: dict, options):
        self.user = user
        self.category = category
        self.bosses = bosses
        super().__init__(placeholder="Select boss/service...", options=options)

    async def callback(self, interaction: discord.Interaction):
        selection = self.values[0]
        price_pkr, price_usd = self.bosses.get(selection, (0, "$0.00"))
        if price_pkr == 0:
            embed = discord.Embed(
                title=f"💬 {selection} - Quote Required",
                description="This service requires a manual quote. Click Create Ticket and staff will reply with a price.",
                color=discord.Color.orange()
            )
            await interaction.response.defer(ephemeral=True, thinking=False)
            await interaction.followup.send(
                embed=embed,
                view=CreateTicketView(self.user, selection, 0, 0.0, 0.0, quote=True),
                ephemeral=True
            )
            return

        await interaction.response.send_modal(
            BossQuantityModal(self.user, selection, price_pkr, price_usd)
        )

# ---------------- Quantity Modal ----------------
class BossQuantityModal(Modal):
    def __init__(self, user: discord.User, selection: str, price_pkr: float, price_usd: str):
        super().__init__(title="Enter Quantity / Runs")
        self.user = user
        self.selection = selection
        self.price_pkr = price_pkr
        self.price_usd = price_usd
        self.qty = TextInput(label="How many kills/runs/items?", placeholder="e.g. 10", required=True)
        self.add_item(self.qty)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            qty = float(self.qty.value)
        except Exception:
            await interaction.response.send_message("❌ Please enter a valid number.", ephemeral=True)
            return

        total_pkr = self.price_pkr * qty
        usd_unit = usd_from_string(self.price_usd)
        total_usd = usd_unit * qty

        embed = discord.Embed(
            title=f"💀 {self.selection}",
            description=(
                f"**Unit:** {format_currency(self.price_pkr)} ({self.price_usd})\n"
                f"**Quantity:** {qty:,}\n\n"
                f"💰 **Total:** {format_currency(total_pkr)} (${total_usd:,.2f} USD)"
            ),
            color=discord.Color.dark_gold()
        )
        embed.set_footer(text="Click below to create a ticket for this bossing order.")
        await interaction.response.send_message(embed=embed, view=CreateTicketView(self.user, self.selection, qty, total_pkr, total_usd), ephemeral=True)

# ---------------- Ticket Creation ----------------
class CreateTicketView(View):
    def __init__(self, user: discord.User, selection: str, qty: float, total_pkr: float, total_usd: float, quote: bool=False):
        super().__init__(timeout=None)
        self.user = user
        self.selection = selection
        self.qty = qty
        self.total_pkr = total_pkr
        self.total_usd = total_usd
        self.quote = quote

    @discord.ui.button(label="🎟 Create Ticket", style=discord.ButtonStyle.success)
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, id=CATEGORY_TICKET_ID)
        if not category:
            category = discord.utils.get(guild.categories, name="Tickets")
        if not category:
            category = await guild.create_category("Tickets")

        channel = await guild.create_text_channel(
            name=f"ticket-{self.user.name.lower()}",
            category=category,
            topic=f"Bossing order for {self.user.name}: {self.selection}",
        )
        await channel.set_permissions(self.user, view_channel=True, send_messages=True)

        if self.quote:
            desc = f"**Customer:** {self.user.mention}\n\nThis service requires a quote from staff. Please wait for staff to reply."
        else:
            desc = (
                f"**Customer:** {self.user.mention}\n"
                f"**Service:** {self.selection}\n"
                f"**Quantity:** {self.qty:,}\n"
                f"**Total:** {format_currency(self.total_pkr)} (${self.total_usd:,.2f} USD)\n\n"
                "Staff will contact you soon!"
            )

        embed = discord.Embed(
            title=f"💀 Bossing Order - {self.selection}",
            description=desc,
            color=discord.Color.dark_red() if "Firecape" in self.selection else discord.Color.dark_gold()
        )
        await channel.send(embed=embed, view=TicketControlView(self.user))
        await interaction.response.send_message(f"✅ Ticket created: {channel.mention}", ephemeral=True)

# ---------------- Ticket Controls ----------------
class TicketControlView(View):
    def __init__(self, owner: discord.Member):
        super().__init__(timeout=None)
        self.owner = owner
        self.add_item(CloseTicketButton(owner))

class CloseTicketButton(Button):
    def __init__(self, owner: discord.Member):
        super().__init__(label="🔒 Close Ticket", style=discord.ButtonStyle.red)
        self.owner = owner

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Are you sure you want to close this ticket?",
            view=CloseConfirmView(self.owner),
            ephemeral=True
        )

class CloseConfirmView(View):
    def __init__(self, owner: discord.Member):
        super().__init__(timeout=20)
        self.owner = owner

    @discord.ui.button(label="✅ Yes", style=discord.ButtonStyle.success)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        try:
            await interaction.message.delete()
        except discord.NotFound:
            pass

        try:
            await interaction.channel.set_permissions(self.owner, send_messages=False, view_channel=False)
            await interaction.channel.edit(name=f"closed-{self.owner.name.lower()}")
        except Exception:
            pass

        embed = discord.Embed(
            title="🔒 Ticket Closed",
            description=f"Ticket closed by {interaction.user.mention}\nStaff options below:",
            color=discord.Color.dark_gold()
        )
        await interaction.channel.send(embed=embed, view=StaffAfterCloseView(self.owner))

    @discord.ui.button(label="❌ No", style=discord.ButtonStyle.gray)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("❌ Ticket closure cancelled.", ephemeral=True)

class StaffAfterCloseView(View):
    def __init__(self, owner: discord.Member):
        super().__init__(timeout=None)
        self.owner = owner
        self.add_item(ReopenButton(owner))
        self.add_item(TranscriptButton())
        self.add_item(DeleteButton())

class ReopenButton(Button):
    def __init__(self, owner: discord.Member):
        super().__init__(label="🔓 Reopen Ticket", style=discord.ButtonStyle.green)
        self.owner = owner

    async def callback(self, interaction: discord.Interaction):
        try:
            await interaction.channel.set_permissions(self.owner, view_channel=True, send_messages=True)
            await interaction.channel.edit(name=f"ticket-{self.owner.name.lower()}")
        except Exception:
            pass
        await interaction.response.send_message("✅ Ticket reopened.", ephemeral=True)

class TranscriptButton(Button):
    def __init__(self):
        super().__init__(label="📜 Transcript", style=discord.ButtonStyle.blurple)

    async def callback(self, interaction: discord.Interaction):
        messages = []
        async for msg in interaction.channel.history(limit=None, oldest_first=True):
            messages.append(f"[{msg.created_at.isoformat()}] {msg.author}: {msg.content}")
        transcript = "\n".join(messages)
        bio = io.BytesIO(transcript.encode("utf-8"))
        file = discord.File(fp=bio, filename="transcript.txt")
        try:
            await interaction.user.send(file=file)
            await interaction.response.send_message("📜 Transcript sent to your DMs.", ephemeral=True)
        except Exception:
            await interaction.response.send_message("⚠️ Unable to DM transcript to you.", ephemeral=True)

class DeleteButton(Button):
    def __init__(self):
        super().__init__(label="❌ Delete Ticket", style=discord.ButtonStyle.red)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Are you sure you want to delete this ticket?",
            view=ConfirmDeleteView(),
            ephemeral=True
        )

class ConfirmDeleteView(View):
    def __init__(self):
        super().__init__(timeout=20)

    @discord.ui.button(label="✅ Yes", style=discord.ButtonStyle.danger)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.channel.delete()
        except Exception:
            pass

    @discord.ui.button(label="❌ No", style=discord.ButtonStyle.gray)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("❌ Deletion canceled.", ephemeral=True)
