import discord
from discord.ui import View, Select, Modal, TextInput, Button
from minigames_data import MINIGAMES_RATES
from config import CATEGORY_TICKET_ID


# ---------------- Minigame Start ----------------
class MinigamesStartView(View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=None)
        self.user = user
        self.add_item(MinigameSelect(user))


class MinigameSelect(Select):
    def __init__(self, user: discord.User):
        self.user = user
        games = sorted(set(name.split(" - ")[0] for name in MINIGAMES_RATES))
        options = [
            discord.SelectOption(label=g, description=f"View methods for {g}")
            for g in games
        ]
        super().__init__(placeholder="Select a minigame...", options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_game = self.values[0]
        methods = {
            k: v
            for k, v in MINIGAMES_RATES.items()
            if k.startswith(selected_game)
        }

        embed = discord.Embed(
            title=f"🎮 {selected_game} Methods",
            description="Select a specific method or item below:",
            color=discord.Color.gold(),
        )

        await interaction.response.edit_message(
            embed=embed,
            view=MinigameMethodView(self.user, selected_game, methods),
        )


# ---------------- Method Selection ----------------
class MinigameMethodView(View):
    def __init__(self, user: discord.User, game_name: str, methods: dict):
        super().__init__(timeout=None)
        self.user = user
        self.game_name = game_name
        self.methods = methods
        self.add_item(MinigameMethodSelect(user, game_name, methods))


class MinigameMethodSelect(Select):
    def __init__(self, user: discord.User, game_name: str, methods: dict):
        self.user = user
        self.game_name = game_name
        self.methods = methods

        options = []
        for method, (price_pkr, price_usd) in methods.items():
            label = method.replace(f"{game_name} - ", "")
            options.append(
                discord.SelectOption(
                    label=label, description=f"{price_pkr} PKR ({price_usd})"
                )
            )

        super().__init__(placeholder="Choose method/item...", options=options)

    async def callback(self, interaction: discord.Interaction):
        method_label = self.values[0]
        full_name = (
            f"{self.game_name} - {method_label}"
            if f"{self.game_name} - {method_label}" in self.methods
            else method_label
        )

        price_pkr, price_usd = self.methods.get(full_name, (0, "$0.00"))
        if price_pkr == 0:
            await interaction.response.send_message(
                "❌ No price data found for this item.", ephemeral=True
            )
            return

        await interaction.response.send_modal(
            MinigameAmountModal(self.user, full_name, price_pkr, price_usd)
        )


# ---------------- Quantity Modal ----------------
class MinigameAmountModal(Modal):
    def __init__(self, user: discord.User, method: str, price_pkr: float, price_usd: str):
        super().__init__(title="Enter Quantity")
        self.user = user
        self.method = method
        self.price_pkr = price_pkr
        self.price_usd = price_usd

        self.quantity = TextInput(
            label="How many points/items?",
            placeholder="e.g. 500",
            required=True,
        )
        self.add_item(self.quantity)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            qty = float(self.quantity.value)
            total_pkr = self.price_pkr * qty
            total_usd = float(self.price_usd.strip("$")) * qty
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error: {str(e)}", ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"🎮 {self.method}",
            description=(
                f"**Unit Price:** {self.price_pkr} PKR ({self.price_usd})\n"
                f"**Quantity:** {qty}\n\n"
                f"💰 **Total:** {total_pkr:,.0f} PKR (${total_usd:,.2f} USD)"
            ),
            color=discord.Color.gold(),
        )
        embed.set_footer(text="Click below to create a ticket for your order.")

        await interaction.response.send_message(
            embed=embed,
            view=CreateTicketView(
                self.user, self.method, qty, total_pkr, total_usd
            ),
            ephemeral=True,
        )


# ---------------- Ticket Creation ----------------
class CreateTicketView(View):
    def __init__(self, user: discord.User, method: str, qty: float, total_pkr: float, total_usd: float):
        super().__init__(timeout=None)
        self.user = user
        self.method = method
        self.qty = qty
        self.total_pkr = total_pkr
        self.total_usd = total_usd

    @discord.ui.button(label="🎟 Create Ticket", style=discord.ButtonStyle.success)
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, id=CATEGORY_TICKET_ID)

        if not category:
            category = await guild.create_category("Tickets")

        channel = await guild.create_text_channel(
            name=f"ticket-{self.user.name.lower()}",
            category=category,
            topic=f"Minigame Order for {self.user.name}",
        )
        await channel.set_permissions(self.user, view_channel=True, send_messages=True)

        embed = discord.Embed(
            title=f"🎮 Minigame Order - {self.method}",
            description=(
                f"**Customer:** {self.user.mention}\n"
                f"**Quantity:** {self.qty}\n"
                f"**Total:** {self.total_pkr:,.0f} PKR (${self.total_usd:,.2f})\n\n"
                "Staff will contact you soon!"
            ),
            color=discord.Color.dark_gold(),
        )

        await channel.send(embed=embed, view=TicketControlView(self.user))
        await interaction.response.send_message("✅ Ticket created successfully!", ephemeral=True)


# ---------------- Ticket Controls ----------------
class TicketControlView(View):
    def __init__(self, owner: discord.Member):
        super().__init__(timeout=None)
        self.owner = owner
        self.add_item(CloseButton(self.owner))


class CloseButton(Button):
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

    @discord.ui.button(label="✅ Yes", style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()  # ✅ tell Discord we're processing it
        try:
            await interaction.message.delete()
        except discord.NotFound:
            pass

        await interaction.channel.set_permissions(self.owner, send_messages=False, view_channel=False)
        await interaction.channel.edit(name=f"closed-{self.owner.name.lower()}")

        embed = discord.Embed(
            title="🎮 Ticket Closed",
            description=f"Ticket closed by {interaction.user.mention}\nStaff options below:",
            color=discord.Color.dark_gold(),
        )

        await interaction.channel.send(embed=embed, view=AfterCloseView(self.owner))

    @discord.ui.button(label="❌ No", style=discord.ButtonStyle.gray)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("❌ Ticket closure cancelled.", ephemeral=True)


class AfterCloseView(View):
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
        await interaction.channel.set_permissions(self.owner, view_channel=True, send_messages=True)
        await interaction.channel.edit(name=f"ticket-{self.owner.name.lower()}")
        await interaction.response.send_message("✅ Ticket reopened.", ephemeral=True)


class TranscriptButton(Button):
    def __init__(self):
        super().__init__(label="📜 Transcript", style=discord.ButtonStyle.blurple)

    async def callback(self, interaction: discord.Interaction):
        messages = []
        async for msg in interaction.channel.history(limit=None, oldest_first=True):
            messages.append(f"[{msg.created_at}] {msg.author}: {msg.content}")

        transcript_text = "\n".join(messages)
        file = discord.File(fp=discord.utils._BytesIO(transcript_text.encode()), filename="transcript.txt")
        await interaction.user.send(file=file)
        await interaction.response.send_message("📜 Transcript sent to your DMs.", ephemeral=True)


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

    @discord.ui.button(label="✅ Yes", style=discord.ButtonStyle.red)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.channel.delete()

    @discord.ui.button(label="❌ No", style=discord.ButtonStyle.gray)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("❌ Deletion canceled.", ephemeral=True)
