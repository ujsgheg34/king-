# quest_panel.py
import discord
import math
import asyncio
from config import (
    CATEGORY_TICKET_ID,
    ROLE_OWNER,
    ROLE_MODERATOR,
    ROLE_STAFF,
    TICKET_PREFIX,
)
from quests_data import QUESTS

# ---------- Utilities ----------
QUEST_NAMES = sorted(QUESTS.keys(), key=lambda s: s.lower())


def calc_total(selected_names):
    total_pkr = 0
    total_usd = 0.0
    for name in selected_names:
        pkr, usd = QUESTS.get(name, (0, 0.0))
        if isinstance(usd, str):
            usd = float(usd.replace("$", "").strip())
        total_pkr += pkr
        total_usd += usd
    return total_pkr, round(total_usd, 2)


def is_staff(member: discord.Member):
    return any(r.id in {ROLE_OWNER, ROLE_MODERATOR, ROLE_STAFF}
               for r in member.roles)


# ---------- RSN Modal ----------
class RSNModal(discord.ui.Modal, title="Enter your RuneScape Name (RSN)"):
    rsn = discord.ui.TextInput(label="RSN",
                               placeholder="Your RuneScape username",
                               max_length=32)

    def __init__(self, user: discord.User):
        super().__init__()
        self.user = user

    async def on_submit(self, interaction: discord.Interaction):
        view = QuestSelectionView(self.user, self.rsn.value)
        embed = discord.Embed(
            title="Select Quests",
            description=
            "Use the dropdown to select quests. Use arrows to paginate.\nWhen ready, press **Confirm Order**.",
            color=discord.Color.blurple(),
        )
        await interaction.response.send_message(embed=embed,
                                                view=view,
                                                ephemeral=True)


# ---------- Quest Selection ----------
class QuestSelect(discord.ui.Select):

    def __init__(self, options):
        super().__init__(placeholder="Select quests (max 25)",
                         min_values=0,
                         max_values=len(options),
                         options=options)


class QuestSelectionView(discord.ui.View):

    def __init__(self, user: discord.User, rsn: str, *, timeout=300):
        super().__init__(timeout=timeout)
        self.user = user
        self.rsn = rsn
        self.page = 0
        self.per_page = 25
        self.selected = []
        self._update_select_for_page()
        self.add_item(PrevPageButton(self))
        self.add_item(NextPageButton(self))
        self.add_item(ConfirmOrderButton(self))

    def _get_page_items(self):
        start = self.page * self.per_page
        return QUEST_NAMES[start:start + self.per_page]

    def _update_select_for_page(self):
        for child in list(self.children):
            if isinstance(child, discord.ui.Select):
                self.remove_item(child)
        page_items = self._get_page_items()
        options = [
            discord.SelectOption(label=name,
                                 description=f"PKR {pkr} • USD {usd}")
            for name, (pkr, usd) in QUESTS.items() if name in page_items
        ]
        select = QuestSelect(options)
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        values = interaction.data.get("values", []) if interaction.data else []
        page_items = set(self._get_page_items())
        self.selected = [s for s in self.selected if s not in page_items]
        self.selected.extend(values)
        total_pkr, total_usd = calc_total(self.selected)
        embed = discord.Embed(title="Order Preview — Questing",
                              color=discord.Color.green())
        embed.add_field(name="RSN", value=self.rsn)
        embed.add_field(name="Selected Quests",
                        value="\n".join(self.selected)
                        if self.selected else "No quests selected",
                        inline=False)
        embed.add_field(name="Total Price",
                        value=f"PKR {total_pkr} • USD {total_usd}")
        embed.set_footer(text="Press Confirm Order when ready.")
        await interaction.response.edit_message(embed=embed, view=self)

    async def interaction_check(self,
                                interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "This is not your session.", ephemeral=True)
            return False
        return True


# ---------- Pagination ----------
class PrevPageButton(discord.ui.Button):

    def __init__(self, view):
        super().__init__(style=discord.ButtonStyle.secondary,
                         label="◀ Prev",
                         row=1)
        self.parent_view = view

    async def callback(self, interaction: discord.Interaction):
        if self.parent_view.page > 0:
            self.parent_view.page -= 1
            self.parent_view._update_select_for_page()
            await interaction.response.edit_message(view=self.parent_view)
        else:
            await interaction.response.defer()


class NextPageButton(discord.ui.Button):

    def __init__(self, view):
        super().__init__(style=discord.ButtonStyle.secondary,
                         label="Next ▶",
                         row=1)
        self.parent_view = view

    async def callback(self, interaction: discord.Interaction):
        max_page = math.ceil(len(QUEST_NAMES) / self.parent_view.per_page) - 1
        if self.parent_view.page < max_page:
            self.parent_view.page += 1
            self.parent_view._update_select_for_page()
            await interaction.response.edit_message(view=self.parent_view)
        else:
            await interaction.response.defer()


# ---------- Confirm Order ----------
class ConfirmOrderButton(discord.ui.Button):

    def __init__(self, parent_view):
        super().__init__(style=discord.ButtonStyle.success,
                         label="✅ Confirm Order",
                         row=2)
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        if not self.parent_view.selected:
            await interaction.response.send_message(
                "Select at least one quest!", ephemeral=True)
            return

        guild = interaction.guild
        author = interaction.user
        ticket_name = f"{TICKET_PREFIX}-{author.name.lower()}"
        existing = discord.utils.get(guild.text_channels, name=ticket_name)
        counter = 1
        while existing:
            ticket_name = f"{TICKET_PREFIX}-{author.name.lower()}-{counter}"
            existing = discord.utils.get(guild.text_channels, name=ticket_name)
            counter += 1

        overwrites = {
            guild.default_role:
            discord.PermissionOverwrite(view_channel=False),
            author:
            discord.PermissionOverwrite(view_channel=True,
                                        send_messages=True,
                                        read_messages=True),
        }

        verified_role = guild.get_role(1423395296917983444)
        if verified_role:
            overwrites[verified_role] = discord.PermissionOverwrite(
                view_channel=False)

        for role_id in (ROLE_OWNER, ROLE_MODERATOR, ROLE_STAFF):
            role = guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(
                    view_channel=True, send_messages=True, read_messages=True)

        category = guild.get_channel(
            CATEGORY_TICKET_ID) if CATEGORY_TICKET_ID else None
        ticket = await guild.create_text_channel(name=ticket_name,
                                                 overwrites=overwrites,
                                                 category=category)

        total_pkr, total_usd = calc_total(self.parent_view.selected)
        embed = discord.Embed(title="New Quest Order",
                              color=discord.Color.gold())
        embed.add_field(name="User", value=author.mention)
        embed.add_field(name="RSN", value=self.parent_view.rsn)
        embed.add_field(name="Quests",
                        value="\n".join(self.parent_view.selected))
        embed.add_field(name="Total",
                        value=f"PKR {total_pkr} • USD {total_usd}")
        embed.set_footer(
            text="Staff: Use the buttons below to manage the ticket.")

        from main import TicketControlView  # local import to avoid circular dependency
        view = TicketControlView(author)
        await ticket.send(
            content=
            f"{author.mention} — your ticket has been created. Staff will assist you shortly.",
            embed=embed,
            view=view,
        )
        await interaction.response.send_message(
            f"Ticket created: {ticket.mention}", ephemeral=True)
