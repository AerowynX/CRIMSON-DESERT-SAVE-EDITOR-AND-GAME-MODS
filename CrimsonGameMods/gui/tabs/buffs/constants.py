import re

_BUFF_PRESETS = [
    {"name": "Max All"},
    {"name": "Max All Flat"},
    {"name": "Max DDD"},
    {"name": "Max DPV"},
    {"name": "Max HP"},
    {"name": "Max All Rates"},
    {"name": "Swap to DDD"},
    {"name": "Swap to DPV"},
    None,
]

_BUFF_DESCRIPTIONS = {
    "Invincible": "Makes you unkillable. Value: 1 = on, 0 = off. [flat2 — 12B entry]",
    "Hp": "Maximum health points. Value: raw HP number (e.g. 1,000,000). [flat1 — 8B entry]",
    "DDD (Damage)": "Direct Damage Dealt. Attack power. Value: raw damage number. [flat2 — 12B entry]",
    "DPV (Defense)": "Defense Point Value. Damage reduction. Value: raw number. [flat2 — 12B entry]",
    "CriticalDamage": "Extra damage on critical hits. [flat2 — 12B entry, value = raw]",
    "AttackedDamageRate": "Extra damage taken modifier. [flat2 — 12B entry, value = raw]",
    "AttackedDamageReduction": "Damage reduction rate. [flat2 — 12B entry, value = raw]",
    "CriticalRate": "Chance to land a critical hit. Level 0-255 (varies per stat). [rate — 5B entry]",
    "AttackSpeedRate": "How fast you swing/attack. Level 0-255 (varies per stat). [rate — 5B entry]",
    "MoveSpeedRate": "How fast you run. Level 0-255 (varies per stat). [rate — 5B entry]",
    "ClimbSpeedRate": "Climbing speed. Level 0-255 (varies per stat). [rate — 5B entry]",
    "SwimSpeedRate": "Swimming speed. Level 0-255 (varies per stat). [rate — 5B entry]",
    "StaminaRegen": "Stamina recovery rate. Level 0-255 (varies per stat). [rate — 5B entry]",
    "HpRegen": "Health regeneration rate. Level 0-255 (varies per stat). [rate — 5B entry]",
    "MpRegen": "Mana regeneration rate. Level 0-255 (varies per stat). [rate — 5B entry]",
    "FireResistance": "Fire damage resistance. Level 0-255 (varies per stat). [rate — 5B entry]",
    "IceResistance": "Ice damage resistance. Level 0-255 (varies per stat). [rate — 5B entry]",
    "ElectricResistance": "Electric damage resistance. Level 0-255 (varies per stat). [rate — 5B entry]",
    "GuardPVRate": "Guard/block effectiveness. Level 0-255 (varies per stat). [rate — 5B entry]",
    "ReduceCraftMaterial": "Reduces crafting material cost. Level 0-255 (varies per stat). [rate — 5B entry]",
    "MoreOreDrop": "Bonus ore from mining. Level 0-255 (varies per stat). [rate — 5B entry]",
    "MoreLumberDrop": "Bonus lumber from chopping. Level 0-255 (varies per stat). [rate — 5B entry]",
    "EquipDropRate": "Equipment drop rate bonus. Level 0-255 (varies per stat). [rate — 5B entry]",
    "MoneyDropRate": "Silver drop rate bonus. Level 0-255 (varies per stat). [rate — 5B entry]",
    "CollectDrop_Ore": "Collection bonus: ore. Level 0-255 (varies per stat). [rate — 5B entry]",
    "CollectDrop_Plant": "Collection bonus: plants. Level 0-255 (varies per stat). [rate — 5B entry]",
    "CollectDrop_Animal": "Collection bonus: animal parts. Level 0-255 (varies per stat). [rate — 5B entry]",
    "CollectDrop_Log": "Collection bonus: logs. Level 0-255 (varies per stat). [rate — 5B entry]",
}

_PRESET_DESCRIPTIONS = [
    "Max every stat on the item: flat values to 999,999, rate levels to 15. No hash changes — keeps original stat types.",
    "Max all flat stats: sets all flat2/flat1 values to 999,999 at every refinement level.",
    "Max DDD to 999,999 at every refinement level. Only edits flat2 stat entries.",
    "Max DPV to 999,999 at every refinement level. Only edits flat2 stat entries.",
    "Max HP to 999,999 at every refinement level. Only edits flat1 stat entries.",
    "Set all rate stats to Lv 15 (max). Only edits rate entries.",
    "Swap existing flat2 stat to DDD (Damage). Same size class, safe in-place swap.",
    "Swap existing flat2 stat to DPV (Defense). Same size class, safe in-place swap.",
    "",
]

_ITEM_PRESETS = {
    "open_sockets": {
        "name": "5 Sockets",
        "description": "Adds 5 open sockets to all newly obtained versions of this item.",
        "warning": "Embedding abyss gears in-game on items that do not normally have socket slots can cause crashing.",
        "drop_default_data": {
            "add_socket_material_item_list": [
                {"item": 1,"value": 500},
                {"item": 1,"value": 1000},
                {"item": 1,"value": 2000},
                {"item": 1,"value": 3000},
                {"item": 1,"value": 4000}
            ],
            "socket_valid_count": 5,
            "use_socket": 1
        }
    },
    "max_enchant": {
        "name": "Max Refine",
        "description": "All newly obtained copies of this item will be lvl 10 be default.",
        "drop_default_data": {
            "drop_enchant_level": 10
        }
    },
    "no_cooldown": {
        "name":"No Cooldown",
        "description": "Set cooldown of item ability to 1s and remove recharge restrictions.",
        "cooltime": 1,
        "item_charge_type": 0,
        "respawn_time_seconds": 0
    },
    "max_charges": {
        "name":"Max Charges",
        "description": "Set charges of item ability to 100.",
        "max_charged_useable_count": 100
    },
    "max_stacks": {
        "name": "Max Stacks",
        "description": "Set the max stack size of an item to 999999.",
        "max_stack_count": 999999  
    },
    "shadow_boots": {
        "name": "Shadow Boots",
        "passives": [
            {"skill": 7201, "level": 1},
            {"skill": 7055, "level": 1},
            {"skill": 7202, "level": 1},
        ],
        "gimmick_info": 1004431,
        "cooltime": 1,
        "item_charge_type": 0,
        "max_charged_useable_count": 100,
        "respawn_time_seconds": 0,
        "docking_child_data": {
            "gimmick_info_key": 1004431,
            "character_key": 0,
            "item_key": 0,
            "attach_parent_socket_name": "Bip01 Footsteps",
            "attach_child_socket_name": "",
            "docking_tag_name_hash": [247236102, 0, 0, 0],
            "docking_equip_slot_no": 65535,
            "spawn_distance_level": 4294967295,
            "is_item_equip_docking_gimmick": 0,
            "send_damage_to_parent": 0,
            "is_body_part": 0,
            "docking_type": 0,
            "is_summoner_team": 0,
            "is_player_only": 0,
            "is_npc_only": 0,
            "is_sync_break_parent": 0,
            "hit_part": 0,
            "detected_by_npc": 0,
            "is_bag_docking": 0,
            "enable_collision": 0,
            "disable_collision_with_other_gimmick": 1,
            "docking_slot_key": "",
            "inherit_summoner": 0,
            "summon_tag_name_hash": [0, 0, 0, 0],
        },
    },
    "lightning_weapon": {
        "name": "Lightning Weapon",
        "passives": [
            {"skill": 91101, "level": 3},
            {"skill": 91104, "level": 3},
            {"skill": 91105, "level": 3},
        ],
        "gimmick_info": 1001961,
        "cooltime": 1,
        "item_charge_type": 0,
        "max_charged_useable_count": 100,
        "respawn_time_seconds": 0,
        "docking_child_data": {
            "gimmick_info_key": 1001961,
            "character_key": 0,
            "item_key": 0,
            "attach_parent_socket_name": "Gimmick_Weapon_00_Socket",
            "attach_child_socket_name": "",
            "docking_tag_name_hash": [3365725887, 0, 0, 0],
            "docking_equip_slot_no": 65535,
            "spawn_distance_level": 4294967295,
            "is_item_equip_docking_gimmick": 1,
            "send_damage_to_parent": 0,
            "is_body_part": 0,
            "docking_type": 0,
            "is_summoner_team": 0,
            "is_player_only": 0,
            "is_npc_only": 0,
            "is_sync_break_parent": 0,
            "hit_part": 0,
            "detected_by_npc": 0,
            "is_bag_docking": 0,
            "enable_collision": 0,
            "disable_collision_with_other_gimmick": 1,
            "docking_slot_key": "",
            "inherit_summoner": 0,
            "summon_tag_name_hash": [0, 0, 0, 0],
        },
    },
    "great_thief": {
        "name": "Great Thief (Block Theft only)",
        "passives": [
            {"skill": 9128, "level": 1},
            {"skill": 76009, "level": 1},
        ],
        "gimmick_info": 1002041,
        "cooltime": 1800,
        "item_charge_type": 0,
        "max_charged_useable_count": 1,
        "respawn_time_seconds": 0,
        "docking_child_data": {
            "gimmick_info_key": 1002041,
            "character_key": 0,
            "item_key": 0,
            "attach_parent_socket_name": "Gimmick_Hand_L_00_Socket",
            "attach_child_socket_name": "",
            "docking_tag_name_hash": [0, 0, 0, 0],
            "docking_equip_slot_no": 65535,
            "spawn_distance_level": 4294967295,
            "is_item_equip_docking_gimmick": 0,
            "send_damage_to_parent": 0,
            "is_body_part": 0,
            "docking_type": 0,
            "is_summoner_team": 0,
            "is_player_only": 0,
            "is_npc_only": 0,
            "is_sync_break_parent": 0,
            "hit_part": 0,
            "detected_by_npc": 0,
            "is_bag_docking": 0,
            "enable_collision": 0,
            "disable_collision_with_other_gimmick": 1,
            "docking_slot_key": "",
            "inherit_summoner": 0,
            "summon_tag_name_hash": [0, 0, 0, 0],
        },
    },
    "great_thief_all": {
        "name": "Great Thief (Block ALL crime)",
        "passives": [
            {"skill": 9128, "level": 1},
            {"skill": 76009, "level": 1},
            {"skill": 76011, "level": 1},
            {"skill": 76012, "level": 1},
        ],
        "gimmick_info": 1002041,
        "cooltime": 1800,
        "item_charge_type": 0,
        "max_charged_useable_count": 1,
        "respawn_time_seconds": 0,
        "docking_child_data": {
            "gimmick_info_key": 1002041,
            "character_key": 0,
            "item_key": 0,
            "attach_parent_socket_name": "Gimmick_Hand_L_00_Socket",
            "attach_child_socket_name": "",
            "docking_tag_name_hash": [0, 0, 0, 0],
            "docking_equip_slot_no": 65535,
            "spawn_distance_level": 4294967295,
            "is_item_equip_docking_gimmick": 0,
            "send_damage_to_parent": 0,
            "is_body_part": 0,
            "docking_type": 0,
            "is_summoner_team": 0,
            "is_player_only": 0,
            "is_npc_only": 0,
            "is_sync_break_parent": 0,
            "hit_part": 0,
            "detected_by_npc": 0,
            "is_bag_docking": 0,
            "enable_collision": 0,
            "disable_collision_with_other_gimmick": 1,
            "docking_slot_key": "",
            "inherit_summoner": 0,
            "summon_tag_name_hash": [0, 0, 0, 0],
        },
    },
    "crime_mask": {
        "name": "Crime Mask (Steal / Threaten)",
        "passives": [
            {"skill": 709, "level": 1},
        ],
    },
}

_FORCE_SOCKET_CATEGORIES = {"Ring", "Necklace", "Earring", "Cloak", "Lantern", "Bracer"}

_FORCE_SOCKET_STRING_KEYS = {"Daeil_Band", "OOngka_Daeil_Band", "Damian_Daeil_Band"}

_NOBILITY_DEGREE_PATTERN = "_Nobility_Degree_"

_CHAR_TRIBE_HASHES = {
    1: {0x13FB2B6E, 0x26BE971F, 0x87D08287, 0x8BF46446,  # Kliff
        0xABFCD791, 0xBFA1F64B, 0xD0A2E1EF, 0xF96C1DD4,
        0xFC66D914, 0xFE7169E2, 0xFF16A579},
    4: {0x26BE971F, 0x8BF46446, 0xABFCD791, 0xF96C1DD4},  # Damiane
    6: {0x13FB2B6E, 0x87D08287, 0xBFA1F64B, 0xD0A2E1EF,  # Oongka
        0xFC66D914, 0xFE7169E2},
}

_PLAYER_TRIBE_HASHES = _CHAR_TRIBE_HASHES[1] | _CHAR_TRIBE_HASHES[4] | _CHAR_TRIBE_HASHES[6] | {0xF21FE2D6}

_PLAYER_CHAR_KEYS = {1, 4, 6}  # Only expand these characters

_DEV_PRESETS = {
    "immune": {
        "label": "Immune Ring",
        "passives": [{"skill": 70994, "level": 1}],
        "regen_stat_list": [{"stat": 1000000, "change_mb": 1000000}],
        "stat_list_static": [{"stat": 1000002, "change_mb": 1000000}],
    },
    "str_hp": {
        "label": "Str+HP Ring",
        "passives": [],
        "regen_stat_list": [{"stat": 1000000, "change_mb": 1000000}],
        "stat_list_static": [{"stat": 1000002, "change_mb": 1000000}],
    },
    "def_hp": {
        "label": "Def+HP Ring",
        "passives": [],
        "regen_stat_list": [{"stat": 1000000, "change_mb": 1000000}],
        "stat_list_static": [{"stat": 1000003, "change_mb": 1000000}],
    },
    "mp_stam": {
        "label": "MP+Stamina Ring",
        "passives": [],
        "regen_stat_list": [
            {"stat": 1000026, "change_mb": 100000},
            {"stat": 1000027, "change_mb": 100000},
        ],
        "stat_list_static": [
            {"stat": 1000037, "change_mb": 100000000},
        ],
    },
    "speed": {
        "label": "Speed Ring",
        "passives": [],
        "regen_stat_list": [],
        "stat_list_static": [],
        "stat_list_static_level": [
            {"stat": 1000010, "change_mb": 15},
            {"stat": 1000011, "change_mb": 15},
            {"stat": 1000007, "change_mb": 15},
        ],
    },
    "all": {
        "label": "All Dev Rings",
        "passives": [{"skill": 70994, "level": 1}],
        "regen_stat_list": [
            {"stat": 1000000, "change_mb": 1000000},
            {"stat": 1000026, "change_mb": 100000},
            {"stat": 1000027, "change_mb": 100000},
        ],
        "stat_list_static": [
            {"stat": 1000002, "change_mb": 1000000},
            {"stat": 1000003, "change_mb": 1000000},
            {"stat": 1000037, "change_mb": 100000000},
        ],
        "stat_list_static_level": [
            {"stat": 1000010, "change_mb": 15},
            {"stat": 1000011, "change_mb": 15},
            {"stat": 1000007, "change_mb": 15},
        ],
    },
    "elemental_weapon": {
        "label": "Elemental Weapon (Lightning+Ice+Fire)",
        "passives": [
            {"skill": 91101, "level": 3},
            {"skill": 91104, "level": 3},
            {"skill": 91105, "level": 3},
        ],
        "gimmick_info": 1001961,
        "cooltime": 1,
        "item_charge_type": 0,
        "max_charged_useable_count": 100,
        "respawn_time_seconds": 0,
        "docking_child_data": {
            "gimmick_info_key": 1001961,
            "character_key": 0,
            "item_key": 0,
            "attach_parent_socket_name": "Gimmick_Weapon_00_Socket",
            "attach_child_socket_name": "",
            "docking_tag_name_hash": [3365725887, 0, 0, 0],
            "docking_equip_slot_no": 65535,
            "spawn_distance_level": 4294967295,
            "is_item_equip_docking_gimmick": 1,
            "send_damage_to_parent": 0,
            "is_body_part": 0,
            "docking_type": 0,
            "is_summoner_team": 0,
            "is_player_only": 0,
            "is_npc_only": 0,
            "is_sync_break_parent": 0,
            "hit_part": 0,
            "detected_by_npc": 0,
            "is_bag_docking": 0,
            "enable_collision": 0,
            "disable_collision_with_other_gimmick": 1,
            "docking_slot_key": "",
            "inherit_summoner": 0,
            "summon_tag_name_hash": [0, 0, 0, 0],
        },
    },
    "jump_boots": {
        "label": "Jump Boots (Dash+Breeze+Swimming)",
        "passives": [
            {"skill": 7201, "level": 1},
            {"skill": 7055, "level": 1},
            {"skill": 7202, "level": 1},
        ],
        "gimmick_info": 1004431,
        "cooltime": 1,
        "item_charge_type": 0,
        "max_charged_useable_count": 100,
        "respawn_time_seconds": 0,
        "docking_child_data": {
            "gimmick_info_key": 1004431,
            "character_key": 0,
            "item_key": 0,
            "attach_parent_socket_name": "Bip01 Footsteps",
            "attach_child_socket_name": "",
            "docking_tag_name_hash": [247236102, 0, 0, 0],
            "docking_equip_slot_no": 65535,
            "spawn_distance_level": 4294967295,
            "is_item_equip_docking_gimmick": 0,
            "send_damage_to_parent": 0,
            "is_body_part": 0,
            "docking_type": 0,
            "is_summoner_team": 0,
            "is_player_only": 0,
            "is_npc_only": 0,
            "is_sync_break_parent": 0,
            "hit_part": 0,
            "detected_by_npc": 0,
            "is_bag_docking": 0,
            "enable_collision": 0,
            "disable_collision_with_other_gimmick": 1,
            "docking_slot_key": "",
            "inherit_summoner": 0,
            "summon_tag_name_hash": [0, 0, 0, 0],
        },
    },
}

_CD_MARKER = b'\x00\x00\x00\x00\x00\x00\x00\x0e'

SE_ITEMBUFFS_DIR = "0058"

SE_STORES_DIR = "0060"

