# config.py

# 👑 Set to your exact Discord Account User ID for Admin Authority
OWNER_ID = 1111819902144225310  

# --- MULTIPLE GEMS (LUCK BOOSTS) ---
GEMS = {
    "ruby_gem": {"name": "🔴 Ruby Luck Gem", "price": 50000, "boost": 1.15, "desc": "+15% Gambling Luck"},
    "sapphire_gem": {"name": "🔵 Sapphire Luck Gem", "price": 150000, "boost": 1.30, "desc": "+30% Gambling Luck"},
    "emerald_gem": {"name": "🟢 Emerald Luck Gem", "price": 500000, "boost": 1.50, "desc": "+50% Gambling Luck"},
    "cosmic_gem": {"name": "🌌 Cosmic Void Gem", "price": 2500000, "boost": 2.00, "desc": "+100% Gambling Luck!"}
}

# --- WEAPONS WITH TIERS & POWER ---
WEAPONS = {
    "wooden_sword": {"name": "🗡️ Wooden Training Sword", "price": 25000, "tier": "Common", "dmg": 10, "attack_name": "Poke"},
    "iron_blade": {"name": "⚔️ Iron Broadblade", "price": 100000, "tier": "Uncommon", "dmg": 35, "attack_name": "Slash"},
    "shadow_dagger": {"name": "🔮 Shadow Dagger", "price": 450000, "tier": "Rare", "dmg": 85, "attack_name": "Phantom Strike"},
    "plasma_rifle": {"name": "🔫 Plasma Core Rifle", "price": 1500000, "tier": "Legendary", "dmg": 200, "attack_name": "Hyper Beam Burst"},
    "infinity_gauntlet": {"name": "👑 Infinity Gauntlet", "price": 10000000, "tier": "Mythic", "dmg": 600, "attack_name": "Universal Snap"}
}

# --- GENERATION 1 STICKER EMOJI MATRIX (BY TIERS) ---
POKEMON_POOL = {
    "Common": [
        {"name": "Bulbasaur", "emoji": "<a:sbulbasaur:10000001>", "hp": 100, "attack": "Vine Whip"},
        {"name": "Charmander", "emoji": "<a:scharmander:10000002>", "hp": 95, "attack": "Ember"},
        {"name": "Squirtle", "emoji": "<a:ssquirtle:10000003>", "hp": 105, "attack": "Water Gun"},
        {"name": "Caterpie", "emoji": "<a:scaterpie:10000004>", "hp": 80, "attack": "Bug Bite"},
        {"name": "Pidgey", "emoji": "<a:spidgey:10000005>", "hp": 85, "attack": "Gust"},
        {"name": "Rattata", "emoji": "<a:srattata:10000006>", "hp": 75, "attack": "Quick Attack"},
        {"name": "Pikachu", "emoji": "<a:spikachu:10000007>", "hp": 90, "attack": "Thunder Shock"},
        {"name": "Zubat", "emoji": "<a:szubat:10000008>", "hp": 85, "attack": "Leech Life"},
        {"name": "Psyduck", "emoji": "<a:spsyduck:10000009>", "hp": 110, "attack": "Water Pulse"},
        {"name": "Magikarp", "emoji": "<a:smagikarp:10000010>", "hp": 30, "attack": "Splash"}
    ],
    "Rare": [
        {"name": "Venusaur", "emoji": "<a:svenusaur:20000001>", "hp": 180, "attack": "Frenzy Plant"},
        {"name": "Charizard", "emoji": "<a:scharizard:20000002>", "hp": 175, "attack": "Blast Burn"},
        {"name": "Blastoise", "emoji": "<a:sblastoise:20000003>", "hp": 185, "attack": "Hydro Cannon"},
        {"name": "Gengar", "emoji": "<a:sgengar:20000004>", "hp": 140, "attack": "Shadow Ball"},
        {"name": "Gyarados", "emoji": "<a:sgyarados:20000005>", "hp": 195, "attack": "Dragon Rage"},
        {"name": "Dragonite", "emoji": "<a:sdragonite:20000006>", "hp": 210, "attack": "Outrage"},
        {"name": "Arcanine", "emoji": "<a:sarcanine:20000007>", "hp": 180, "attack": "Flare Blitz"},
        {"name": "Snorlax", "emoji": "<a:ssnorlax:20000008>", "hp": 260, "attack": "Body Slam"},
        {"name": "Eevee", "emoji": "<a:seevee:20000009>", "hp": 110, "attack": "Swift"}
    ],
    "Legendary": [
        {"name": "Articuno", "emoji": "<a:sarticuno:30000001>", "hp": 250, "attack": "Blizzard"},
        {"name": "Zapdos", "emoji": "<a:szapdos:30000002>", "hp": 250, "attack": "Thunderbolt"},
        {"name": "Moltres", "emoji": "<a:smoltres:30000003>", "hp": 250, "attack": "Sky Attack"}
    ],
    "Mythic": [
        {"name": "Mewtwo", "emoji": "<a:smewtwo:40000001>", "hp": 280, "attack": "Psystrike Core"},
        {"name": "Mew", "emoji": "<a:smew:40000002>", "hp": 250, "attack": "Genesis Super Nova"}
    ]
}

# --- ULTIMATE WORLD ENCOUNTER RAID BOSS ---
WORLD_BOSS = {
    "name": "Chaos Void Beast Apex",
    "emoji": "<a:s_void_beast:99999001>",
    "hp": 2500,
    "attack": "🌌 Event Horizon Collapse",
    "tier": "💥 BEAST CLASS BOSS 💥"
}

# Shared structural runtime in-memory player profiles
USER_DATA = {}

def get_profile(user_id):
    return USER_DATA.get(user_id, None)

def create_starter_account(user_id, chosen_pokemon):
    USER_DATA[user_id] = {
        "sycoizz": 50000,  # Complimentary initial starter cash allocation
        "gems": [],
        "weapons": [],
        "equipped_weapon": None,
        "pokemon": [chosen_pokemon]
    }
    return USER_DATA[user_id]

async def edit_msg_safe(msg, content):
    try:
        await msg.edit(content=content)
    except Exception:
        pass

