# leveling_panel_v4.py
import discord
from discord.ui import View, Select, Modal, TextInput, Button
from leveling_data import LEVELING_RATES
from config import CATEGORY_TICKET_ID, ROLE_OWNER, ROLE_MODERATOR, ROLE_STAFF, TICKET_PREFIX

# ---------- Helpers ----------
def xp_to_level(xp: int):
    """Approximate OSRS level from total XP using standard formula."""
    points = 0
    for lvl in range(1, 100):
        points += int(lvl + 300 * 2 ** (lvl / 7.0))
        if xp < points / 4:
            return lvl
    return 99


def parse_xp_input(value: str) -> int:
    """Accept '100k', '1.5m', '123456' etc. Returns int XP or raises ValueError."""
    v = value.lower().replace(",", "").strip()
    if v.endswith("m"):
        return int(float(v[:-1]) * 1_000_000)
    if v.endswith("k"):
        return int(float(v[:-1]) * 1_000)
    return int(float(v))


def pretty_num(n: int) -> str:
    return f"{n:,}"


# ---------- Core skill list (23) ----------
CORE_SKILLS = [
    "Attack", "Strength", "Defence", "Ranged", "Prayer", "Magic", "Hitpoints",
    "Cooking", "Woodcutting", "Fletching", "Fishing", "Firemaking", "Crafting",
    "Smithing", "Mining", "Herblore", "Agility", "Thieving", "Runecrafting",
    "Hunter", "Construction", "Slayer"
]

# ---------- Data extraction ----------
def extract_skill_data(skill_name: str) -> dict:
    """
    Return {entry_name: (pkr, usd)} for entries that belong to given skill_name.
    Also group combat-related methods (Monkey Madness, Crabs, NMZ) under combat skills.
    """
    res = {}
    skill_lower = skill_name.lower()
    for key, val in LEVELING_RATES.items():
        if key.lower().startswith(skill_lower):
            res[key] = val

    # For combat skills: show shared combat methods
    if skill_name in {"Attack", "Strength", "Defence", "Ranged", "Magic", "Hitpoints"}:
        for key, val in LEVELING_RATES.items():
            kl = key.lower()
            if "monkey madness" in kl or "rock/sand crabs" in kl or "crabs" in kl or "nightmare zone" in kl or "nmz" in kl:
                res[key] = val
            # some combat entries might be 'Magic (Bursting)' style; include those too
            if "bursting" in kl or "chinning" in kl:
                res[key] = val
    return dict(sorted(res.items()))


# ---------- Start View & Skill select ----------
class SkillSelect(Select):
    def __init__(self, user: discord.User):
        options = [
            discord.SelectOption(label=s, description=f"View leveling rates for {s}")
            for s in CORE_SKILLS
        ]
        super().__init__(placeholder="Select a skill to view leveling prices...", options=options, min_values=1, max_values=1)
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        skill = self.values[0]
        data = extract_skill_data(skill)
        if not data:
            await interaction.response.send_message(f"⚠️ No pricing data found for **{skill}**.", ephemeral=True)
            return

        # Build a stylish embed (similar style to quest panel)
        embed = discord.Embed(
            title=f"⚔️ {skill} Leveling Rates",
            description=f"Select the desired rate / XP bracket for **{skill}** from the dropdown below.",
            color=discord.Color.teal()
        )
        # Group similar names: show friendly label
        for name, (pkr, usd) in data.items():
            label = name.replace(skill, "").strip()
            if not label:
                label = name
            embed.add_field(name=label, value=f"💰 {pkr} PKR ({usd}) per 100 XP", inline=False)

        embed.set_footer(text="After selecting a bracket you will enter From/To XP to get a final estimate.")
        await interaction.response.edit_message(embed=embed, view=RangeSelectView(self.user, skill, data))


class LevelingStartView(View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=None)
        self.add_item(SkillSelect(user))


# ---------- Range select (shows options for chosen skill and opens modal) ----------
class RangeSelect(Select):
    def __init__(self, user: discord.User, skill: str, data: dict):
        options = []
        for k, (pkr, _) in data.items():
            # Keep labels under 100 chars — safe for Discord select
            label = k if len(k) <= 100 else k[:97] + "..."
            options.append(discord.SelectOption(label=label, description=f"{pkr} PKR per 100 XP"))
        # Discord limits: 1-25 options; if data is >25 (rare), slice and show warning option
        if not options:
            options = [discord.SelectOption(label="⚠️ No ranges available")]
        if len(options) > 25:
            options = options[:24] + [discord.SelectOption(label="⚠️ More ranges available (see website)")]
        super().__init__(placeholder="Choose a rate / range...", options=options, min_values=1, max_values=1)
        self.user = user
        self.skill = skill
        self.data = data

    async def callback(self, interaction: discord.Interaction):
        choice = self.values[0]
        # find the data matching the selected label (exact key), fallback if not exact
        matched = None
        for k in self.data.keys():
            if k == choice or k.startswith(choice) or choice.startswith(k):
                matched = k
                break
        if not matched:
            # try fuzzy match
            for k in self.data.keys():
                if choice in k:
                    matched = k
                    break
        if not matched:
            await interaction.response.send_message("⚠️ Could not identify selected range. Try again.", ephemeral=True)
            return

        pkr, usd = self.data[matched]
        # open modal for XP input
        await interaction.response.send_modal(XPInputModal(self.user, self.skill, matched, pkr, usd))


class RangeSelectView(View):
    def __init__(self, user: discord.User, skill: str, data: dict):
        super().__init__(timeout=None)
        self.add_item(RangeSelect(user, skill, data))


# ---------- XP Input Modal ----------
class XPInputModal(Modal, title="Enter From / To XP"):
    from_xp = TextInput(label="From XP (e.g. 100k or 150000)", style=discord.TextStyle.short)
    to_xp = TextInput(label="To XP (e.g. 5m or 5000000)", style=discord.TextStyle.short)

    def __init__(self, user: discord.User, skill: str, range_label: str, pkr: float, usd: str):
        super().__init__()
        self.user = user
        self.skill = skill
        self.range_label = range_label
        self.pkr = pkr
        self.usd = usd

    async def on_submit(self, interaction: discord.Interaction):
        # parse XP values
        try:
            start = parse_xp_input(self.from_xp.value)
            end = parse_xp_input(self.to_xp.value)
        except Exception:
            await interaction.response.send_message("❌ Invalid XP values. Use examples like 100k, 1.5m or full numbers.", ephemeral=True)
            return

        if end <= start:
            await interaction.response.send_message("❌ 'To XP' must be larger than 'From XP'.", ephemeral=True)
            return

        gained = end - start
        lvl_start = xp_to_level(start)
        lvl_end = xp_to_level(end)
        total_pkr = round((gained / 100) * self.pkr, 2)
        # try to parse USD from provided usd string, fallback if not numeric
        try:
            usd_val = float(str(self.usd).replace("$", ""))
            total_usd = round((gained / 100) * usd_val, 2)
        except Exception:
            total_usd = None

        # Stylish summary embed
        embed = discord.Embed(
            title=f"✅ {self.skill} Leveling Estimate",
            color=discord.Color.green()
        )
        embed.add_field(name="XP Range", value=f"{pretty_num(start)} → {pretty_num(end)}", inline=True)
        embed.add_field(name="Level Range", value=f"{lvl_start} → {lvl_end}", inline=True)
        embed.add_field(name="XP Gained", value=f"{pretty_num(gained)}", inline=False)
        embed.add_field(name="Rate", value=f"{self.pkr} PKR ({self.usd}) per 100 XP", inline=False)
        total_line = f"💰 {pretty_num(int(total_pkr))} PKR"
        if total_usd is not None:
            total_line += f" (~${total_usd:.2f})"
        embed.add_field(name="Total", value=total_line, inline=False)
        embed.set_footer(text=f"Range selected: {self.range_label}")

        # Add Create Ticket button below the summary
        view = ConfirmEstimateView(self.user, self.skill, self.range_label, start, end, gained, self.pkr, total_pkr, total_usd)
        # send ephemeral so only the user sees this summary and can create a ticket
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


# ---------- Confirm + Create Ticket ----------
class CreateTicketButton(Button):
    def __init__(self, user: discord.User, skill, range_label, start, end, gained, rate_pkr, total_pkr, total_usd):
        super().__init__(label="🎟 Create Leveling Ticket", style=discord.ButtonStyle.primary)
        self.user = user
        self.skill = skill
        self.range_label = range_label
        self.start = start
        self.end = end
        self.gained = gained
        self.rate_pkr = rate_pkr
        self.total_pkr = total_pkr
        self.total_usd = total_usd

    async def callback(self, interaction: discord.Interaction):
        # Prevent others from clicking
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This button is only for the user who requested the estimate.", ephemeral=True)
            return

        guild = interaction.guild
        author = interaction.user

        # create unique ticket channel name
        base = f"{TICKET_PREFIX}-{author.name.lower()}"
        ticket_name = base
        i = 1
        while discord.utils.get(guild.text_channels, name=ticket_name):
            ticket_name = f"{base}-{i}"
            i += 1

        # build overwrites
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            author: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True),
        }
        # allow staff roles
        for role_id in (ROLE_OWNER, ROLE_MODERATOR, ROLE_STAFF):
            role = guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True)

        category = guild.get_channel(CATEGORY_TICKET_ID) if CATEGORY_TICKET_ID else None
        # create channel
        ticket = await guild.create_text_channel(name=ticket_name, overwrites=overwrites, category=category)

        # build order embed to post in ticket
        embed = discord.Embed(title="🎟 New Leveling Order", color=discord.Color.gold())
        embed.add_field(name="Customer", value=author.mention, inline=True)
        embed.add_field(name="Skill", value=self.skill, inline=True)
        embed.add_field(name="Range Selected", value=self.range_label, inline=False)
        embed.add_field(name="XP Range", value=f"{pretty_num(self.start)} → {pretty_num(self.end)}", inline=True)
        embed.add_field(name="Level Range", value=f"{xp_to_level(self.start)} → {xp_to_level(self.end)}", inline=True)
        embed.add_field(name="XP Gained", value=f"{pretty_num(self.gained)}", inline=False)
        embed.add_field(name="Rate", value=f"{self.rate_pkr} PKR per 100 XP", inline=False)
        total_line = f"💰 {pretty_num(int(self.total_pkr))} PKR"
        if self.total_usd is not None:
            total_line += f" (~${self.total_usd:.2f})"
        embed.add_field(name="Total", value=total_line, inline=False)
        embed.set_footer(text="Staff: use the buttons below to manage this ticket.")

        # Attach the same TicketControlView from main.py (import inside to avoid circular import)
        try:
            from main import TicketControlView
            view = TicketControlView(author)
        except Exception:
            view = None

        await ticket.send(content=f"{author.mention} — your leveling ticket has been created. Staff will assist you shortly.", embed=embed, view=view)
        await interaction.response.send_message(f"✅ Ticket created: {ticket.mention}", ephemeral=True)


class ConfirmEstimateView(View):
    def __init__(self, user: discord.User, skill, range_label, start, end, gained, rate_pkr, total_pkr, total_usd):
        super().__init__(timeout=None)
        self.add_item(CreateTicketButton(user, skill, range_label, start, end, gained, rate_pkr, total_pkr, total_usd))
        # keep only Closeable by user (we don't add other buttons here)


# End of file
