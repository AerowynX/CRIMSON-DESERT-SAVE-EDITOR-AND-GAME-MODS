# CrimsonGameMods v1.2.0-nightly — dmm_parser Full Migration

**NIGHTLY TEST BUILD — Report bugs, do NOT redistribute on Nexus Mods**

## What changed

Every game-data editing operation in `world.py` and `field_edit.py` has been migrated from hardcoded byte offsets to dmm_parser field-level editing. This means mods survive weekly game updates without code changes.

### world.py — 63 struct ops eliminated (63 → 0)

**Store Editor** — fully dmm_parser (`store_info`)
- Load, display, edit (prices/limits), swap, add, import/export JSON all use dmm_parser dicts
- Old `storeinfo_parser` and `store_editor` parsers completely removed
- Serialization via `dmm_parser.serialize_table('store_info')`

**Spawn Editor** — fully dmm_parser
- Terrain spawns: `terrain_region_auto_spawn_info` — 863 entries (was 180 with old MARKER scanner)
- Factionnode operators: `faction_node_info` — max_op via `raw_data_ext.flag`
- Spawning pool: `spawning_pool_auto_spawn_info` — ambient life density
- Spawn rates: mapped to `spline.raw_g` field
- All edit operations (multiply, halve timers, increase density, context menu) use dict refs
- Character names loaded via `dmm_parser.parse_table('character_info')`
- Old `terrain_spawn_parser` and `factionnode_operator_parser` removed

**Skill / Drop Rate Batch Ops** — dmm_parser
- Cooldown zeroing: `skill_info.cooltime` field directly
- Drop rate multiply: `drop_set_info.list[].raw_16` field

**Dropset Editor** — pabgh header parsing via `int.from_bytes`

**All pack_mod calls** — replaced with `PackGroupBuilder(NONE)` + proper PAPGT management

### field_edit.py — 39 struct ops eliminated (39 → 0)

**Vehicle Tab** — dmm_parser (`vehicle_info`)
- Altitude cap: `max_allowable_height`
- Mount call type: `rider_detect_info` (packed u8)
- Safe zone flag: `send_damage_to`

**Mount Tab** — dmm_parser (`character_info`)
- Duration: `call_mercenary_spawn_duration`
- Cooldown: `call_mercenary_cool_time`

**Weapon Package Tab** — dmm_parser (`character_info`)
- Upper chart: `appearance_name` field
- Lower chart: `character_prefab_path` field
- GamePlay data: `skeleton_name` field
- Appearance: `lookup_22` field
- Skeleton: `lookup_24` field
- Save/load presets, Kliff gun fix, UP resets all use dmm dicts

**Region Info** — dmm_parser (`region_info`)
- Town/vehicle restriction/wild flags via `_dmm_ref`
- Enable Mounts uses dmm_parser instead of byte offset walking

**Alliance/Faction** — already migrated (previous session)

### Bug Fixes
- Fixed transmog dialog crash when `category` is None
- Fixed spawn filter crash (fnode_ops elements missing `count_offset`)
- Fixed context menu guard skipping terrain elements
- Cleaned up dead `fnode` source code paths

### Technical
- All 7 dmm_parser tables round-trip byte-for-byte
- Field JSON v3 export uses dmm_parser serialization for diffing
- No game-data byte offsets remain in world.py or field_edit.py
