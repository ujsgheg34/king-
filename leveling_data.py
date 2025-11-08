# leveling_data.py
# 🔹 Simple global multiplier for quick price updates
# Just change PRICE_MULTIPLIER once and all rates auto-adjust
PRICE_MULTIPLIER = 1.0   # Example: 1.1 = +10%, 0.9 = -10%
USD_RATE = 280            # 1 USD ≈ 280 PKR (for conversion)

def calc_usd(pkr):
    """Convert PKR to USD (string formatted)."""
    return f"${pkr / USD_RATE:.4f}"

LEVELING_RATES = {
    # ⚔️ Combat Training (Monkey Madness, NMZ, Crabs)
    "Monkey Madness 1 - Bursting": (1.0 * PRICE_MULTIPLIER, calc_usd(1.0 * PRICE_MULTIPLIER)),
    "Monkey Madness 1 - Chinning": (0.8 * PRICE_MULTIPLIER, calc_usd(0.8 * PRICE_MULTIPLIER)),
    "Monkey Madness 2 - Bursting": (0.65 * PRICE_MULTIPLIER, calc_usd(0.65 * PRICE_MULTIPLIER)),
    "Monkey Madness 2 - Chinning": (0.5 * PRICE_MULTIPLIER, calc_usd(0.5 * PRICE_MULTIPLIER)),
    "Nightmare Zone (70-99 Melee)": (0.5 * PRICE_MULTIPLIER, calc_usd(0.5 * PRICE_MULTIPLIER)),
    "Rock/Sand Crabs (1-70 All)": (1.75 * PRICE_MULTIPLIER, calc_usd(1.75 * PRICE_MULTIPLIER)),
    "Rock/Sand Crabs (70-99 All)": (0.75 * PRICE_MULTIPLIER, calc_usd(0.75 * PRICE_MULTIPLIER)),

    # 🪓 Woodcutting
    "Woodcutting 1-15": (5 * PRICE_MULTIPLIER, calc_usd(5 * PRICE_MULTIPLIER)),
    "Woodcutting 15-35": (3 * PRICE_MULTIPLIER, calc_usd(3 * PRICE_MULTIPLIER)),
    "Woodcutting 35-61": (2.5 * PRICE_MULTIPLIER, calc_usd(2.5 * PRICE_MULTIPLIER)),
    "Woodcutting 61-90": (1.75 * PRICE_MULTIPLIER, calc_usd(1.75 * PRICE_MULTIPLIER)),
    "Woodcutting 90-99": (1.25 * PRICE_MULTIPLIER, calc_usd(1.25 * PRICE_MULTIPLIER)),

    # 🕵️ Thieving
    "Thieving 1-25": (12.5 * PRICE_MULTIPLIER, calc_usd(12.5 * PRICE_MULTIPLIER)),
    "Thieving 25-45": (7.5 * PRICE_MULTIPLIER, calc_usd(7.5 * PRICE_MULTIPLIER)),
    "Thieving 45-65": (5 * PRICE_MULTIPLIER, calc_usd(5 * PRICE_MULTIPLIER)),
    "Thieving 65-81": (2 * PRICE_MULTIPLIER, calc_usd(2 * PRICE_MULTIPLIER)),
    "Thieving 81-99": (1.5 * PRICE_MULTIPLIER, calc_usd(1.5 * PRICE_MULTIPLIER)),

    # 🩸 Slayer
    "Slayer 1-50": (6 * PRICE_MULTIPLIER, calc_usd(6 * PRICE_MULTIPLIER)),
    "Slayer 50-80": (5 * PRICE_MULTIPLIER, calc_usd(5 * PRICE_MULTIPLIER)),
    "Slayer 80-99": (4 * PRICE_MULTIPLIER, calc_usd(4 * PRICE_MULTIPLIER)),

    # 🔮 Runecrafting
    "Runecrafting 1-23 (Lava/ZMI)": (20 * PRICE_MULTIPLIER, calc_usd(20 * PRICE_MULTIPLIER)),
    "Runecrafting 23-50 (Lava/ZMI)": (7.5 * PRICE_MULTIPLIER, calc_usd(7.5 * PRICE_MULTIPLIER)),
    "Runecrafting 50-75 (Lava/ZMI)": (5.5 * PRICE_MULTIPLIER, calc_usd(5.5 * PRICE_MULTIPLIER)),
    "Runecrafting 75-99 (Lava/ZMI)": (5 * PRICE_MULTIPLIER, calc_usd(5 * PRICE_MULTIPLIER)),
    "Runecrafting 1-99 (Lava + Runners)": (7.5 * PRICE_MULTIPLIER, calc_usd(7.5 * PRICE_MULTIPLIER)),
    "Runecrafting 77-90 (Zeah)": (3.5 * PRICE_MULTIPLIER, calc_usd(3.5 * PRICE_MULTIPLIER)),
    "Runecrafting 90-99 (Zeah)": (2.75 * PRICE_MULTIPLIER, calc_usd(2.75 * PRICE_MULTIPLIER)),

    # 💀 Prayer
    "Prayer 1-70 (Dragon Bones)": (0.6 * PRICE_MULTIPLIER, calc_usd(0.6 * PRICE_MULTIPLIER)),
    "Prayer 70-99 (Superior Bones)": (0.35 * PRICE_MULTIPLIER, calc_usd(0.35 * PRICE_MULTIPLIER)),

    # ⛏️ Mining
    "Mining 1-30 (Iron Ore)": (35 * PRICE_MULTIPLIER, calc_usd(35 * PRICE_MULTIPLIER)),
    "Motherlode 30-72": (5.5 * PRICE_MULTIPLIER, calc_usd(5.5 * PRICE_MULTIPLIER)),
    "Motherlode 72-85": (3.5 * PRICE_MULTIPLIER, calc_usd(3.5 * PRICE_MULTIPLIER)),
    "Motherlode 85-99": (3 * PRICE_MULTIPLIER, calc_usd(3 * PRICE_MULTIPLIER)),
    "Volcanic Mine 75-85": (3.25 * PRICE_MULTIPLIER, calc_usd(3.25 * PRICE_MULTIPLIER)),
    "Volcanic Mine 85-99": (3 * PRICE_MULTIPLIER, calc_usd(3 * PRICE_MULTIPLIER)),
    "Powermine 30-80": (6 * PRICE_MULTIPLIER, calc_usd(6 * PRICE_MULTIPLIER)),
    "3t4g 80-99": (5 * PRICE_MULTIPLIER, calc_usd(5 * PRICE_MULTIPLIER)),

    # 🐍 Hunter
    "Birds 1-29": (12.5 * PRICE_MULTIPLIER, calc_usd(12.5 * PRICE_MULTIPLIER)),
    "Birds 29-60": (6 * PRICE_MULTIPLIER, calc_usd(6 * PRICE_MULTIPLIER)),
    "Monkeys 60-80": (2 * PRICE_MULTIPLIER, calc_usd(2 * PRICE_MULTIPLIER)),
    "Monkeys 80-99": (1.75 * PRICE_MULTIPLIER, calc_usd(1.75 * PRICE_MULTIPLIER)),
    "Sallies 60-69": (3 * PRICE_MULTIPLIER, calc_usd(3 * PRICE_MULTIPLIER)),
    "Sallies 69-80": (2.5 * PRICE_MULTIPLIER, calc_usd(2.5 * PRICE_MULTIPLIER)),
    "Sallies 80-99": (2 * PRICE_MULTIPLIER, calc_usd(2 * PRICE_MULTIPLIER)),
    "Chins 63-80": (3.5 * PRICE_MULTIPLIER, calc_usd(3.5 * PRICE_MULTIPLIER)),
    "Chins 80-99": (2.5 * PRICE_MULTIPLIER, calc_usd(2.5 * PRICE_MULTIPLIER)),

    # 🌿 Herblore
    "Herblore 1-38": (1.5 * PRICE_MULTIPLIER, calc_usd(1.5 * PRICE_MULTIPLIER)),
    "Herblore 38-66": (1 * PRICE_MULTIPLIER, calc_usd(1 * PRICE_MULTIPLIER)),
    "Herblore 66-81": (0.6 * PRICE_MULTIPLIER, calc_usd(0.6 * PRICE_MULTIPLIER)),
    "Herblore 81-99": (0.4 * PRICE_MULTIPLIER, calc_usd(0.4 * PRICE_MULTIPLIER)),

    # 🎣 Fishing
    "Fishing 1-30": (11.5 * PRICE_MULTIPLIER, calc_usd(11.5 * PRICE_MULTIPLIER)),
    "Fishing 30-58": (6 * PRICE_MULTIPLIER, calc_usd(6 * PRICE_MULTIPLIER)),
    "Fishing 58-70": (3 * PRICE_MULTIPLIER, calc_usd(3 * PRICE_MULTIPLIER)),
    "Fishing 70-85": (2.25 * PRICE_MULTIPLIER, calc_usd(2.25 * PRICE_MULTIPLIER)),
    "Fishing 85-99": (2 * PRICE_MULTIPLIER, calc_usd(2 * PRICE_MULTIPLIER)),

    # 🔥 Firemaking
    "Firemaking 1-15": (7.5 * PRICE_MULTIPLIER, calc_usd(7.5 * PRICE_MULTIPLIER)),
    "Firemaking 15-50": (3 * PRICE_MULTIPLIER, calc_usd(3 * PRICE_MULTIPLIER)),
    "Firemaking 50-80": (1.25 * PRICE_MULTIPLIER, calc_usd(1.25 * PRICE_MULTIPLIER)),
    "Firemaking 80-90": (0.9 * PRICE_MULTIPLIER, calc_usd(0.9 * PRICE_MULTIPLIER)),
    "Firemaking 90-99": (0.6 * PRICE_MULTIPLIER, calc_usd(0.6 * PRICE_MULTIPLIER)),

    # 🌾 Farming
    "Farming Tree Runs 1-15": (10 * PRICE_MULTIPLIER, calc_usd(10 * PRICE_MULTIPLIER)),
    "Farming Tree Runs 15-34": (5 * PRICE_MULTIPLIER, calc_usd(5 * PRICE_MULTIPLIER)),
    "Farming Tree Runs 54-74": (0.9 * PRICE_MULTIPLIER, calc_usd(0.9 * PRICE_MULTIPLIER)),
    "Farming Tree Runs 74-99": (0.35 * PRICE_MULTIPLIER, calc_usd(0.35 * PRICE_MULTIPLIER)),
    "Farming Tithe 34-54": (12.5 * PRICE_MULTIPLIER, calc_usd(12.5 * PRICE_MULTIPLIER)),
    "Farming Tithe 54-74": (6 * PRICE_MULTIPLIER, calc_usd(6 * PRICE_MULTIPLIER)),
    "Farming Tithe 74-99": (4 * PRICE_MULTIPLIER, calc_usd(4 * PRICE_MULTIPLIER)),

    # 💎 Crafting
    "Crafting 1-31": (1.75 * PRICE_MULTIPLIER, calc_usd(1.75 * PRICE_MULTIPLIER)),
    "Crafting 31-66": (0.6 * PRICE_MULTIPLIER, calc_usd(0.6 * PRICE_MULTIPLIER)),
    "Crafting 66-99": (0.5 * PRICE_MULTIPLIER, calc_usd(0.5 * PRICE_MULTIPLIER)),

    # 🍳 Cooking
    "Cooking 1-35": (1.5 * PRICE_MULTIPLIER, calc_usd(1.5 * PRICE_MULTIPLIER)),
    "Cooking 35-99": (0.5 * PRICE_MULTIPLIER, calc_usd(0.5 * PRICE_MULTIPLIER)),

    # 🏠 Construction
    "Construction 1-20": (10 * PRICE_MULTIPLIER, calc_usd(10 * PRICE_MULTIPLIER)),
    "Construction 20-33": (2.5 * PRICE_MULTIPLIER, calc_usd(2.5 * PRICE_MULTIPLIER)),
    "Construction 33-52": (2 * PRICE_MULTIPLIER, calc_usd(2 * PRICE_MULTIPLIER)),
    "Construction 52-99": (0.75 * PRICE_MULTIPLIER, calc_usd(0.75 * PRICE_MULTIPLIER)),

    # 🏃 Agility
    "Agility 1-20": (20 * PRICE_MULTIPLIER, calc_usd(20 * PRICE_MULTIPLIER)),
    "Agility 20-50": (12.5 * PRICE_MULTIPLIER, calc_usd(12.5 * PRICE_MULTIPLIER)),
    "Agility 50-60": (6.5 * PRICE_MULTIPLIER, calc_usd(6.5 * PRICE_MULTIPLIER)),
    "Agility 60-90": (3.5 * PRICE_MULTIPLIER, calc_usd(3.5 * PRICE_MULTIPLIER)),
    "Agility 90-99": (3 * PRICE_MULTIPLIER, calc_usd(3 * PRICE_MULTIPLIER)),

    # 🏹 Fletching
    "Fletching 1-40": (1 * PRICE_MULTIPLIER, calc_usd(1 * PRICE_MULTIPLIER)),
    "Fletching 40-60": (0.4 * PRICE_MULTIPLIER, calc_usd(0.4 * PRICE_MULTIPLIER)),
    "Fletching 60-99": (0.25 * PRICE_MULTIPLIER, calc_usd(0.25 * PRICE_MULTIPLIER)),

    # ⚒️ Smithing
    "Smithing 1-30": (2 * PRICE_MULTIPLIER, calc_usd(2 * PRICE_MULTIPLIER)),
    "Smithing 30-60": (1.25 * PRICE_MULTIPLIER, calc_usd(1.25 * PRICE_MULTIPLIER)),
    "Smithing 60-80": (0.9 * PRICE_MULTIPLIER, calc_usd(0.9 * PRICE_MULTIPLIER)),
    "Smithing 80-99": (0.6 * PRICE_MULTIPLIER, calc_usd(0.6 * PRICE_MULTIPLIER)),
}
