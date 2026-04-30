from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QAbstractItemView, QApplication, QCheckBox, QComboBox, QDialog,
    QDialogButtonBox, QFileDialog, QFrame, QGridLayout, QGroupBox,
    QHBoxLayout, QHeaderView, QInputDialog, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QMenu, QMessageBox, QPushButton,
    QScrollArea, QSizePolicy, QSpinBox, QSplitter, QTableWidget,
    QTableWidgetItem, QTabWidget, QTextEdit, QToolButton, QVBoxLayout,
    QWidget,
)
import textwrap
from paz_patcher import BUFF_HASHES
from gui.theme import COLORS
from icon_cache import ICON_SIZE
from .helpers import make_help_btn

if TYPE_CHECKING:
    from . import ItemBuffsTab

class HelpRowBuilder:
    @staticmethod
    def build(tab: ItemBuffsTab) -> QHBoxLayout:
        help_row = QHBoxLayout()
        help_row.setSpacing(4)
        help_row.addStretch(1)
        help_row.addWidget(make_help_btn("itembuffs", tab._show_guide_fn))
        return help_row

class WarnLabelBuilder:
    @staticmethod
    def build() -> QLabel:
        warn_label = QLabel(
            "\u26A0  Buff and stat names may be inaccurate — they are community-mapped, "
            "not from official game data. Some buffs share numeric keys across different "
            "systems (stats/buffs/passives are 3 separate ID namespaces). "
            "If a name looks wrong, trust the in-game tooltip after applying."
        )
        warn_label.setWordWrap(True)
        warn_label.setStyleSheet(
            f"color: #FFB74D; padding: 6px; font-size: 10px; "
            f"border: 1px solid #5D4037; border-radius: 4px; "
            f"background-color: rgba(93,64,55,0.25);"
        )
        return warn_label

class MoreMenuBuilder:
    @staticmethod
    def build(tab: ItemBuffsTab) -> QMenu:
        more_menu = QMenu(tab)
        more_menu.setToolTipsVisible(True)

        act_sync = more_menu.addAction("Sync Buff Names from GitHub")
        act_sync.setToolTip(
            "Download community-verified buff/stat/passive names.")
        act_sync.triggered.connect(tab._buff_sync_community_names)

        more_menu.addSeparator()
        
        act_verify = more_menu.addAction("Verify Applied Overlay...")
        act_verify.setToolTip(
            "Diagnostics: extract your current overlay and report how many "
            "items actually have each mutation applied. Use after Apply to "
            "Game to confirm the overlay matches expectations.")
        act_verify.triggered.connect(tab._buff_verify_applied_overlay)

        act_restore = more_menu.addAction("Restore Original (remove overlay)")
        act_restore.setToolTip(
            "Undo 'Apply to Game': remove the ItemBuffs PAZ overlay and its "
            "PAPGT entry. Requires admin.")
        act_restore.triggered.connect(tab._buff_restore_original)

        act_reset_vanilla = more_menu.addAction(
            "Reset to Vanilla PAPGT (nuclear)")
        act_reset_vanilla.setToolTip(
            "NUCLEAR RECOVERY: restore first-apply PAPGT snapshot. "
            "Disables ALL overlays. Requires admin.")
        act_reset_vanilla.triggered.connect(tab._buff_reset_vanilla_papgt)
  
        return more_menu

class ActionRowBuilder:
    @staticmethod
    def build(tab: ItemBuffsTab) -> QHBoxLayout:
        action_row = QHBoxLayout()
        action_row.setSpacing(4)

        extract_rust_btn = QPushButton("Extract")
        extract_rust_btn.setObjectName("accentBtn")
        extract_rust_btn.setToolTip("Extract iteminfo from game.\n"
            "Uses existing overlay if present, falls back to vanilla.")
        extract_rust_btn.clicked.connect(tab._buff_extract_rust)
        # action_row.addWidget(extract_rust_btn)

        extract_vanilla_btn = QPushButton("Extract Vanilla")
        extract_vanilla_btn.setToolTip("Always extract from vanilla game files (0008/).\n"
            "Use this after Apply to Game to get a clean baseline.")
        extract_vanilla_btn.clicked.connect(tab._buff_extract_vanilla)
        # action_row.addWidget(extract_vanilla_btn)
        
        extract_menu_btn = QPushButton("Extract")
        # START Extract Menu
        extract_menu = QMenu(tab)
        extract_menu.setToolTipsVisible(True)
        extract_menu_btn.setMenu(extract_menu)
        action_row.addWidget(extract_menu_btn)
        
        act_extract_rust = extract_menu.addAction("Extract Rust")
        act_extract_rust.setToolTip("Extract iteminfo from game.\n"
            "Uses existing overlay if present, falls back to vanilla.")
        act_extract_rust.triggered.connect(tab._buff_extract_rust)

        act_extract_vanilla = extract_menu.addAction("Extract Vanilla")
        act_extract_vanilla.setToolTip("Always extracts from vanilla game files (0008/).\n"
            "Use this after Apply to Game to get a clean baseline.")
        act_extract_vanilla.triggered.connect(tab._buff_extract_vanilla)
        # END Extract Menu


        reset_btn = QPushButton("Undo")
        undo_menu = QMenu(tab)
        undo_menu.addAction("Undo (Ctrl+Z)")
        undo_menu.addAction("Undo All")
        reset_btn.setMenu(undo_menu)
        reset_btn.setObjectName("accentBtn")
        reset_btn.setToolTip("Discard all in-memory changes, re-extract from disk")
        reset_btn.clicked.connect(tab._buff_remove_all)
        action_row.addWidget(reset_btn)

        enable_exports_btn = QPushButton("Enable Exports")
        enable_exports_btn.setStyleSheet(
            "QPushButton { background-color: #6A1B9A; color: white; font-weight: bold; }")
        enable_exports_btn.setToolTip("Enable export features (Dev Mode required)")
        enable_exports_btn.clicked.connect(lambda: tab._require_dev_mode("Enable Exports"))
        # action_row.addWidget(enable_exports_btn)

        apply_game_btn = QPushButton("Apply to Game")
        apply_game_btn.setStyleSheet("QPushButton {"
            "background-color: #B71C1C; color: white; font-weight: bold; }")
        apply_game_btn.setToolTip(
            "Deploy modified iteminfo.pabgb directly to the game.\n"
            "Creates a PAZ overlay — original files are NOT modified.\n"
            "Restart the game for changes to take effect.\n"
            "Use Restore (More ▾) to undo.")
        apply_game_btn.clicked.connect(tab._buff_apply_to_game)
        tab._buff_apply_game_btn = apply_game_btn
        action_row.addWidget(apply_game_btn)

        import_mod_btn = QPushButton("Import")
        import_mod_btn.setStyleSheet("QPushButton {"
            "background-color: #00695C; color: white; font-weight: bold; }")
        
        # START Import Menu
        import_mod_menu = QMenu(tab)
        import_mod_menu.setToolTipsVisible(True)
        import_mod_btn.setMenu(import_mod_menu)
        action_row.addWidget(import_mod_btn)
        
        act_import_config = import_mod_menu.addAction("Import ItemBuffs Config")
        act_import_config.setToolTip(
            "Load a previously saved config file.")
        act_import_config.triggered.connect(tab._buff_load_config)
        
        import_mod_menu.addSeparator()
        
        act_import_json_mod = import_mod_menu.addAction("Import JSON Mod...")
        act_import_json_mod.setToolTip(
            "Import a Pldada/DMM-format JSON byte patch (e.g. Infinity Durability).")
        act_import_json_mod.triggered.connect(tab._buff_import_community_json)
        
        act_import_cdumm_mod = import_mod_menu.addAction("Import CDUMM/PAZ Mod...")
        act_import_cdumm_mod.setToolTip(
            "Reverse-engineer any CDUMM/PAZ mod folder back into an editable "
            "config.\nPoint at a mod's files/gamedata/binary__/client/bin/"
            "iteminfo.pabgb — every modified field becomes editable here.")
        act_import_cdumm_mod.triggered.connect(tab._buff_import_mod_folder)
        # END Import Menu
        
        export_mod_btn = QPushButton("Export")
        export_mod_btn.setStyleSheet("QPushButton {"
            "background-color: #00695C; color: white; font-weight: bold; }")

        export_mod_menu = QMenu(tab)
        export_mod_menu.setToolTipsVisible(True)
        export_mod_btn.setMenu(export_mod_menu)
        action_row.addWidget(export_mod_btn)
        
        # START Export Menu
        # Export buttons are dev-gated (normal users never see them).
        act_export_config = export_mod_menu.addAction("Export ItemBuffs Config")
        act_export_config.setToolTip(
            "Save your current edits as a reusable config file.")
        act_export_config.triggered.connect(tab._buff_save_config)
        

        act_export_field = export_mod_menu.addAction("Export as Field JSON (v3)")
        act_export_field.setToolTip(
            "Export all edits as a Format 3 field-name JSON.\n"
            "Uses field names instead of byte offsets — survives game updates.\n"
            "Compatible with Stacker Tool and future mod loaders.")
        act_export_field.triggered.connect(tab._buff_export_field_json_v3)
        export_mod_menu.addAction(act_export_field)
        
        export_mod_menu.addSeparator()
        
        act_export_mod = export_mod_menu.addAction("Export as Mod Folder")
        act_export_mod.setToolTip(
            "Export as a ready-to-use mod folder (NNNN/0.paz + 0.pamt + meta/0.papgt).\n"
            "Drop the folder into your game directory or import into a mod manager.\n"
            "Same as Apply to Game, but saves to a folder you choose instead.")
        act_export_mod.triggered.connect(tab._buff_export_mod_folder)
        export_mod_menu.addAction(act_export_mod)
        
        act_export_legacy = export_mod_menu.addAction("Export as Legacy JSON (v2)")
        act_export_legacy.setToolTip(
            "Opens Stacker Tool to export as Format 2 byte-diff JSON.\n"
            "Use Pull ItemBuffs Edit in Stacker, then Export Legacy JSON.")
        act_export_legacy.triggered.connect(tab._goto_stacker_legacy_export)   
        # END Export Menu
        
        transmog_btn = QPushButton("Transmog (Armor / Weapon Visual Swap)")
        transmog_btn.setStyleSheet("QPushButton {"
            "background-color: #6A1B9A; color: white; font-weight: bold; }")
        transmog_btn.setToolTip(
            "Visual Transmog for ANY armor or weapon you own.\n\n"
            "• Make your endgame armor look like a fancy starter set\n"
            "• Make your sword look like a legendary weapon you don't have\n"
            "• Mix and match looks per slot — boots from one set, helm from another\n\n"
            "Opens a dialog with quick-filter buttons (Helm, Chest, Sword,\n"
            "Bow, Ring, etc.) so you find the right slot in one click.\n"
            "Stats / buffs / enchants are kept — only the visual model changes.\n\n"
            "Queued swaps apply automatically on Export as Mod or Apply to Game.")
        transmog_btn.clicked.connect(tab._buff_open_transmog_dialog)
        # action_row.addWidget(transmog_btn)

        create_item_btn = QPushButton("⚒ Create Custom Item")
        create_item_btn.setStyleSheet(
            "QPushButton { background-color: #00695C; color: white; "
            "font-weight: bold; font-size: 13px; }")
        create_item_btn.setToolTip(
            "Design a brand-new item by cloning an existing donor.\n\n"
            "• Pick any of 6,000+ game items as a starting point\n"
            "• Edit stats per enchant level, passives, buffs, sockets, gimmicks\n"
            "• Save/Load shareable configs\n"
            "• Two deploy modes:\n"
            "    — Swap to Vendor: replace a vendor item with your stats\n"
            "    — Apply to Game (New Item): mint a brand new key 999001+\n"
            "      with custom localized name\n\n"
            "Use 'Add to Save File' from inside the creator to push the new\n"
            "item into your save without external tools.")
        create_item_btn.clicked.connect(tab._open_item_creator)
        # action_row.addWidget(create_item_btn)

        # Standalone entry into the Add-to-Save dialog without having to
        # re-run Create Item. Scans the current 0058/ overlay for any
        # custom keys (>= 999001) and lets the user pick one to swap
        # into a save-file vendor item. Useful for testing or adding
        # an already-deployed custom item to additional saves.
        add_save_btn = QPushButton("🎒 Add Custom Item to Save")
        add_save_btn.setStyleSheet(
            "QPushButton { background-color: #1565C0; color: white; "
            "font-weight: bold; font-size: 13px; }")
        add_save_btn.setToolTip(
            "Open the Add-to-Save dialog for an ALREADY-deployed custom item.\n"
            "Scans <game>/0058/iteminfo.pabgb for keys in the custom range\n"
            "(999001+) and lets you pick one, then swaps it into a save file\n"
            "vendor/repurchase item — same flow as the Create Item post-apply\n"
            "prompt, but reusable without re-running Create Item.")
        add_save_btn.clicked.connect(tab._open_add_to_save_picker)
        # action_row.addWidget(add_save_btn)

        more_btn = QPushButton("More")
        more_menu = MoreMenuBuilder.build(tab)
        more_btn.setMenu(more_menu)
        action_row.addWidget(more_btn)

        action_row.addWidget(make_help_btn("itembuffs", tab._show_guide_fn))
        action_row.addStretch(1)
        
        credit = QLabel("credit: Potter420 & LukeFZ")
        credit.setStyleSheet("color: #FF5252; font-style: italic; padding: 2px;")
        action_row.addWidget(credit)
        
        return action_row

class SearchRowBuilder:
    @staticmethod
    def build(tab: ItemBuffsTab) -> QHBoxLayout:
        search_row = QHBoxLayout()
        search_row.setSpacing(4)
        tab._buff_search = QLineEdit()
        tab._buff_search.setPlaceholderText("Item name (e.g. Earring, Sword, Necklace)...")
        tab._buff_search.returnPressed.connect(tab._buff_search_items)

        search_btn = QPushButton("Search")
        search_btn.clicked.connect(tab._buff_search_items)

        # Category filter (populated after extract — empty until then)
        tab._buff_category_filter = QComboBox()
        tab._buff_category_filter.setToolTip(
            "Restrict results to items in a specific category.\n"
            "Populated from live iteminfo after Extract.")
        tab._buff_category_filter.setMinimumWidth(180)
        tab._buff_category_filter.addItem("All categories", None)
        tab._buff_category_filter.currentIndexChanged.connect(tab._buff_search_items)

        my_inv_btn = QPushButton("My Inventory")
        my_inv_btn.setToolTip("Show only items from your loaded save that exist in iteminfo")
        my_inv_btn.clicked.connect(tab._buff_show_my_inventory)

        tab._buff_show_icons_btn = QPushButton("Icons")
        tab._buff_show_icons_btn.setToolTip("Toggle item icons in the items list")
        tab._buff_show_icons_btn.clicked.connect(tab._buff_toggle_icons)
        tab._buff_icons_enabled = False

        def toggle_fav():
            tab._buff_items_table.cellChanged.disconnect(toggle_fav)
            tab._showing_favorites = False
        def show_favs():
            if tab._showing_favorites: toggle_fav()
            tab._showing_favorites = True
            tab._show_similar_items({"key": 0},"favorites")
            tab._buff_items_table.cellChanged.connect(toggle_fav)
        tab._show_favorite_items = show_favs

        fav_btn = QPushButton("⭐")
        fav_btn.setToolTip("Show favorited items only")
        fav_btn.clicked.connect(show_favs)
        tab._showing_favorites = False

        search_row.addWidget(fav_btn)
        search_row.addWidget(QLabel("Search:"))
        search_row.addWidget(tab._buff_search, 1)
        search_row.addWidget(search_btn)
        search_row.addWidget(tab._buff_category_filter)
        # search_row.addWidget(desc_search_btn)
        search_row.addWidget(my_inv_btn)
        search_row.addWidget(tab._buff_show_icons_btn)
        
        return search_row

class ItemsFrameBuilder:
    @staticmethod
    def build(tab: ItemBuffsTab) -> QFrame:
        items_frame = QFrame()
        items_vlayout = QVBoxLayout(items_frame)
        items_vlayout.setContentsMargins(0, 0, 0, 0)
        items_vlayout.setSpacing(2)
        items_vlayout.addWidget(QLabel("Matching Items:"))
        tab._buff_items_table = QTableWidget()
        tab._buff_items_table.setColumnCount(6)
        tab._buff_items_table.setHorizontalHeaderLabels(["", "Name", "Type", "Tier", "Enchants", "Stack"])
        tab._buff_items_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        tab._buff_items_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        tab._buff_items_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        hdr_items = tab._buff_items_table.horizontalHeader()
        hdr_items.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        tab._buff_items_table.setColumnWidth(0, 0)
        hdr_items.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        tab._buff_items_table.setColumnWidth(1, 180)
        hdr_items.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        tab._buff_items_table.setColumnWidth(2, 70)
        hdr_items.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        tab._buff_items_table.setColumnWidth(3, 70)
        hdr_items.setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)
        tab._buff_items_table.setColumnWidth(4, 70)
        hdr_items.setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive)
        tab._buff_items_table.setColumnWidth(5, 50)
        hdr_items.setStretchLastSection(False)
        tab._buff_items_table.verticalHeader().setDefaultSectionSize(24)
        tab._buff_items_table.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
        tab._buff_items_table.setSortingEnabled(True)
        tab._buff_items_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        tab._buff_items_table.customContextMenuRequested.connect(tab._buff_items_context_menu)
        tab._buff_items_table.selectionModel().selectionChanged.connect(
            tab._buff_item_selected
        )
        tab._buff_items_table.setMinimumHeight(120)
        tab._buff_items_table.setColumnHidden(2, True)
        tab._buff_items_table.setColumnHidden(4, True)
        tab._buff_items_table.setColumnHidden(5, True)
        items_vlayout.addWidget(tab._buff_items_table, 1)
        items_frame.setMinimumWidth(120)
        # items_frame.setMaximumWidth(280)
        return items_frame

class StatsTableFrameBuilder:
    @staticmethod
    def build(tab: ItemBuffsTab) -> QFrame:
        stats_table_frame = QFrame()
        stf_layout = QVBoxLayout(stats_table_frame)
        stf_layout.setContentsMargins(0, 0, 0, 0)
        stf_layout.setSpacing(2)
        tab._buff_selected_label = QLabel("No item selected — search and click an item on the left")
        tab._buff_selected_label.setStyleSheet(
            f"color: {COLORS['text_dim']}; font-weight: bold; padding: 2px 4px;"
        )
        stf_layout.addWidget(tab._buff_selected_label)
        stf_layout.addWidget(QLabel("Current Stats / Buffs:"))
        tab._buff_stats_table = QTableWidget()
        tab._buff_stats_table.setColumnCount(2)
        tab._buff_stats_table.setHorizontalHeaderLabels([
            "Stat/Buff", "Value",
        ])
        tab._buff_stats_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        tab._buff_stats_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        tab._buff_stats_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        tab._buff_stats_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        tab._buff_stats_table.customContextMenuRequested.connect(tab._buff_stats_context_menu)
        hdr_stats = tab._buff_stats_table.horizontalHeader()
        hdr_stats.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        tab._buff_stats_table.setColumnWidth(0, 240)
        hdr_stats.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        tab._buff_stats_table.setColumnWidth(1, 100)
        hdr_stats.setStretchLastSection(False)
        tab._buff_stats_table.verticalHeader().setDefaultSectionSize(24)
        tab._buff_stats_table.setMinimumHeight(100)
        stf_layout.addWidget(tab._buff_stats_table, 1)
        stats_table_frame.setMinimumHeight(120)
        stats_table_frame.setMinimumWidth(120)
        return stats_table_frame
    
class BuffActionTabsBuilder:
    def __init__(self, tab: ItemBuffsTab):
        self.tab = tab

    def build(self) -> None:
        tab = self.tab
        # ══════════════════════════════════════════════════════════════════
        # Action tabs — replaces the old scrollable controls panel and the
        # third-column "right panel". All the ~35 control rows that used to
        # be crammed into one scrollarea now live in a QTabWidget with 8
        # focused sub-tabs. Every widget attribute name (_buff_*, _eb_*,
        # _stack_check, _inf_dura_check, _buff_overlay_spin, etc.) is
        # preserved so existing handlers continue to reference them.
        #
        # Layout now: two-column horizontal splitter — items list | stats/tabs.
        # The old third "_buff_right_panel" is kept as an empty widget for
        # backwards compatibility; nothing is added to it.
        # ══════════════════════════════════════════════════════════════════

        # Build the QTabWidget and its 8 sub-pages via helper methods.
        tab._buff_action_tabs = QTabWidget()
        tab._buff_action_tabs.setMinimumHeight(220)
        tab._buff_action_tabs.setMinimumWidth(120)
        tab._buff_action_tabs.addTab(
            self._build_buff_testing_page(), "Testing")
        tab._buff_action_tabs.addTab(
            self._build_buff_hero_presets_page(), "Presets")
        tab._buff_action_tabs.addTab(
            self._build_buff_quick_edit_page(), "Quick Edit")
        tab._buff_action_tabs.addTab(
            self._build_buff_drop_data_page(), "Drop Data")
        tab._buff_action_tabs.addTab(
            self._build_buff_effects_page(), "Passives & Effects")
        tab._buff_action_tabs.addTab(
            self._build_buff_stats_page(), "Stats & Buffs")
        tab._buff_action_tabs.addTab(
            self._build_buff_imbue_page(), "Imbue")
        tab._buff_action_tabs.addTab(
            self._build_buff_global_mods_page(), "Global Mods")
        tab._buff_action_tabs.addTab(
            self._build_buff_bulk_page(), "Bulk Actions")
        tab._buff_action_adv_idx = tab._buff_action_tabs.count()
        tab._buff_action_tabs.addTab(
            self._build_buff_advanced_page(), "Advanced")
        # tab_test_idx = tab._buff_action_tabs.count()

        # Advanced tab hidden unless dev/experimental mode is on.
        tab._buff_action_tabs.setTabVisible(
            tab._buff_action_adv_idx, tab._experimental_mode)

    def _build_buff_testing_page(self) -> QWidget:
        tab = self.tab
        page = QWidget()
        pl = QVBoxLayout(page)
        pl.setContentsMargins(8, 8, 8, 8)
        pl.setSpacing(6)

        return page

    def _build_buff_quick_edit_page(self) -> QWidget:
        tab = self.tab
        """Quick Edit sub-tab — preset, custom row, edit-selected stat."""
        page = QWidget()
        pl = QVBoxLayout(page)
        pl.setContentsMargins(8, 8, 8, 8)
        pl.setSpacing(6)

        preset_row = QHBoxLayout()
        preset_row.setSpacing(4)
        preset_row.addWidget(QLabel("Preset:"))
        tab._buff_preset_combo = QComboBox()
        tab._buff_preset_combo.addItems([
            "Max All (max every stat value, no hash changes)",
            "Max All Flat (max value on all flat stat entries)",
            "Max DDD (max value on flat2 entries)",
            "Max DPV (max value on flat2 entries)",
            "Max HP (max value on flat1 entries)",
            "Max All Rates (max value on all rate entries)",
            "Swap to DDD (change flat2 hashes to Damage)",
            "Swap to DPV (change flat2 hashes to Defense)",
            "Custom (pick stat + value)",
        ])
        tab._buff_preset_combo.currentIndexChanged.connect(tab._buff_preset_changed)
        preset_row.addWidget(tab._buff_preset_combo, 1)

        apply_preset_btn = QPushButton("Apply Preset")
        apply_preset_btn.setObjectName("accentBtn")
        apply_preset_btn.clicked.connect(tab._buff_add_to_item)
        preset_row.addWidget(apply_preset_btn)

        suggest_btn = QPushButton("Suggest from Cluster")
        suggest_btn.setToolTip(
            "Show the stat template typical for items like the one selected "
            "(same item_type + tier). Read-only.")
        suggest_btn.clicked.connect(tab._buff_show_stat_template)
        preset_row.addWidget(suggest_btn)

        reset_btn = QPushButton("Reset")
        reset_btn.setToolTip("Discard all in-memory changes, re-extract from disk")
        reset_btn.clicked.connect(tab._buff_remove_all)
        preset_row.addWidget(reset_btn)
        pl.addLayout(preset_row)

        # Custom stat row (hidden unless "Custom" preset selected).
        tab._buff_custom_row = QWidget()
        custom_layout = QHBoxLayout(tab._buff_custom_row)
        custom_layout.setContentsMargins(0, 0, 0, 0)
        custom_layout.setSpacing(4)
        custom_layout.addWidget(QLabel("Stat:"))
        tab._buff_type_combo = QComboBox()
        for name in BUFF_HASHES:
            tab._buff_type_combo.addItem(name)
        custom_layout.addWidget(tab._buff_type_combo, 1)
        custom_layout.addWidget(QLabel("Value:"))
        tab._buff_value_spin = QSpinBox()
        tab._buff_value_spin.setRange(0, 999999999)
        tab._buff_value_spin.setValue(1000000)
        tab._buff_value_spin.setToolTip(
            "Flat stats (HP/DDD/DPV): use large values like 1,000,000\n"
            "Rate stats: 1 byte, 0-255 (max varies per stat type)\n"
            "Invincible: 1 = on, 0 = off")
        custom_layout.addWidget(tab._buff_value_spin)
        tab._buff_custom_row.setVisible(False)
        pl.addWidget(tab._buff_custom_row)

        # Edit-Selected-Stat + Refinement Level row.
        edit_refine_row = QHBoxLayout()
        edit_refine_row.setSpacing(4)
        edit_refine_row.addWidget(QLabel("Edit Stat:"))
        tab._buff_sel_value_spin = QSpinBox()
        tab._buff_sel_value_spin.setRange(0, 999999999)
        tab._buff_sel_value_spin.setValue(0)
        tab._buff_sel_value_spin.setToolTip(
            "Set the value for the selected base stat "
            "(Attack/Defense/DDD/DPV/HP etc.)")
        edit_refine_row.addWidget(tab._buff_sel_value_spin)

        edit_sel_btn = QPushButton("Apply to Stat")
        edit_sel_btn.setToolTip("Change ONLY the clicked base stat")
        edit_sel_btn.clicked.connect(tab._buff_apply_to_selected)
        edit_refine_row.addWidget(edit_sel_btn)

        tab._buff_sel_label = QLabel("")
        tab._buff_sel_label.setStyleSheet(f"color: {COLORS['accent']};")
        edit_refine_row.addWidget(tab._buff_sel_label, 1)

        edit_refine_row.addWidget(QLabel("Refine:"))
        tab._buff_array_combo = QComboBox()
        tab._buff_array_combo.addItem("All Levels (apply to every array)")
        tab._buff_array_combo.setToolTip(
            "Select which refinement level to apply presets to.\n"
            "'All Levels' applies to every array (default).")
        edit_refine_row.addWidget(tab._buff_array_combo)
        pl.addLayout(edit_refine_row)

        # Kept as empty widgets for any legacy API references.
        tab._buff_edit_selected_row = QWidget()
        tab._buff_array_row = QWidget()

        # Connect stat-table selection to the edit-selected controls.
        tab._buff_stats_table.selectionModel().selectionChanged.connect(
            tab._buff_on_stat_selected)

        # Description label (compact, hidden by default).
        tab._buff_desc_label = QLabel()
        tab._buff_desc_label.setWordWrap(True)
        tab._buff_desc_label.setStyleSheet(
            f"color: {COLORS['text_dim']}; padding: 2px; font-size: 10px;"
        )
        tab._buff_desc_label.setVisible(False)
        tab._buff_preset_combo.currentIndexChanged.connect(tab._buff_update_desc)
        tab._buff_type_combo.currentTextChanged.connect(tab._buff_update_desc)
        tab._buff_update_desc()
        pl.addWidget(tab._buff_desc_label)
        
        pl.addWidget(tab._ui_add_line(True))
        
        # --- Socket count ---
        tab._eb_socket_row_widget = QWidget()
        socket_row = QHBoxLayout(tab._eb_socket_row_widget)
        socket_row.setContentsMargins(0, 0, 0, 0)
        socket_row.setSpacing(6)
        socket_row.addWidget(QLabel("Count:"))
        tab._eb_socket_count = QSpinBox()
        tab._eb_socket_count.setRange(1, 8)
        tab._eb_socket_count.setValue(5)
        tab._eb_socket_count.setFixedWidth(60)
        tab._eb_socket_count.setToolTip(
            "Target max socket count. Writes to drop_default_data."
            "add_socket_material_item_list.")
        socket_row.addWidget(tab._eb_socket_count)
        socket_row.addWidget(QLabel("Pre-unlocked:"))
        tab._eb_socket_valid = QSpinBox()
        tab._eb_socket_valid.setRange(0, 8)
        tab._eb_socket_valid.setValue(0)
        tab._eb_socket_valid.setFixedWidth(60)
        tab._eb_socket_valid.setToolTip(
            "How many sockets are unlocked on drop. Extra sockets need to "
            "be unlocked at the Witch NPC.")
        socket_row.addWidget(tab._eb_socket_valid)
        socket_apply_btn = QPushButton("Extend Sockets (Selected)")
        socket_apply_btn.setToolTip(
            "Extend socket capacity on the SELECTED item. Only applies to "
            "items with use_socket=1 (abyss gear).")
        socket_apply_btn.clicked.connect(tab._eb_extend_sockets)
        socket_row.addWidget(socket_apply_btn)
        socket_row.addStretch(1)
        pl.addWidget(tab._eb_socket_row_widget)
        
        # --- Drop enchant level ---
        drop_enchant = QWidget()
        drop_enchant_row = QHBoxLayout(drop_enchant)
        drop_enchant_row.setContentsMargins(0, 0, 0, 0)
        drop_enchant_row.setSpacing(6)
        drop_enchant_row.addWidget(QLabel("Enchant Level:"))
        tab._eb_drop_enchant_level = QSpinBox()
        tab._eb_drop_enchant_level.setRange(0, 10)
        tab._eb_drop_enchant_level.setValue(0)
        tab._eb_drop_enchant_level.setFixedWidth(60)
        tab._eb_drop_enchant_level.setToolTip(
            "What refinement level the item will be on drop.")
        drop_enchant_row.addWidget(tab._eb_drop_enchant_level)
        drop_enchant_apply = QPushButton("Change Drop Level (Selected)")
        drop_enchant_apply.setToolTip(
            "Change the default enchantment level for the SELECTED item "
            "when it drops or is purchased.")
        drop_enchant_apply.clicked.connect(tab._eb_change_drop_enchant)
        drop_enchant_row.addWidget(drop_enchant_apply)
        drop_enchant_row.addStretch(1)
        pl.addWidget(drop_enchant)

        pl.addStretch(1)
        return page
        tab = self.tab

    def _build_buff_effects_page(self) -> QWidget:
        tab = self.tab
        """Passives & Effects sub-tab — passive combo, effect catalog, gimmick."""
        from PySide6.QtWidgets import QFormLayout, QCompleter
        page = QWidget()
        form = QFormLayout(page)
        form.setContentsMargins(8, 8, 8, 8)
        form.setSpacing(6)
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        # Passive row
        passive_container = QWidget()
        passive_row = QHBoxLayout(passive_container)
        passive_row.setContentsMargins(0, 0, 0, 0)
        passive_row.setSpacing(4)
        tab._eb_passive_combo = QComboBox()
        tab._eb_passive_combo.setToolTip(
            "Change the passive skill on this item. Green text on tooltips.")
        tab._eb_passive_combo.setMinimumWidth(200)
        tab._eb_passive_combo.setEditable(True)
        tab._eb_passive_combo.setInsertPolicy(QComboBox.NoInsert)
        tab._eb_passive_combo.lineEdit().setPlaceholderText("Type to search passives...")
        tab._eb_passive_combo.completer().setCompletionMode(QCompleter.PopupCompletion)
        tab._eb_passive_combo.completer().setFilterMode(Qt.MatchContains)
        for sk in sorted(tab._PASSIVE_SKILL_NAMES.keys()):
            name = tab._PASSIVE_SKILL_NAMES[sk]
            desc = tab._buff_skill_descs.get(str(sk), {}).get("description", "")
            label = f"{name} ({sk})" + (f" \u2014 {desc}" if desc else "")
            tab._eb_passive_combo.addItem(label, sk)
        passive_row.addWidget(tab._eb_passive_combo, 1)

        passive_row.addWidget(QLabel("Lv:"))
        tab._eb_level_spin = QSpinBox()
        tab._eb_level_spin.setRange(1, 100)
        tab._eb_level_spin.setValue(1)
        tab._eb_level_spin.setToolTip("Passive level (shown as 'Lv X' in-game)")
        tab._eb_level_spin.setMinimumWidth(60)
        passive_row.addWidget(tab._eb_level_spin)

        add_pass_btn = QPushButton("Add")
        add_pass_btn.setObjectName("accentBtn")
        add_pass_btn.setToolTip(
            "ADD a passive skill to this item (stacks with existing passives).")
        add_pass_btn.clicked.connect(tab._eb_apply)
        passive_row.addWidget(add_pass_btn)

        remove_pass_btn = QPushButton("Remove")
        remove_pass_btn.setToolTip("Remove selected passive from this item")
        remove_pass_btn.clicked.connect(tab._eb_remove_passive)
        passive_row.addWidget(remove_pass_btn)

        god_mode_btn = QPushButton("God Mode")
        god_mode_btn.setToolTip(
            "Inject full God Mode stats: Invincible + Great Thief, max DDD/DPV, "
            "max regen, max speed/crit/resist, 8 equipment buffs.")
        god_mode_btn.setStyleSheet(
            "background-color: #cc3333; color: white; font-weight: bold;")
        god_mode_btn.clicked.connect(tab._eb_god_mode)
        passive_row.addWidget(god_mode_btn)

        tab._eb_status = QLabel("")
        tab._eb_status.setStyleSheet(f"color: {COLORS['accent']};")
        passive_row.addWidget(tab._eb_status)
        form.addRow("Passive:", passive_container)

        # Effect row: search + catalog + apply
        effect_container = QWidget()
        effect_row = QHBoxLayout(effect_container)
        effect_row.setContentsMargins(0, 0, 0, 0)
        effect_row.setSpacing(4)
        tab._effect_search = QLineEdit()
        tab._effect_search.setPlaceholderText("shadow, lightning, boot...")
        tab._effect_search.setToolTip(
            "Filter effects by name, gimmick, skill ID, or source item.")
        tab._effect_search.setMaximumWidth(200)
        tab._effect_search.textChanged.connect(tab._effect_filter_changed)
        effect_row.addWidget(tab._effect_search)

        tab._effect_catalog_combo = QComboBox()
        tab._effect_catalog_combo.setToolTip(
            "Pick a gimmick effect from an existing in-game item.\n"
            "Copies gimmick_info, docking, cooltime, passive skills.")
        tab._effect_catalog_combo.setMinimumWidth(220)
        tab._effect_catalog_combo.addItem("(load item data first)", None)
        effect_row.addWidget(tab._effect_catalog_combo, 1)

        copy_effect_btn = QPushButton("Apply Effect")
        copy_effect_btn.setObjectName("accentBtn")
        copy_effect_btn.setToolTip(
            "Apply the selected gimmick effect to the current item.\n"
            "Passives STACK; gimmick/docking REPLACES (one per item).")
        copy_effect_btn.clicked.connect(tab._eb_copy_effect)
        effect_row.addWidget(copy_effect_btn)
        form.addRow("Effect:", effect_container)

        # Gimmick row: searchable combo + Apply + user-preview label
        gimmick_container = QWidget()
        gl = QVBoxLayout(gimmick_container)
        gl.setContentsMargins(0, 0, 0, 0)
        gl.setSpacing(2)
        gimmick_row = QHBoxLayout()
        gimmick_row.setSpacing(4)
        tab._eb_vfx_combo = QComboBox()
        tab._eb_vfx_combo.setEditable(True)
        tab._eb_vfx_combo.setInsertPolicy(QComboBox.NoInsert)
        tab._eb_vfx_combo.lineEdit().setPlaceholderText(
            "Search gimmicks (lantern, lightning, flame, drone, thief...)")
        tab._eb_vfx_combo.setMinimumWidth(220)
        tab._eb_vfx_combo.setSizeAdjustPolicy(
            QComboBox.AdjustToMinimumContentsLengthWithIcon)
        tab._eb_vfx_combo.setToolTip(
            "Attach any equip-gimmick to the current item. Clones gimmick_info, "
            "docking_child_data, cooltime, charge config from a sample item.")
        tab._eb_vfx_combo.completer().setCompletionMode(QCompleter.PopupCompletion)
        tab._eb_vfx_combo.completer().setFilterMode(Qt.MatchContains)
        tab._load_vfx_catalog_into_combo()
        gimmick_row.addWidget(tab._eb_vfx_combo, 1)

        apply_gimmick_btn = QPushButton("Apply Gimmick")
        apply_gimmick_btn.setStyleSheet(
            "background-color: #006064; color: white; font-weight: bold;")
        apply_gimmick_btn.setToolTip(
            "Apply the selected gimmick to the current item.\n"
            "Replaces any existing gimmick slot — one gimmick per item.")
        apply_gimmick_btn.clicked.connect(tab._eb_apply_vfx_gimmick)
        gimmick_row.addWidget(apply_gimmick_btn)
        gl.addLayout(gimmick_row)

        # Live preview of which vanilla items already use the selected gimmick.
        tab._eb_vfx_users_label = QLabel("")
        tab._eb_vfx_users_label.setStyleSheet(
            f"color: {COLORS['text_dim']}; font-size: 10px; padding: 1px 4px;")
        tab._eb_vfx_users_label.setWordWrap(True)
        gl.addWidget(tab._eb_vfx_users_label)
        tab._eb_vfx_combo.currentIndexChanged.connect(
            lambda _i: tab._refresh_gimmick_user_label())
        form.addRow("Gimmick:", gimmick_container)

        return page
        tab = self.tab

    def _build_buff_stats_page(self) -> QWidget:
        tab = self.tab
        """Stats & Buffs sub-tab — enchant level + stat + equip buff rows."""
        from PySide6.QtWidgets import QFormLayout, QCompleter
        page = QWidget()
        form = QFormLayout(page)
        form.setContentsMargins(8, 8, 8, 8)
        form.setSpacing(6)
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        # Enchant level row
        level_container = QWidget()
        level_row = QHBoxLayout(level_container)
        level_row.setContentsMargins(0, 0, 0, 0)
        level_row.setSpacing(4)
        tab._eb_level_target = QComboBox()
        tab._eb_level_target.addItem("All Levels (0-10)", -1)
        for i in range(11):
            tab._eb_level_target.addItem(f"Level +{i} only", i)
        tab._eb_level_target.setToolTip(
            "Which enchant level(s) to apply stat/buff changes to. Items have "
            "11 enchant levels (0-10). 'All Levels' applies to every one.")
        tab._eb_level_target.setFixedWidth(180)
        tab._eb_level_target.currentIndexChanged.connect(
            lambda: tab._buff_refresh_stats() if tab._buff_current_item else None)
        level_row.addWidget(tab._eb_level_target)
        hint = QLabel("Pick level \u2192 Add stats/buffs \u2192 Apply to Game")
        hint.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 10px;")
        level_row.addWidget(hint, 1)
        form.addRow("Enchant level:", level_container)

        # Stat row
        stat_container = QWidget()
        stat_row = QHBoxLayout(stat_container)
        stat_row.setContentsMargins(0, 0, 0, 0)
        stat_row.setSpacing(4)
        tab._eb_stat_combo = QComboBox()
        tab._eb_stat_combo.setEditable(True)
        tab._eb_stat_combo.setInsertPolicy(QComboBox.NoInsert)
        tab._eb_stat_combo.lineEdit().setPlaceholderText("Type to search stats...")
        tab._eb_stat_combo.completer().setCompletionMode(QCompleter.PopupCompletion)
        tab._eb_stat_combo.completer().setFilterMode(Qt.MatchContains)
        for idx, (sname, skey, slist, sdefault) in enumerate(tab._ENCHANT_STAT_LIST):
            label_type = slist.replace('stat_list_', '').replace('_', ' ')
            tab._eb_stat_combo.addItem(f"{sname} [{label_type}] ({skey})", idx)
        stat_row.addWidget(tab._eb_stat_combo, 1)

        stat_row.addWidget(QLabel("Val:"))
        tab._eb_stat_value = QSpinBox()
        tab._eb_stat_value.setRange(0, 999999999)
        tab._eb_stat_value.setValue(999999)
        tab._eb_stat_value.setToolTip(
            "Flat stats (DDD/DPV): 999,999 = strong, 1,000,000 = dev ring\n"
            "Rate stats (Speed/Crit): 0-15 where 15 = max\n"
            "Regen: 100,000 = very fast, 1,000,000 = dev ring")
        tab._eb_stat_value.setMinimumWidth(100)
        stat_row.addWidget(tab._eb_stat_value)

        stat_add_btn = QPushButton("Add Stat")
        stat_add_btn.setObjectName("accentBtn")
        stat_add_btn.setToolTip(
            "Add this stat to ALL enchant levels (structural edit)")
        stat_add_btn.clicked.connect(tab._eb_add_stat)
        stat_row.addWidget(stat_add_btn)

        stat_remove_btn = QPushButton("Remove")
        stat_remove_btn.setToolTip("Remove this stat from ALL enchant levels")
        stat_remove_btn.clicked.connect(tab._eb_remove_stat)
        stat_row.addWidget(stat_remove_btn)
        form.addRow("Stat:", stat_container)

        # Equip buff row
        buff_container = QWidget()
        eb_row = QHBoxLayout(buff_container)
        eb_row.setContentsMargins(0, 0, 0, 0)
        eb_row.setSpacing(4)
        tab._eb_buff_combo = QComboBox()
        tab._eb_buff_combo.setToolTip(
            "Select an equipment buff to add to ALL enchant levels.\n"
            "Colored effects on items (Fire Res, Ice Res, etc).")
        tab._eb_buff_combo.setMinimumWidth(200)
        tab._eb_buff_combo.setEditable(True)
        tab._eb_buff_combo.setInsertPolicy(QComboBox.NoInsert)
        tab._eb_buff_combo.lineEdit().setPlaceholderText("Type to search buffs...")
        tab._eb_buff_combo.completer().setCompletionMode(QCompleter.PopupCompletion)
        tab._eb_buff_combo.completer().setFilterMode(Qt.MatchContains)
        for bk in sorted(tab._EQUIP_BUFF_NAMES.keys()):
            bname = tab._EQUIP_BUFF_NAMES[bk]
            desc = tab._buff_skill_descs.get(str(bk), {}).get("description", "")
            label = f"{bname} ({bk})" + (f" \u2014 {desc}" if desc else "")
            tab._eb_buff_combo.addItem(label, bk)
        tab._eb_buff_combo.currentIndexChanged.connect(tab._buff_on_buff_selected)
        eb_row.addWidget(tab._eb_buff_combo, 1)

        eb_row.addWidget(QLabel("Lv:"))
        tab._eb_buff_level = QSpinBox()
        tab._eb_buff_level.setRange(0, 100)
        tab._eb_buff_level.setValue(15)
        tab._eb_buff_level.setToolTip("Buff level (0-100, 15 = max for most buffs)")
        tab._eb_buff_level.setMinimumWidth(60)
        eb_row.addWidget(tab._eb_buff_level)

        tab._buff_range_label = QLabel("")
        tab._buff_range_label.setStyleSheet(
            f"color: {COLORS['text_dim']}; font-size: 10px;")
        eb_row.addWidget(tab._buff_range_label)

        eb_add_btn = QPushButton("Add Buff")
        eb_add_btn.setObjectName("accentBtn")
        eb_add_btn.setToolTip(
            "Add this equipment buff to ALL enchant levels of the selected item")
        eb_add_btn.clicked.connect(tab._eb_add_buff)
        eb_row.addWidget(eb_add_btn)

        eb_remove_btn = QPushButton("Remove Buff")
        eb_remove_btn.setToolTip(
            "Remove this buff from ALL enchant levels of the selected item")
        eb_remove_btn.clicked.connect(tab._eb_remove_buff)
        eb_row.addWidget(eb_remove_btn)
        form.addRow("Equip Buff:", buff_container)

        return page
        tab = self.tab

    def _build_buff_drop_data_page(self) -> QWidget:
        tab = self.tab
        page = QWidget()
        pl = QVBoxLayout(page)
        pl.setContentsMargins(8, 8, 8, 8)
        pl.setSpacing(8)
        return page

    def _build_buff_hero_presets_page(self) -> QWidget:
        tab = self.tab
        """Hero Presets sub-tab — 3 large colored buttons."""
        
        # TEMP styles array
        styles = [
            ("#4682B4","White"),
            ("#FFFFFF","Black"),
            ("#00FF7F","Black"),
            ("#00BFFF","Black"),
            ("#9370DB","Black"),
            ("#DC143C","White"),
            ("#778899","Black"),
            ("#FFD700","Black"),
            ("#FF69B4","Black"),
            ("#FF8C00","Black"),
            ("#00FFFF","Black"),
            ("#7FFF00","Black"),
            ("#DDA0DD","Black"),
            ("#2E8B57","White"),
        ]   
        
        def gen_styles(font_color: str, bkg_color: str):
            return textwrap.dedent(f"""
            QPushButton, QToolTip {{
                font-size: 13px;
                font-weight: bold;
            }}
            
            QPushButton {{
                color: {font_color};
                background-color: {bkg_color};
                padding: 16px 24px;
            }}
            
            QToolTip {{
                color: black;
                background-color: white;
                border: 1px solid black;
            }}
            """).strip()
        
        page = QWidget()
        pl = QVBoxLayout(page)
        pl.setContentsMargins(8, 8, 8, 8)
        pl.setSpacing(8)

        grid = QGridLayout()
        grid.setSpacing(8)
        grid_columns = 3
        grid_buttons: list[QPushButton] = []
        grid_label = QLabel(
            "One-click presets. Click an item in the list, "
            "then choose a preset below to apply.")
        
        dev_grid = QGridLayout()
        dev_grid.setSpacing(8)
        dev_grid_buttons: list[QPushButton] = []
        dev_grid_label = QLabel(
            "DEV Ring presets. Click an item in the list, "
            "then choose a preset below to apply.")

        custom_grid = QGridLayout()
        custom_grid.setSpacing(8)
        custom_grid_buttons: list[QPushButton] = []
        custom_grid_label = QLabel("")
      
        sockets_btn = QPushButton("5 Sockets")
        sockets_btn.setToolTip("Item will drop with 5 open sockets by default.")
        sockets_btn.clicked.connect(
            lambda: tab._eb_apply_preset("open_sockets"))
        grid_buttons.append(sockets_btn)
        
        enchant_btn = QPushButton("Max Refine")
        enchant_btn.setToolTip("Item will drop at lvl 10 by default.")
        enchant_btn.clicked.connect(
            lambda: tab._eb_apply_preset("max_enchant"))
        grid_buttons.append(enchant_btn)
        
        cooldown_btn = QPushButton("No Cooldown")
        cooldown_btn.setToolTip("Item will have 1s cooldown by default.")
        cooldown_btn.clicked.connect(
            lambda: tab._eb_apply_preset("no_cooldown"))
        grid_buttons.append(cooldown_btn)
        
        charges_btn = QPushButton("Max Charges")
        charges_btn.setToolTip("Item will have 100 charges by default.")
        charges_btn.clicked.connect(
            lambda: tab._eb_apply_preset("max_charges"))
        grid_buttons.append(charges_btn)
        stacks_btn = QPushButton("Max Stacks")
        stacks_btn.setToolTip("Item will have a max stack size of 999999.")
        stacks_btn.clicked.connect(
            lambda: tab._eb_apply_preset("max_stacks"))
        grid_buttons.append(stacks_btn)
        godmode_desc = textwrap.dedent("""
            - No Cooldown   
            - Max Charges
            - Max Sockets
            - Max Enchant
            - Invincible
            - Great Thief (All Crimes)
            - Max Attack/Defense
            - Max Attack/Move Speed
            - Max Regen
            - Max Crit/Resist
            - 8 Equipment Buffs at level 10
        """).strip()
        def apply_godmode():
            if not hasattr(tab, '_buff_rust_items') or not tab._buff_rust_items:
                QMessageBox.warning(tab, "God Mode", "Extract with Rust parser first.")
                return
            if not hasattr(tab, '_buff_current_item') or tab._buff_current_item is None:
                QMessageBox.warning(tab, "God Mode", "Select an item first.")
                return

            rust_info = tab._buff_rust_lookup.get(tab._buff_current_item.item_key)
            if not rust_info:
                QMessageBox.warning(tab, "God Mode", "Item not found in Rust data.")
                return

            edl = rust_info.get('enchant_data_list', [])
            if not edl:
                QMessageBox.warning(tab, "God Mode",
                    "This item has no enchant data.\n"
                    "Only equippable items (weapons, armor, accessories) can have buffs.")
                return

            display_name = tab._name_db.get_name(tab._buff_current_item.item_key)

            reply = QMessageBox.warning(
                tab, "Potter's God Mode",
                f"Apply God Mode to {display_name}?\n\n"
                f"This will inject into ALL enchant levels:\n"
                f"{godmode_desc}\n\n"
                f"Click 'Export as Mod' after to write.",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return
            tab._eb_god_mode(True)
            tab._eb_apply_preset("great_thief_all", True)
            tab._eb_apply_preset("open_sockets", True)
            tab._eb_apply_preset("max_charges", True)
            tab._eb_apply_preset("max_enchant", True)
            tab._eb_apply_preset("no_cooldown", True)
        godmode_btn = QPushButton("God Mode")
        godmode_btn.setToolTip(f"Inject full God Mode stats:\n{godmode_desc}")
        godmode_btn.clicked.connect(apply_godmode)
        grid_buttons.append(godmode_btn)
        
        shadow_boots_btn = QPushButton("Shadow Boots")
        shadow_boots_btn.setToolTip(
            "Apply Potter's Shadow Boots config to selected item:\n"
            "Skills: Shadow Dash (7201) + Breeze Step (7055) + Swimming (7202)\n"
            "Gimmick: 1004431 (boots gimmick — activates the skills)")
        shadow_boots_btn.clicked.connect(
            lambda: tab._eb_apply_preset("shadow_boots"))
        grid_buttons.append(shadow_boots_btn)

        lightning_btn = QPushButton("Lightning Weapon")
        lightning_btn.setToolTip(
            "Apply lightning weapon config (Potter's Hwando recipe):\n"
            "Skills: Lightning (91101) + Fire (91105) + Ice (91104) affinity\n"
            "Gimmick: 1001961 (weapon gimmick)")
        lightning_btn.clicked.connect(
            lambda: tab._eb_apply_preset("lightning_weapon"))
        grid_buttons.append(lightning_btn)
        
        great_thief_btn = QPushButton("Great Thief")
        great_thief_btn.setToolTip(
            "Apply Great Thief activated skill (works on ANY item).\n"
            "Opens a picker: Block Theft only, or Block ALL crime.\n"
            "Gimmick: 1002041, 1 charge, 30-min cooldown.")
        great_thief_btn.clicked.connect(tab._eb_great_thief_pick_variant)
        grid_buttons.append(great_thief_btn)
        
        dev_immunity_btn = QPushButton("Immunity")
        dev_immunity_btn.setToolTip("Adds DEV Immune Ring buff to item.")
        dev_immunity_btn.clicked.connect(
            lambda: tab._eb_apply_dev_preset("immune"))
        dev_grid_buttons.append(dev_immunity_btn)
        
        dev_str_hp_btn = QPushButton("STR/HP")
        dev_str_hp_btn.setToolTip(
            "Inject DEV STR/HP Ring stats:\n"
            "- Max DDD (Damage)\n"
            "- Max HP Regen")
        dev_str_hp_btn.clicked.connect(
            lambda: tab._eb_apply_dev_preset("str_hp"))
        dev_grid_buttons.append(dev_str_hp_btn)

        dev_def_hp_btn = QPushButton("DEF/HP")
        dev_def_hp_btn.setToolTip(
            "Inject DEV DEF/HP Ring stats:\n"
            "- Max DPV (Defense)\n"
            "- Max HP Regen")
        dev_def_hp_btn.clicked.connect(
            lambda: tab._eb_apply_dev_preset("def_hp"))
        dev_grid_buttons.append(dev_def_hp_btn)

        dev_mp_stam_btn = QPushButton("MP/Stamina")
        dev_mp_stam_btn.setToolTip(
            "Inject DEV MP/Stamina Ring stats:\n"
            "- Max Spirit Regen\n"
            "- Max Stamina Regen\n"
            "- Max Stamina Cost Reduction")
        dev_mp_stam_btn.clicked.connect(
            lambda: tab._eb_apply_dev_preset("mp_stam"))
        dev_grid_buttons.append(dev_mp_stam_btn)

        dev_speed = QPushButton("Speed")
        dev_speed.setToolTip(
            "Inject DEV Speed Ring stats:\n"
            "- Max Attack Speed\n"
            "- Max Move Speed\n"
            "- Max Crit Rate")
        dev_speed.clicked.connect(
            lambda: tab._eb_apply_dev_preset("speed"))
        dev_grid_buttons.append(dev_speed)

        dev_mode_desc = textwrap.dedent("""
            Inject ALL DEV Ring stats:
            - Immunity
            - Max DDD (Damage)
            - Max DPV (Defense)
            - Max Attack Speed
            - Max Move Speed
            - Max Crit Rate
            - Max HP Regen
            - Max Spirit Regen
            - Max Stamina Regen
            - Max Stamina Cost Reduction
        """).strip()
        dev_all = QPushButton("All")
        dev_all.setToolTip(dev_mode_desc)
        dev_all.clicked.connect(
            lambda: tab._eb_apply_dev_preset("all"))
        dev_grid_buttons.append(dev_all)

        # Apply Layout and Styles to all grid buttons
        i = 0
        for btn in grid_buttons:
            bc,fc = styles[i % len(styles)]
            r,c = divmod(i,grid_columns)
            btn.setStyleSheet(gen_styles(fc,bc))
            grid.addWidget(btn,r,c)
            i += 1

        i = 0
        for btn in dev_grid_buttons:
            bc,fc = styles[~(i % len(styles))]
            r,c = divmod(i,grid_columns)
            btn.setStyleSheet(gen_styles(fc,bc))
            dev_grid.addWidget(btn,r,c)
            i += 1
            
        i = 0
        for btn in custom_grid_buttons:
            bc,fc = styles[i % len(styles)]
            r,c = divmod(i,grid_columns)
            btn.setStyleSheet(gen_styles(fc,bc))
            custom_grid.addWidget(btn,r,c)
            i += 1
        
        pl.addWidget(grid_label)
        pl.addLayout(grid)

        # ── DEV Ring Presets (collapsible) ──────────────────────────────
        dev_content = QWidget()
        dev_vbox = QVBoxLayout(dev_content)
        dev_vbox.setContentsMargins(0, 0, 0, 0)
        dev_vbox.setSpacing(4)

        dev_grid = QGridLayout()
        dev_grid.setSpacing(6)
        dev_btns: list[QPushButton] = []

        dev_defs = [
            ("Immunity",   "immune",  "Invincible passive + Max HP regen + Max DDD"),
            ("STR / HP",   "str_hp",  "Max DDD (Damage) + Max HP Regen"),
            ("DEF / HP",   "def_hp",  "Max DPV (Defense) + Max HP Regen"),
            ("MP / Stam",  "mp_stam", "Max Spirit Regen + Max Stamina Regen + Stamina Cost Reduction"),
            ("Speed",      "speed",   "Max Attack Speed + Move Speed + Crit Rate"),
            ("All DEV",    "all",     "All DEV Ring stats combined"),
            ("Elemental",  "elemental_weapon", "Lightning + Ice + Fire weapon imbue"),
            ("Jump Boots", "jump_boots", "Shadow Dash + Breeze Step + Swimming"),
        ]

        for label, key, tip in dev_defs:
            b = QPushButton(label)
            b.setToolTip(tip)
            b.clicked.connect(lambda _=False, k=key: tab._eb_apply_dev_preset(k))
            dev_btns.append(b)

        dev_styles = [
            ("#4682B4","White"), ("#2E8B57","White"), ("#00695C","White"),
            ("#6A1B9A","White"), ("#00BFFF","Black"), ("#DC143C","White"),
            ("#FF8C00","Black"), ("#778899","Black"),
        ]
        for idx, btn in enumerate(dev_btns):
            bc, fc = dev_styles[idx % len(dev_styles)]
            btn.setStyleSheet(gen_styles(fc, bc))
            r, c = divmod(idx, grid_columns)
            dev_grid.addWidget(btn, r, c)

        dev_vbox.addLayout(dev_grid)

        pl.addWidget(
            tab._make_collapsible("DEV Ring Presets", dev_content,
                                   start_open=False, config_key="buffs_show_dev_presets"))

        pl.addStretch(1)
        return page

    def _build_buff_imbue_page(self) -> QWidget:
        tab = self.tab
        """Imbue sub-tab — searchable passive combo + add/preview/coverage."""
        from PySide6.QtWidgets import QCompleter
        page = QWidget()
        pl = QVBoxLayout(page)
        pl.setContentsMargins(8, 8, 8, 8)
        pl.setSpacing(6)

        info = QLabel(
            "Imbue weapons/items with elemental passives (Fire, Ice, Lightning, "
            "Bismuth, Poison, Shadow, etc.) and open the weapon class to use them.")
        info.setWordWrap(True)
        info.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 10px;")
        pl.addWidget(info)

        imbue_row = QHBoxLayout()
        imbue_row.setSpacing(4)
        imbue_row.addWidget(QLabel("Imbue:"))
        tab._eb_imbue_combo = QComboBox()
        try:
            _imbue = __import__("imbue")
            _catalog = _imbue.get_passive_skill_catalog()
            _CLASS_RANK = {'visual': 0, 'functional': 1, 'stat_only': 2}
            def _sort_key(entry):
                sid, info_d = entry
                vrank = _CLASS_RANK.get(info_d.get('visual_class', 'stat_only'), 2)
                group = info_d.get('group', 'other')
                GROUP_ORDER = {
                    'fire': 0, 'ice': 1, 'lightning': 2, 'bismuth': 3,
                    'poison': 4, 'bleed': 5, 'shadow': 6, 'wind': 7, 'water': 8,
                }
                return (vrank, GROUP_ORDER.get(group, 99),
                        info_d.get('pretty_name') or info_d.get('display', ''))
            _sorted = sorted(_catalog.items(), key=_sort_key)
            _CLASS_ICON = {'visual': '\U0001f386', 'functional': '\u2699', 'stat_only': '\u00b7'}
            for sid, info_d in _sorted:
                pretty = info_d.get('pretty_name') or info_d.get('display') or info_d.get('name', f'skill_{sid}')
                internal = info_d.get('name', '')
                desc = info_d.get('description', '') or ''
                group = info_d.get('group', 'other')
                vclass = info_d.get('visual_class', 'stat_only')
                tag = f"[{group}]" if group != 'other' else ''
                icon = _CLASS_ICON.get(vclass, '\u00b7')
                label = f"{icon} {pretty} ({sid}) \u2014 {internal}"
                if tag:
                    label += f" {tag}"
                if desc and desc.lower() != pretty.lower():
                    label += f" \u2014 {desc}"
                tab._eb_imbue_combo.addItem(label, sid)
        except Exception:
            try:
                _imbue = __import__("imbue")
                for sid, (disp, _name) in sorted(_imbue.IMBUE_SKILLS.items()):
                    tab._eb_imbue_combo.addItem(f"{disp} ({sid})", sid)
            except Exception:
                pass
        tab._eb_imbue_combo.setMinimumWidth(300)
        tab._eb_imbue_combo.setEditable(True)
        tab._eb_imbue_combo.setInsertPolicy(QComboBox.NoInsert)
        tab._eb_imbue_combo.lineEdit().setPlaceholderText(
            "Type to search by name, key, or internal name...")
        _comp = tab._eb_imbue_combo.completer()
        _comp.setCompletionMode(QCompleter.PopupCompletion)
        _comp.setFilterMode(Qt.MatchContains)
        _comp.setCaseSensitivity(Qt.CaseInsensitive)
        tab._eb_imbue_combo.setToolTip(
            "Pick any Equip_Passive_* skill to imbue. Search matches pretty "
            "name, skill key, or internal name.\n\n"
            "Tier markers:\n"
            "  \U0001f386 Visual — real VFX (fire/ice/lightning aura, glow, footstep)\n"
            "  \u2699 Functional — gimmick exists but invisible (stealth, immunity)\n"
            "  \u00b7 Stat-only — no vanilla gimmick. Stat buff only."
        )
        imbue_row.addWidget(tab._eb_imbue_combo, 1)

        imbue_btn = QPushButton("Add to Selected")
        imbue_btn.setStyleSheet(
            "background-color: #7B1FA2; color: white; font-weight: bold;")
        imbue_btn.setToolTip(
            "One-click imbue. Adds the passive to the selected item and "
            "opens the weapon class if needed.")
        imbue_btn.clicked.connect(tab._eb_add_imbue_to_selected)
        imbue_row.addWidget(imbue_btn)

        preview_btn = QPushButton("\U0001f441 Preview Item")
        preview_btn.setStyleSheet(
            "background-color: #1565C0; color: white; font-weight: bold;")
        preview_btn.setToolTip(
            "Show a preview of how the selected item will look in-game.")
        preview_btn.clicked.connect(tab._buff_preview_item)
        imbue_row.addWidget(preview_btn)

        imbue_coverage_btn = QPushButton("Coverage Report")
        imbue_coverage_btn.setToolTip(
            "Show skill.pabgb-aware coverage report for the selected imbue "
            "skill: weapon count currently allowed, what 'Imbue All' opens.")
        imbue_coverage_btn.clicked.connect(tab._imbue_show_coverage)
        imbue_row.addWidget(imbue_coverage_btn)
        pl.addLayout(imbue_row)

        # Live coverage label (refreshed when imbue combo changes).
        tab._eb_imbue_coverage_label = QLabel("")
        tab._eb_imbue_coverage_label.setStyleSheet(
            f"color: {COLORS['text_dim']}; font-size: 10px; padding: 1px 4px;")
        tab._eb_imbue_coverage_label.setWordWrap(True)
        pl.addWidget(tab._eb_imbue_coverage_label)
        tab._eb_imbue_combo.currentIndexChanged.connect(
            lambda _i: tab._refresh_imbue_coverage_label())

        # ── Imbue All Weapons (bulk) — lives here so it's next to the imbue
        # combo that picks its target passive. Same handler as before.
        bulk_imbue_btn = QPushButton("Imbue All Weapons")
        bulk_imbue_btn.setStyleSheet(
            "background-color: #4A148C; color: white; font-weight: bold; "
            "padding: 10px;")
        bulk_imbue_btn.setToolTip(
            "Apply the passive picked above (Lightning, Fire, Ice, etc.) to "
            "every weapon. Adds passive + gimmick + docking + staged "
            "skill.pabgb edit that whitelists every weapon class.")
        bulk_imbue_btn.clicked.connect(tab._eb_bulk_imbue_all_weapons)
        pl.addWidget(bulk_imbue_btn)

        pl.addStretch(1)
        return page
        tab = self.tab

    def _build_buff_global_mods_page(self) -> QWidget:
        """Global Mods sub-tab — apply-to-all toggles, scroll-safe at small heights.

        Wrapped in QScrollArea so the content stays reachable even when the
        tab body is shorter than the natural content height (1080p, stats
        table taking half the vertical space, etc). The old layout used 5
        separate QGroupBoxes that clipped the bottom button off-screen.
        Everything now lives in one compact group with stacked rows.
        """
        tab = self.tab
        # Outer QScrollArea wraps the content — the page returned to QTabWidget.
        page = QScrollArea()
        page.setWidgetResizable(True)
        page.setFrameShape(QFrame.NoFrame)
        page.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        page.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        inner = QWidget()
        pl = QVBoxLayout(inner)
        pl.setContentsMargins(8, 8, 8, 8)
        pl.setSpacing(8)

        # ULTRA one-click: everything bulk-applicable in one shot.
        enable_all_btn = QPushButton(
            "Enable EVERYTHING (QoL + Dye + Sockets + Abyss + Universal Prof)")
        enable_all_btn.setStyleSheet(
            "background-color: #B71C1C; color: white; font-weight: bold; "
            "padding: 12px; font-size: 13px;")
        enable_all_btn.setToolTip(
            "Runs ALL bulk apply-to-many mods in one shot:\n"
            "  \u2022 QoL bundle (stacks 999999, charges 99, durability 65535, no cooldown)\n"
            "  \u2022 Make All Equipment Dyeable\n"
            "  \u2022 All items \u2192 5 sockets\n"
            "  \u2022 Unlock All Abyss Gear (equipable_hash \u2192 0)\n"
            "  \u2022 Universal Proficiency v2 (tribe_gender + equipslotinfo)\n\n"
            "Skipped (needs a target): Imbue passive/gimmick, per-item Add Buff/Stat.\n"
            "Everything lands in a single overlay slot on Apply to Game.")
        enable_all_btn.clicked.connect(tab._eb_enable_everything_oneclick)
        pl.addWidget(enable_all_btn)

        # Classic QoL-only button (narrower scope, no UP/Dye/Sockets) kept for
        # users who just want the 4 QoL flags without the full bundle.
        all_qol_btn = QPushButton("Enable All QoL only (no UP / Dye / Sockets)")
        all_qol_btn.setStyleSheet(
            "background-color: #00796B; color: white; font-weight: bold; "
            "padding: 10px; font-size: 12px;")
        all_qol_btn.setToolTip(
            "Narrower one-click bundle (QoL only):\n"
            "  \u2022 No Cooldown on every item\n"
            "  \u2022 Max Charges (99) on every charged item\n"
            "  \u2022 Max Stacks ticked at 999999\n"
            "  \u2022 Infinity Durability ticked (65535)\n\n"
            "For the full QoL + Dye + Sockets + UP bundle use the red button above.")
        all_qol_btn.clicked.connect(tab._eb_enable_all_qol)
        pl.addWidget(all_qol_btn)

        # Single consolidated group — 4 rows instead of 4 separate group boxes.
        toggles_grp = QGroupBox("Apply to All Items (individual mods)")
        tl = QVBoxLayout(toggles_grp)
        tl.setSpacing(6)
        tl.setContentsMargins(10, 14, 10, 10)

        # Row 1: No Cooldown
        row1 = QHBoxLayout()
        row1.setSpacing(6)
        no_cd_btn = QPushButton("No Cooldown")
        no_cd_btn.setToolTip(
            "Queue cooldown \u2192 1s for every item that has one. Included "
            "in the next Apply / Export. Same as Pldada's No Cooldown mod.")
        no_cd_btn.clicked.connect(tab._cd_patch_all_items)
        row1.addWidget(no_cd_btn)
        row1.addStretch(1)
        tl.addLayout(row1)

        # Row 2: Max Charges (spin + apply button)
        row2 = QHBoxLayout()
        row2.setSpacing(6)
        row2.addWidget(QLabel("Charges:"))
        tab._max_charges_spin = QSpinBox()
        tab._max_charges_spin.setRange(1, 99)
        tab._max_charges_spin.setValue(30)
        tab._max_charges_spin.setFixedWidth(70)
        tab._max_charges_spin.setToolTip(
            "Target max charges. Vanilla highest is 30. Values above may be "
            "clamped by the game.")
        row2.addWidget(tab._max_charges_spin)
        max_charges_btn = QPushButton("Apply Max Charges")
        max_charges_btn.setToolTip(
            "Set max_charged_useable_count to the chosen value on every "
            "item that uses charges. Takes effect on FRESH copies only.")
        max_charges_btn.clicked.connect(tab._max_charges_all_items)
        row2.addWidget(max_charges_btn)
        row2.addStretch(1)
        tl.addLayout(row2)

        # Row 3: Max Stacks (checkbox + size spin)
        row3 = QHBoxLayout()
        row3.setSpacing(6)
        tab._stack_check = QCheckBox("Max Stacks")
        tab._stack_check.setStyleSheet(
            f"color: {COLORS['accent']}; font-weight: bold;")
        tab._stack_check.setToolTip(
            "When checked, every export sets the custom stack size on all "
            "stackable items. Replaces FatStacks mod.")
        row3.addWidget(tab._stack_check)
        row3.addWidget(QLabel("Size:"))
        tab._stack_spin = QSpinBox()
        tab._stack_spin.setRange(1, 2147483647)
        tab._stack_spin.setValue(9999)
        tab._stack_spin.setFixedWidth(100)
        tab._stack_spin.setToolTip("Custom max stack size for all stackable items")
        row3.addWidget(tab._stack_spin)
        row3.addStretch(1)
        tl.addLayout(row3)

        # Row 4: Infinity Durability (single checkbox with inline description)
        row4 = QHBoxLayout()
        row4.setSpacing(6)
        tab._inf_dura_check = QCheckBox("Infinity Durability (max_endurance = 65535)")
        tab._inf_dura_check.setStyleSheet(
            f"color: {COLORS['accent']}; font-weight: bold;")
        tab._inf_dura_check.setToolTip(
            "When checked, every export sets max_endurance = 65535 and "
            "is_destroy_when_broken = 0 on all items that have durability. "
            "Replaces Pldada Infinity Durability byte-patch mod.")
        row4.addWidget(tab._inf_dura_check)
        row4.addStretch(1)
        tl.addLayout(row4)

        # Row 5: Unlock All Abyss Gear
        row5 = QHBoxLayout()
        row5.setSpacing(6)
        abyss_btn = QPushButton("Unlock All Abyss Gear")
        abyss_btn.setToolTip(
            "Sets equipable_hash = 0 on every Abyss Gear item so they\n"
            "can be socketed into ANY equipment, not just matching types.\n\n"
            "Original concept: OhmesmileTH (Nexus Mods) discovered that\n"
            "zeroing _equipableHash removes abyss socket restrictions.\n"
            "Re-implemented here using field names instead of byte offsets\n"
            "so it stacks with all other mods and survives game updates.")
        abyss_btn.clicked.connect(tab._eb_unlock_all_abyss_gear)
        row5.addWidget(abyss_btn)
        row5.addStretch(1)
        tl.addLayout(row5)

        pl.addWidget(toggles_grp)
        pl.addStretch(1)

        page.setWidget(inner)
        return page

    def _build_buff_bulk_page(self) -> QWidget:
        """Bulk Actions sub-tab — apply-to-many operations, scroll-safe.

        Wrapped in QScrollArea so buttons stay reachable when the tab body
        is shorter than the content (1080p etc). Imbue All Weapons now
        lives on the Imbue tab where it belongs next to its imbue combo.
        Socket bulk/per-item controls moved here from Advanced since
        'All \u2192 5 Sockets' is literally a bulk action.
        """
        tab = self.tab
        page = QScrollArea()
        page.setWidgetResizable(True)
        page.setFrameShape(QFrame.NoFrame)
        page.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        page.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        inner = QWidget()
        pl = QVBoxLayout(inner)
        pl.setContentsMargins(8, 8, 8, 8)
        pl.setSpacing(8)

        info = QLabel(
            "Bulk operations \u2014 click a source item first (where it matters), "
            "then a button below.")
        info.setWordWrap(True)
        info.setStyleSheet(f"color: {COLORS['text_dim']}; font-size: 11px;")
        pl.addWidget(info)

        # Weapons group
        weapons_grp = QGroupBox("Weapons")
        wgl = QVBoxLayout(weapons_grp)
        wgl.setSpacing(6)
        wgl.setContentsMargins(10, 14, 10, 10)

        bulk_buffs_btn = QPushButton("Copy Selected Item's Buffs \u2192 All Weapons")
        bulk_buffs_btn.setStyleSheet(
            "background-color: #b71c1c; color: white; font-weight: bold; "
            "padding: 10px;")
        bulk_buffs_btn.setToolTip(
            "Broadcast the equip_buffs from the CURRENTLY SELECTED item onto "
            "every weapon. Existing weapon buffs preserved; duplicates merge "
            "with higher-level wins. Then 'Apply to Game' to write.")
        bulk_buffs_btn.clicked.connect(tab._eb_bulk_apply_buffs_to_weapons)
        wgl.addWidget(bulk_buffs_btn)
        pl.addWidget(weapons_grp)

        # Equipment / Character group
        equip_grp = QGroupBox("Equipment / Character")
        egl = QVBoxLayout(equip_grp)
        egl.setSpacing(6)
        egl.setContentsMargins(10, 14, 10, 10)

        bulk_dye_btn = QPushButton("Make All Equipment Dyeable")
        bulk_dye_btn.setStyleSheet(
            "background-color: #1565C0; color: white; font-weight: bold; "
            "padding: 10px;")
        bulk_dye_btn.setToolTip(
            "Flip is_dyeable + is_editable_grime to 1 on every equipment item.\n"
            "Vanilla: only 530 of 3,038 items are dyeable. After: every armor + "
            "weapon shows up in the Dye tab.")
        bulk_dye_btn.clicked.connect(tab._eb_bulk_make_dyeable)
        egl.addWidget(bulk_dye_btn)

        bulk_equip_v2_btn = QPushButton("Universal Proficiency (all chars)")
        bulk_equip_v2_btn.setStyleSheet(
            "background-color: #B71C1C; color: white; font-weight: bold; "
            "padding: 10px;")
        bulk_equip_v2_btn.setToolTip(
            "Make ALL items equippable by Kliff, Damiane, and Oongka.\n"
            "Adds player tribe hashes to restricted items; expands equip slots.\n"
            "Only the 3 player characters are modified (NPCs untouched).")
        bulk_equip_v2_btn.clicked.connect(tab._eb_universal_proficiency_v2)
        egl.addWidget(bulk_equip_v2_btn)

        # Dev-only v1 Universal Proficiency.
        bulk_equip_btn = QPushButton("Universal Proficiency v1 [DEV]")
        bulk_equip_btn.setStyleSheet(
            "background-color: #E65100; color: white; font-weight: bold; "
            "padding: 10px;")
        bulk_equip_btn.setToolTip(
            "[DEV] Legacy universal proficiency \u2014 blanket expansion. Kept "
            "for research. Use the non-DEV button above for production.")
        bulk_equip_btn.clicked.connect(tab._eb_universal_proficiency)
        bulk_equip_btn.setVisible(tab._experimental_mode)
        egl.addWidget(bulk_equip_btn)
        tab._dev_buff_widgets.append(bulk_equip_btn)

        pl.addWidget(equip_grp)

        # Sockets group — per-item + bulk, moved from Advanced tab.
        sockets_grp = QGroupBox("Sockets")
        sgl = QVBoxLayout(sockets_grp)
        sgl.setSpacing(6)
        sgl.setContentsMargins(10, 14, 10, 10)

        # Per-item socket extender row
        # tab._eb_socket_row_widget = QWidget()
        # socket_row = QHBoxLayout(tab._eb_socket_row_widget)
        # socket_row.setContentsMargins(0, 0, 0, 0)
        # socket_row.setSpacing(6)
        # socket_row.addWidget(QLabel("Count:"))
        # tab._eb_socket_count = QSpinBox()
        # tab._eb_socket_count.setRange(1, 8)
        # tab._eb_socket_count.setValue(5)
        # tab._eb_socket_count.setFixedWidth(60)
        # tab._eb_socket_count.setToolTip(
        #     "Target max socket count. Writes to drop_default_data."
        #     "add_socket_material_item_list.")
        # socket_row.addWidget(tab._eb_socket_count)
        # socket_row.addWidget(QLabel("Pre-unlocked:"))
        # tab._eb_socket_valid = QSpinBox()
        # tab._eb_socket_valid.setRange(0, 8)
        # tab._eb_socket_valid.setValue(0)
        # tab._eb_socket_valid.setFixedWidth(60)
        # tab._eb_socket_valid.setToolTip(
        #     "How many sockets are unlocked on drop. Extra sockets need to "
        #     "be unlocked at the Witch NPC.")
        # socket_row.addWidget(tab._eb_socket_valid)
        # socket_apply_btn = QPushButton("Extend Sockets (Selected)")
        # socket_apply_btn.setToolTip(
        #     "Extend socket capacity on the SELECTED item. Only applies to "
        #     "items with use_socket=1 (abyss gear).")
        # socket_apply_btn.clicked.connect(tab._eb_extend_sockets)
        # socket_row.addWidget(socket_apply_btn)
        # socket_row.addStretch(1)
        # sgl.addWidget(tab._eb_socket_row_widget)

        # Bulk 'All → 5' socket button on its own row so it isn't squeezed
        # alongside the per-item row above.
        socket_bulk_btn = QPushButton("All \u2192 5 Sockets")
        socket_bulk_btn.setStyleSheet(
            "background-color: #1565C0; color: white; font-weight: bold; "
            "padding: 10px;")
        socket_bulk_btn.setToolTip(
            "Bulk-extend every item that's already socket-capable to 5 "
            "sockets.\nSkips items without drop_default_data or already at 5+.")
        socket_bulk_btn.clicked.connect(tab._eb_extend_all_sockets_to_5)
        sgl.addWidget(socket_bulk_btn)

        pl.addWidget(sockets_grp)

        pl.addStretch(1)

        page.setWidget(inner)
        return page

    def _build_buff_advanced_page(self) -> QWidget:
        tab = self.tab
        """Advanced sub-tab (dev-gated) — JSON Edit + mod load-order spinners."""
        from PySide6.QtWidgets import QFormLayout
        page = QWidget()
        form = QFormLayout(page)
        form.setContentsMargins(8, 8, 8, 8)
        form.setSpacing(6)
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        info = QLabel("Advanced tools. Dev mode only. Use with care.")
        info.setWordWrap(True)
        info.setStyleSheet(f"color: {COLORS['warning']}; font-size: 10px;")
        form.addRow(info)

        # Item Tools
        item_tools_container = QWidget()
        item_tools_row = QHBoxLayout(item_tools_container)
        item_tools_row.setContentsMargins(0, 0, 0, 0)
        item_tools_row.setSpacing(4)
        
        diff_btn = QPushButton("Item Diff")
        diff_btn.setToolTip(
            "Compare two items field by field — see exactly what's different\n"
            "between e.g. a working modded item and a broken one.")
        diff_btn.clicked.connect(tab._buff_open_item_diff_dialog)
        item_tools_row.addWidget(diff_btn)

        inspect_btn = QPushButton("Inspect Item")
        inspect_btn.setToolTip(
            "Deep-dive on the currently selected item — every field, type,\n"
            "and value rendered in a searchable tree. Shows crafting deps\n"
            "and any references back to this item from elsewhere in iteminfo.")
        inspect_btn.clicked.connect(tab._buff_open_item_inspector)
        item_tools_row.addWidget(inspect_btn)

        # JSON Edit
        json_btn = QPushButton("Edit JSON")
        json_btn.setToolTip("Open raw enchant data as editable JSON — full control")
        json_btn.clicked.connect(tab._eb_json_edit)
        item_tools_row.addWidget(json_btn)
        raw_import_btn = QPushButton("Import ITEMINFO")
        raw_import_btn.setToolTip("Import a previously dumped item JSON back into the editor")
        raw_import_btn.clicked.connect(tab._import_item_info)
        item_tools_row.addWidget(raw_import_btn)
        form.addRow("Item Tools:", item_tools_container)

        # Socket controls moved to Bulk Actions tab (where 'All → 5 Sockets'
        # naturally belongs). Advanced only keeps JSON Edit + load-order spins.

        # Mod folder load order (exposed in Advanced tab instead of bottom bar).
        overlay_container = QWidget()
        overlay_row = QHBoxLayout(overlay_container)
        overlay_row.setContentsMargins(0, 0, 0, 0)
        overlay_row.setSpacing(4)
        adv_overlay_spin = QSpinBox()
        adv_overlay_spin.setRange(1, 9999)
        adv_overlay_spin.setValue(tab._config.get("buff_overlay_dir", 58))
        adv_overlay_spin.setFixedWidth(80)
        adv_overlay_spin.setToolTip(
            "PAZ folder slot for 'Export JSON Patch'. Default 0058.")
        def _sync_overlay(v):
            tab._buff_overlay_spin.setValue(v)
        adv_overlay_spin.valueChanged.connect(_sync_overlay)
        overlay_row.addWidget(adv_overlay_spin)
        overlay_row.addWidget(QLabel(" (0058 default)"))
        overlay_row.addStretch(1)
        form.addRow("JSON Load Order:", overlay_container)

        modgroup_container = QWidget()
        modgroup_row = QHBoxLayout(modgroup_container)
        modgroup_row.setContentsMargins(0, 0, 0, 0)
        modgroup_row.setSpacing(4)
        adv_modgroup_spin = QSpinBox()
        adv_modgroup_spin.setRange(1, 9999)
        adv_modgroup_spin.setValue(tab._config.get("buff_mod_group", 36))
        adv_modgroup_spin.setFixedWidth(80)
        adv_modgroup_spin.setToolTip(
            "PAZ folder slot for 'Export as Mod'. Default 0036.")
        def _sync_modgroup(v):
            tab._buff_modgroup_spin.setValue(v)
        adv_modgroup_spin.valueChanged.connect(_sync_modgroup)
        modgroup_row.addWidget(adv_modgroup_spin)
        modgroup_row.addWidget(QLabel(" (0036 default)"))
        modgroup_row.addStretch(1)
        form.addRow("Mod Load Order:", modgroup_container)

        return page
        tab = self.tab

class StatusLabelBuilder:
    @staticmethod
    def build(tab: ItemBuffsTab) -> QLabel:
        # Status label — always visible, directly above the compact bottom bar.
        tab._buff_status_label = QLabel("")
        tab._buff_status_label.setWordWrap(True)
        tab._buff_status_label.setStyleSheet(
            f"color: {COLORS['text_dim']}; padding: 2px;"
        )
        return tab._buff_status_label

class BottomBarBuilder:
    @staticmethod
    def build(tab: ItemBuffsTab) -> QWidget:
        # ── Compact bottom bar: 4 primary buttons + More ▾ menu ──
        # Old bar had ~15 widgets in a FlowLayout that silently wrapped to
        # multiple rows at smaller resolutions. New bar keeps the must-have
        # actions visible on one row at 1280px wide and moves the rest into
        # a popup menu.
        from PySide6.QtWidgets import QToolButton
        bottom_bar_wrap = QWidget()
        bottom_bar = QHBoxLayout(bottom_bar_wrap)
        bottom_bar.setContentsMargins(0, 0, 0, 0)
        bottom_bar.setSpacing(6)

        export_field_btn = QPushButton("Export as Field JSON v3")
        export_field_btn.setStyleSheet(
            "background-color: #00695C; color: white; font-weight: bold;")
        export_field_btn.setToolTip(
            "Export all edits as a Format 3 field-name JSON.\n"
            "Uses field names instead of byte offsets — survives game updates.\n"
            "Compatible with Stacker Tool and future mod loaders.")
        export_field_btn.clicked.connect(tab._buff_export_field_json_v3)
        bottom_bar.addWidget(export_field_btn)

        export_mod_btn = QPushButton("Export as Mod Folder")
        export_mod_btn.setStyleSheet(
            "background-color: #7B1FA2; color: white; font-weight: bold;")
        export_mod_btn.setToolTip(
            "Export as a ready-to-use mod folder (NNNN/0.paz + 0.pamt + meta/0.papgt).\n"
            "Drop the folder into your game directory or import into a mod manager.\n"
            "Same as Apply to Game, but saves to a folder you choose instead.")
        export_mod_btn.clicked.connect(tab._buff_export_mod_folder)
        bottom_bar.addWidget(export_mod_btn)

        tab._dev_export_btns_buffs = []

        # Primary action 1: Create Item (green)
        create_item_btn = QPushButton("Create Item")
        create_item_btn.setStyleSheet(
            "background-color: #00695C; color: white; font-weight: bold;")
        create_item_btn.setToolTip(
            "Create a new custom item by cloning an existing one.\n"
            "Pick a donor item, customize name and stats, deploy.\n"
            "Use the save editor Repurchase tab to acquire it in-game.")
        create_item_btn.clicked.connect(tab._open_item_creator)
        bottom_bar.addWidget(create_item_btn)

        # Primary action 2: Apply to Game (red)
        apply_game_btn = QPushButton("Apply to Game")
        apply_game_btn.setStyleSheet(
            "background-color: #B71C1C; color: white; font-weight: bold;")
        apply_game_btn.setToolTip(
            "Deploy modified iteminfo.pabgb directly to the game.\n"
            "Creates a PAZ overlay — original files are NOT modified.\n"
            "Restart the game for changes to take effect.\n"
            "Use Restore (More ▾) to undo.")
        apply_game_btn.clicked.connect(tab._buff_apply_to_game)
        tab._buff_apply_game_btn = apply_game_btn
        bottom_bar.addWidget(apply_game_btn)

        # Primary action 3: Import Mod Folder (teal, power-user friendly)
        import_mod_btn = QPushButton("Import Mod Folder")
        import_mod_btn.setStyleSheet(
            "background-color: #00695C; color: white; font-weight: bold;")
        import_mod_btn.setToolTip(
            "Reverse-engineer any CDUMM/PAZ mod folder back into an editable "
            "config.\nPoint at a mod's files/gamedata/binary__/client/bin/"
            "iteminfo.pabgb — every modified field becomes editable here.")
        import_mod_btn.clicked.connect(tab._buff_import_mod_folder)
        bottom_bar.addWidget(import_mod_btn)

        # More ▾ popup menu — collapses the other 6 rarely-used actions.
        more_btn = QToolButton()
        more_btn.setText("More ▾")
        more_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        more_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        more_btn.setStyleSheet(
            "QToolButton { padding: 6px 12px; border: 1px solid #554430; "
            "border-radius: 4px; background: #3d2e1a; color: #f0e6d4; } "
            "QToolButton:hover { background: #5c4320; } "
            "QToolButton::menu-indicator { image: none; width: 0; }"
        )
        more_menu = QMenu(tab)

        act_import = more_menu.addAction("Import Community JSON Patch...")
        act_import.setToolTip(
            "Import a Pldada/DMM-format JSON byte patch (e.g. Infinity Durability).")
        act_import.triggered.connect(tab._buff_import_community_json)

        act_sync = more_menu.addAction("Sync Buff Names from GitHub")
        act_sync.setToolTip(
            "Download community-verified buff/stat/passive names.")
        act_sync.triggered.connect(tab._buff_sync_community_names)

        more_menu.addSeparator()

        act_save = more_menu.addAction("Save Config...")
        act_save.setToolTip(
            "Save your current edits as a reusable config file.")
        act_save.triggered.connect(tab._buff_save_config)

        act_load = more_menu.addAction("Load Config...")
        act_load.setToolTip(
            "Load a previously saved config file.")
        act_load.triggered.connect(tab._buff_load_config)

        more_menu.addSeparator()

        act_restore = more_menu.addAction("Restore Original (remove overlay)")
        act_restore.setToolTip(
            "Undo 'Apply to Game': remove the ItemBuffs PAZ overlay and its "
            "PAPGT entry. Requires admin.")
        act_restore.triggered.connect(tab._buff_restore_original)

        act_reset_vanilla = more_menu.addAction(
            "Reset to Vanilla PAPGT (nuclear)")
        act_reset_vanilla.setToolTip(
            "NUCLEAR RECOVERY: restore first-apply PAPGT snapshot. "
            "Disables ALL overlays. Requires admin.")
        act_reset_vanilla.triggered.connect(tab._buff_reset_vanilla_papgt)

        more_menu.addSeparator()

        act_verify = more_menu.addAction("Verify Applied Overlay...")
        act_verify.setToolTip(
            "Diagnostics: extract your current overlay and report how many "
            "items actually have each mutation applied. Use after Apply to "
            "Game to confirm the overlay matches expectations.")
        act_verify.triggered.connect(tab._buff_verify_applied_overlay)

        more_btn.setMenu(more_menu)
        bottom_bar.addWidget(more_btn)

        bottom_bar.addStretch(1)

        credit = QLabel("credit: Potter420 & LukeFZ")
        credit.setStyleSheet("color: #FF5252; font-style: italic; padding: 2px;")
        bottom_bar.addWidget(credit)
        
        return bottom_bar_wrap
    



