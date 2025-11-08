# bossing_data.py
# Rates (PKR, USD-string). USD shown per unit or as given.
BOSSING_RATES = {
    "Slayer": {
        "Grotesque Guardians": (12.5, "$0.04"),
        "Abyssal Sire": (20, "$0.07"),
        "Cerberus": (10, "$0.04"),
        "Thermonuclear Smoke Devil": (5, "$0.02"),
        "Hydra": (15, "$0.05"),
        "Dagannoth Kings": (6.25, "$0.02"),
        "Kalphite Queen": (20, "$0.07"),
        "Demonic Gorillas": (8.75, "$0.03"),
        "Lizardman Shaman": (4, "$0.01"),
    },
    "Wilderness Bossing": {
        "Vet'ion": (25, "$0.09"),
        "Callisto": (250, "$0.89"),
        "Venenatis": (20, "$0.07"),
        "Scorpia": (6, "$0.02"),
        "Chaos Elemental": (10, "$0.04"),
        "Chaos Fanatic": (6.5, "$0.02"),
        "King Black Dragon": (6.5, "$0.02"),
    },
    "Miscellaneous": {
        "Barrows Chests": (22.5, "$0.08"),
        "Zulrah": (12.5, "$0.04"),
        "Vorkath": (16.5, "$0.06"),
        "Giant Mole": (5, "$0.02"),
        "Sarachnis": (10, "$0.04"),
        "Corporeal Beast": (50, "$0.18"),
        "Gauntlet (corrupted kill)": (100, "$0.36"),
        "Nightmare Solo": (200, "$0.71"),
        "Nightmare FFA": (75, "$0.27"),
        "Zalcano (per KC, 3-5 man)": (22.5, "$0.08"),
        "God Wars Dungeon (quote)": (0, "$0.00"),  # quote -> 0 indicates open ticket for price
        "Firecape - Main/Zerker": (1868, "$6.58"),  # included here since you prefer Bossing
        "Firecape - Pure": (4290, "$15.12"),
        "Firecape - Ironman (Main)": (1841, "$6.49"),
    },
    "Raids - Chambers of Xeric": {
        "CoX Standard - Max Gear": (300, "$1.07"),
        "CoX Standard (Tent Whip + BP)": (450, "$1.61"),
        "CoX Challenge - Max Gear": (450, "$1.61"),
        "CoX Solo - Max Gear": (600, "$2.14"),
    },
    "Raids - Theatre of Blood": {
        "ToB Standard - Max Gear": (450, "$1.61"),
        "ToB With Scythe": (300, "$1.07"),
        "ToB With Tent Whip": (450, "$1.61"),
        "ToB Hard Mode (quote)": (0, "$0.00"),
    }
}
