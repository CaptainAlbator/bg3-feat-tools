#!/usr/bin/env python3
"""
ABCs of Feats - Graphical User Interface
========================================

Simple graphical interface to merge and sort feats from BG3 mods.
Compatible Windows, Mac, Linux.

Supports two modes:
- YAML preset: load a pre-configured preset (recommended for distribution)
- Manual: select a source folder and configure options by hand

Original concept: LostSoulMan (featsextra_ORDERFEATS)
Tool development: Albator & Claude (Anthropic)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
import uuid as uuid_lib
from pathlib import Path
from datetime import datetime

# Import main module (must be in the same folder)
try:
    from abcs_of_feats import (
        BG3FeatsSorter, ConfigFile, NeutralizedFeat, RenamedFeat, Feat
    )
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from abcs_of_feats import (
        BG3FeatsSorter, ConfigFile, NeutralizedFeat, RenamedFeat, Feat
    )

import json
import hashlib
import configparser

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


# =============================================================================
# META.LSX GENERATOR
# =============================================================================

class MetaLsxGenerator:
    """Generator for meta.lsx files for BG3 mods"""
    
    TEMPLATE = '''<?xml version="1.0" encoding="UTF-8"?>
<save>
    <version major="4" minor="0" revision="0" build="49"/>
    <region id="Config">
        <node id="root">
            <children>
                <node id="Dependencies"/>
                <node id="ModuleInfo">
                    <attribute id="Author" type="LSWString" value="{author}"/>
                    <attribute id="CharacterCreationLevelName" type="FixedString" value=""/>
                    <attribute id="Description" type="LSWString" value="{description}"/>
                    <attribute id="Folder" type="LSWString" value="{folder}"/>
                    <attribute id="GMTemplate" type="FixedString" value=""/>
                    <attribute id="LobbyLevelName" type="FixedString" value=""/>
                    <attribute id="MD5" type="LSString" value=""/>
                    <attribute id="MainMenuBackgroundVideo" type="FixedString" value=""/>
                    <attribute id="MenuLevelName" type="FixedString" value=""/>
                    <attribute id="Name" type="FixedString" value="{name}"/>
                    <attribute id="NumPlayers" type="uint8" value="4"/>
                    <attribute id="PhotoBooth" type="FixedString" value=""/>
                    <attribute id="StartupLevelName" type="FixedString" value=""/>
                    <attribute id="Tags" type="LSWString" value=""/>
                    <attribute id="Type" type="FixedString" value="Add-on"/>
                    <attribute id="UUID" type="FixedString" value="{uuid}"/>
                    <attribute id="Version64" type="int64" value="{version64}"/>
                    <children>
                        <node id="PublishVersion">
                            <attribute id="Version64" type="int64" value="{version64}"/>
                        </node>
                        <node id="TargetModes">
                            <children>
                                <node id="Target">
                                    <attribute id="Object" type="FixedString" value="Story"/>
                                </node>
                            </children>
                        </node>
                    </children>
                </node>
            </children>
        </node>
    </region>
</save>
'''
    
    @staticmethod
    def version_to_int64(major: int = 1, minor: int = 0, revision: int = 0, build: int = 0) -> int:
        """Convert version to BG3 int64 format"""
        return (major << 55) | (minor << 47) | (revision << 31) | build
    
    @classmethod
    def generate(cls, name: str, author: str, description: str, 
                 version: tuple = (1, 0, 0, 0), mod_uuid: str = None, folder: str = None) -> str:
        """Generate meta.lsx content"""
        if mod_uuid is None:
            mod_uuid = str(uuid_lib.uuid4())
        
        version64 = cls.version_to_int64(*version)
        if folder is None:
            folder = name
        
        return cls.TEMPLATE.format(
            author=author,
            description=description,
            folder=folder,
            name=name,
            uuid=mod_uuid,
            version64=version64
        )


# =============================================================================
# INFO.JSON GENERATOR
# =============================================================================

class InfoJsonGenerator:
    """Generator for info.json files for BG3 mod managers"""
    
    @staticmethod
    def generate(name: str, folder: str, uuid: str, version: str = "1.0.0.0", 
                 author: str = "", description: str = "") -> str:
        info = {
            "Mods": [
                {
                    "Author": author,
                    "Name": name,
                    "Folder": folder,
                    "Version": version,
                    "Description": description,
                    "UUID": uuid,
                    "Created": datetime.now().isoformat(),
                    "MD5": ""
                }
            ]
        }
        return json.dumps(info, indent=2, ensure_ascii=False)


# =============================================================================
# MAIN GUI CLASS
# =============================================================================

class BG3FeatsSorterGUI:
    """Main graphical interface"""
    
    CONFIG_FILE = "bg3_feats_sorter.ini"
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ABCs of Feats v1.2")
        self.root.geometry("800x950")
        self.root.minsize(600, 750)
        
        # Active YAML config (None = manual mode)
        self.active_config = None
        self.active_yaml_path = ""
        
        # Load saved preferences
        self.config = configparser.ConfigParser()
        self.config_path = Path(os.path.dirname(os.path.abspath(__file__))) / self.CONFIG_FILE
        self.load_config()
        
        # Variables with saved values
        self.input_dir = tk.StringVar(value=self.config.get('paths', 'input_dir', fallback=''))
        self.output_dir = tk.StringVar(value=self.config.get('paths', 'output_dir', fallback=os.path.expanduser("~/BG3_Feats_Sorted")))
        self.mod_name = tk.StringVar(value=self.config.get('mod', 'name', fallback='ABCs of Feats'))
        self.mod_author = tk.StringVar(value=self.config.get('mod', 'author', fallback=''))
        self.mod_description = tk.StringVar(value=self.config.get('mod', 'description', fallback='Feats sorted alphabetically'))
        self.generate_meta = tk.BooleanVar(value=self.config.get('options', 'generate_meta', fallback='True') == 'True')
        self.generate_info_json = tk.BooleanVar(value=self.config.get('options', 'generate_info_json', fallback='True') == 'True')
        self.generate_report = tk.BooleanVar(value=self.config.get('options', 'generate_report', fallback='False') == 'True')
        
        self.setup_ui()
        self.setup_styles()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def load_config(self):
        """Load configuration from INI file"""
        if self.config_path.exists():
            self.config.read(self.config_path)
        for section in ['paths', 'mod', 'options']:
            if not self.config.has_section(section):
                self.config.add_section(section)
    
    def save_config(self):
        """Save configuration to INI file"""
        self.config.set('paths', 'input_dir', self.input_dir.get())
        self.config.set('paths', 'output_dir', self.output_dir.get())
        self.config.set('mod', 'name', self.mod_name.get())
        self.config.set('mod', 'author', self.mod_author.get())
        self.config.set('mod', 'description', self.mod_description.get())
        self.config.set('options', 'generate_meta', str(self.generate_meta.get()))
        self.config.set('options', 'generate_info_json', str(self.generate_info_json.get()))
        self.config.set('options', 'generate_report', str(self.generate_report.get()))
        
        with open(self.config_path, 'w') as f:
            self.config.write(f)
    
    def on_close(self):
        """Called when window is closed"""
        self.save_config()
        self.root.destroy()
        
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.configure("Header.TLabel", font=("Helvetica", 12, "bold"))
        style.configure("Mode.TLabel", font=("Helvetica", 9, "italic"))
        
    def setup_ui(self):
        """Build the user interface"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # === TITLE ===
        ttk.Label(main_frame, text="ABCs of Feats", style="Header.TLabel").grid(
            row=row, column=0, columnspan=3, pady=(0, 5))
        row += 1
        
        ttk.Label(main_frame, text="Merge and alphabetically sort feats from your BG3 mods").grid(
            row=row, column=0, columnspan=3, pady=(0, 10))
        row += 1
        
        # === MODE SELECTOR ===
        mode_frame = ttk.LabelFrame(main_frame, text="Mode", padding="5")
        mode_frame.grid(row=row, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        mode_frame.columnconfigure(1, weight=1)
        
        ttk.Button(mode_frame, text="Load YAML Preset", command=self.load_yaml_preset).grid(
            row=0, column=0, padx=(0, 5))
        
        self.mode_label = ttk.Label(mode_frame, text="Manual mode (no preset loaded)", 
                                     style="Mode.TLabel")
        self.mode_label.grid(row=0, column=1, sticky="w", padx=5)
        
        ttk.Button(mode_frame, text="Clear Preset", command=self.clear_preset).grid(
            row=0, column=2, padx=(5, 0))
        row += 1
        
        # === SOURCE FOLDER ===
        ttk.Label(main_frame, text="Source folder (unpacked mods):").grid(
            row=row, column=0, sticky="w", pady=5)
        row += 1
        
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=row, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(input_frame, textvariable=self.input_dir).grid(
            row=0, column=0, sticky="ew", padx=(0, 5))
        ttk.Button(input_frame, text="Browse...", command=self.browse_input).grid(
            row=0, column=1)
        row += 1
        
        # === OUTPUT FOLDER ===
        ttk.Label(main_frame, text="Output folder:").grid(
            row=row, column=0, sticky="w", pady=5)
        row += 1
        
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=row, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(output_frame, textvariable=self.output_dir).grid(
            row=0, column=0, sticky="ew", padx=(0, 5))
        ttk.Button(output_frame, text="Browse...", command=self.browse_output).grid(
            row=0, column=1)
        row += 1
        
        # === MOD OPTIONS ===
        ttk.Separator(main_frame, orient="horizontal").grid(
            row=row, column=0, columnspan=3, sticky="ew", pady=10)
        row += 1
        
        ttk.Label(main_frame, text="Mod Configuration", style="Header.TLabel").grid(
            row=row, column=0, sticky="w", pady=(0, 10))
        row += 1
        
        ttk.Label(main_frame, text="Mod name:").grid(row=row, column=0, sticky="w")
        ttk.Entry(main_frame, textvariable=self.mod_name, width=40).grid(
            row=row, column=1, sticky="w", padx=5)
        row += 1
        
        ttk.Label(main_frame, text="Author:").grid(row=row, column=0, sticky="w")
        ttk.Entry(main_frame, textvariable=self.mod_author, width=40).grid(
            row=row, column=1, sticky="w", padx=5, pady=5)
        row += 1
        
        ttk.Label(main_frame, text="Description:").grid(row=row, column=0, sticky="w")
        ttk.Entry(main_frame, textvariable=self.mod_description, width=40).grid(
            row=row, column=1, sticky="w", padx=5, pady=5)
        row += 1
        
        # Checkboxes
        options_frame = ttk.Frame(main_frame)
        options_frame.grid(row=row, column=0, columnspan=3, sticky="w", pady=10)
        
        ttk.Checkbutton(options_frame, text="Generate meta.lsx", variable=self.generate_meta).grid(
            row=0, column=0, padx=(0, 20))
        ttk.Checkbutton(options_frame, text="Generate info.json", variable=self.generate_info_json).grid(
            row=0, column=1, padx=(0, 20))
        ttk.Checkbutton(options_frame, text="Generate report", variable=self.generate_report).grid(
            row=0, column=2)
        row += 1
        
        # === EXCLUDE FEATS ===
        ttk.Separator(main_frame, orient="horizontal").grid(
            row=row, column=0, columnspan=3, sticky="ew", pady=10)
        row += 1
        
        neutralize_header = ttk.Frame(main_frame)
        neutralize_header.grid(row=row, column=0, columnspan=3, sticky="w")
        ttk.Label(neutralize_header, text="Exclude Feats", style="Header.TLabel").grid(
            row=0, column=0, sticky="w")
        ttk.Label(neutralize_header, text="(loaded from preset or enter manually)", 
                  font=("Helvetica", 8)).grid(row=0, column=1, sticky="w", padx=(10, 0))
        row += 1
        
        ttk.Label(main_frame, text="UUIDs to exclude (one per line):").grid(
            row=row, column=0, sticky="w", pady=(5, 0))
        row += 1
        
        self.neutralize_text = tk.Text(main_frame, height=3, width=60, font=("Consolas", 9))
        self.neutralize_text.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        
        # Quick add buttons for manual mode
        quick_exclude_frame = ttk.Frame(main_frame)
        quick_exclude_frame.grid(row=row, column=2, sticky="nw", padx=(5, 0))
        ttk.Button(quick_exclude_frame, text="+ SYR_MetamagicAdept", 
                   command=lambda: self._add_to_text(self.neutralize_text, 
                   "9e5537b5-e1f9-4a3c-8dd5-1216cdc0d174 (SYR_MetamagicAdept)")).grid(
                   row=0, column=0, sticky="ew")
        ttk.Button(quick_exclude_frame, text="+ FE_MetamagicAdept", 
                   command=lambda: self._add_to_text(self.neutralize_text, 
                   "6a695d23-6f97-488e-aa3b-deeeeeeeeeee (FE_MetamagicAdept)")).grid(
                   row=1, column=0, sticky="ew", pady=(2, 0))
        
        # Fields start EMPTY - filled by YAML preset or user manually
        
        ttk.Label(main_frame, text="Format: UUID or UUID (comment)",
                  font=("Helvetica", 8), foreground="gray").grid(
            row=row+1, column=0, columnspan=3, sticky="w")
        row += 2
        
        # === RENAME FEATS ===
        ttk.Separator(main_frame, orient="horizontal").grid(
            row=row, column=0, columnspan=3, sticky="ew", pady=10)
        row += 1
        
        rename_header = ttk.Frame(main_frame)
        rename_header.grid(row=row, column=0, columnspan=3, sticky="w")
        ttk.Label(rename_header, text="Rename Feats", style="Header.TLabel").grid(
            row=0, column=0, sticky="w")
        ttk.Label(rename_header, text="(loaded from preset or enter manually)", 
                  font=("Helvetica", 8)).grid(row=0, column=1, sticky="w", padx=(10, 0))
        row += 1
        
        ttk.Label(main_frame, text="Renames (format: OriginalName -> NewName):").grid(
            row=row, column=0, sticky="w", pady=(5, 0))
        row += 1
        
        self.rename_text = tk.Text(main_frame, height=3, width=60, font=("Consolas", 9))
        self.rename_text.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        
        # Quick add buttons for manual mode
        quick_rename_frame = ttk.Frame(main_frame)
        quick_rename_frame.grid(row=row, column=2, sticky="nw", padx=(5, 0))
        ttk.Button(quick_rename_frame, text="+ LHB_Metamagic", 
                   command=lambda: self._add_to_text(self.rename_text, 
                   "LHB_MetamagicAdept -> MetamagicAdept")).grid(
                   row=0, column=0, sticky="ew")
        ttk.Button(quick_rename_frame, text="+ Dexterous", 
                   command=lambda: self._add_to_text(self.rename_text, 
                   "FinesseWeaponMaster -> DexterousWeaponMaster")).grid(
                   row=1, column=0, sticky="ew", pady=(2, 0))
        ttk.Button(quick_rename_frame, text="+ Gunner", 
                   command=lambda: self._add_to_text(self.rename_text, 
                   "Artificer_FirearmsProficiency_Gunner -> Gunner")).grid(
                   row=2, column=0, sticky="ew", pady=(2, 0))
        ttk.Button(quick_rename_frame, text="+ Artificer", 
                   command=lambda: self._add_to_text(self.rename_text, 
                   "MagicInitiateArtificer -> ArtificerInitiate")).grid(
                   row=3, column=0, sticky="ew", pady=(2, 0))
        
        # Fields start EMPTY - filled by YAML preset or user manually
        
        ttk.Label(main_frame, text="Example: LHB_MetamagicAdept -> MetamagicAdept",
                  font=("Helvetica", 8), foreground="gray").grid(
            row=row+1, column=0, columnspan=3, sticky="w")
        row += 2
        
        # === PROCESS BUTTON ===
        ttk.Separator(main_frame, orient="horizontal").grid(
            row=row, column=0, columnspan=3, sticky="ew", pady=10)
        row += 1
        
        self.process_button = ttk.Button(main_frame, text="Generate Sorted Mod", 
                                          command=self.start_processing)
        self.process_button.grid(row=row, column=0, columnspan=3, pady=10, ipadx=20, ipady=5)
        row += 1
        
        # === PROGRESS BAR ===
        self.progress = ttk.Progressbar(main_frame, mode="indeterminate")
        self.progress.grid(row=row, column=0, columnspan=3, sticky="ew", pady=5)
        row += 1
        
        # === LOG ===
        ttk.Label(main_frame, text="Log:").grid(row=row, column=0, sticky="w", pady=(10, 5))
        row += 1
        
        self.log_text = scrolledtext.ScrolledText(main_frame, height=12, state="disabled", 
                                                   font=("Consolas", 9))
        self.log_text.grid(row=row, column=0, columnspan=3, sticky="nsew", pady=(0, 10))
        main_frame.rowconfigure(row, weight=1)
        row += 1
        
        # === FOOTER ===
        ttk.Label(main_frame, 
                  text="Original concept: LostSoulMan | Design & Development: Albator with Claude (Anthropic)", 
                  font=("Helvetica", 8)).grid(row=row, column=0, columnspan=3, pady=(5, 0))

    # =========================================================================
    # YAML PRESET MANAGEMENT
    # =========================================================================
    
    def load_yaml_preset(self):
        """Load a YAML preset file and populate the GUI fields"""
        if not YAML_AVAILABLE:
            messagebox.showerror("Error", "PyYAML is not installed.\nRun: pip install pyyaml")
            return
        
        filepath = filedialog.askopenfilename(
            title="Select YAML preset",
            filetypes=[("YAML files", "*.yaml *.yml"), ("All files", "*.*")],
            initialdir=os.path.dirname(os.path.abspath(__file__))
        )
        
        if not filepath:
            return
        
        try:
            config = ConfigFile.from_yaml(Path(filepath))
            self.active_config = config
            self.active_yaml_path = filepath
            
            # Populate GUI fields from YAML
            self.mod_name.set(config.name)
            self.mod_author.set(config.author)
            self.mod_description.set(config.description)
            
            # Populate exclude feats
            self.neutralize_text.delete("1.0", "end")
            if config.neutralize:
                lines = []
                for item in config.neutralize:
                    if item.reason:
                        lines.append(f"{item.uuid} ({item.reason})")
                    else:
                        lines.append(item.uuid)
                self.neutralize_text.insert("1.0", "\n".join(lines))
            
            # Populate rename feats
            self.rename_text.delete("1.0", "end")
            if config.renames:
                lines = []
                for item in config.renames:
                    lines.append(f"{item.original_name} -> {item.new_name}")
                self.rename_text.insert("1.0", "\n".join(lines))
            
            # Update mode label
            preset_name = Path(filepath).stem
            sources_str = ", ".join(config.sources) if config.sources else "all"
            self.mode_label.configure(
                text=f"Preset: {preset_name} | Sources: {sources_str}")
            
            self.log(f"[OK] Preset loaded: {filepath}")
            self.log(f"     Name: {config.name}")
            self.log(f"     Sources: {', '.join(config.sources)}")
            if config.neutralize:
                self.log(f"     Exclude: {len(config.neutralize)} feat(s)")
            if config.renames:
                self.log(f"     Rename: {len(config.renames)} feat(s)")
            if config.sort_aliases:
                self.log(f"     Sort aliases: {len(config.sort_aliases)}")
                for orig, alias in config.sort_aliases.items():
                    self.log(f"       {orig} -> sorted as {alias}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load YAML:\n{e}")
            self.log(f"[ERROR] YAML load failed: {e}")
    
    def clear_preset(self):
        """Clear the active preset and return to manual mode"""
        self.active_config = None
        self.active_yaml_path = ""
        self.mode_label.configure(text="Manual mode (no preset loaded)")
        
        # Clear fields
        self.mod_name.set("ABCs of Feats")
        self.mod_author.set("")
        self.mod_description.set("Feats sorted alphabetically")
        self.neutralize_text.delete("1.0", "end")
        self.rename_text.delete("1.0", "end")
        
        # Reset sort aliases
        Feat.set_sort_aliases({})
        
        self.log("[OK] Preset cleared - manual mode")

    # =========================================================================
    # QUICK-ADD HELPERS (manual mode)
    # =========================================================================
    
    def _add_to_text(self, text_widget: tk.Text, entry: str):
        """Add an entry to a text widget if not already present"""
        # Check for duplicate (use the key part before any comment)
        key = entry.split('(')[0].strip() if '(' in entry else entry.split('->')[0].strip()
        current = text_widget.get("1.0", "end").strip()
        if key in current:
            self.log(f"[INFO] Already present: {key}")
            return
        
        if current:
            text_widget.insert("end", f"\n{entry}")
        else:
            text_widget.insert("1.0", entry)
        self.log(f"[OK] Added: {entry}")

    # =========================================================================
    # BROWSING
    # =========================================================================
    
    def browse_input(self):
        """Open folder selection dialog for source"""
        directory = filedialog.askdirectory(title="Select folder containing unpacked mods")
        if directory:
            self.input_dir.set(directory)
            self.log(f"Source folder: {directory}")
    
    def browse_output(self):
        """Open folder selection dialog for output"""
        directory = filedialog.askdirectory(title="Select output folder")
        if directory:
            self.output_dir.set(directory)
            self.log(f"Output folder: {directory}")

    # =========================================================================
    # LOGGING
    # =========================================================================
    
    def log(self, message: str):
        """Add message to log"""
        self.log_text.configure(state="normal")
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    # =========================================================================
    # SOURCE DETECTION
    # =========================================================================
    
    def find_all_feats_files(self, base_dir: Path) -> list:
        """
        Find all Feats.lsx files in a directory and its subdirectories.
        Returns a list of tuples: (feats_file_path, source_name)
        """
        feats_files = []
        base_path = Path(base_dir)
        
        for feats_file in base_path.rglob("Feats.lsx"):
            relative = feats_file.relative_to(base_path)
            parts = relative.parts
            
            if len(parts) >= 1:
                source_name = parts[0]
            else:
                source_name = feats_file.parent.name
            
            feats_files.append((feats_file, source_name))
        
        return feats_files
    
    def find_feats_for_sources(self, base_dir: Path, source_names: list) -> list:
        """
        Find Feats.lsx files only for the specified source names.
        Matches source names against folder names with flexible matching:
        - Exact match first
        - Case-insensitive match
        - Prefix match (handles BG3 UUID suffixes like ModName_16af93a9-...)
        Returns a list of tuples: (feats_file_path, source_name)
        """
        feats_files = []
        base_path = Path(base_dir)
        
        # Build lookup of available folders
        available_folders = {}
        if base_path.exists():
            for item in base_path.iterdir():
                if item.is_dir():
                    available_folders[item.name] = item
        
        for source_name in source_names:
            source_path = None
            matched_name = None
            
            # 1. Exact match
            if source_name in available_folders:
                source_path = available_folders[source_name]
                matched_name = source_name
            
            # 2. Case-insensitive match
            if source_path is None:
                for folder_name, folder_path in available_folders.items():
                    if folder_name.lower() == source_name.lower():
                        source_path = folder_path
                        matched_name = folder_name
                        break
            
            # 3. Prefix match (folder starts with source name, handles UUID suffixes)
            if source_path is None:
                for folder_name, folder_path in available_folders.items():
                    if folder_name.lower().startswith(source_name.lower()):
                        source_path = folder_path
                        matched_name = folder_name
                        self.log(f"  [MATCH] '{source_name}' -> '{folder_name}' (prefix match)")
                        break
            
            if source_path is None:
                self.log(f"  [WARN] Source not found: {source_name}")
                continue
            
            # Search for Feats.lsx in this source
            found_files = list(source_path.rglob("Feats.lsx"))
            if found_files:
                feats_files.append((found_files[0], matched_name))
            else:
                self.log(f"  [WARN] No Feats.lsx in: {matched_name}")
        
        return feats_files

    # =========================================================================
    # REPORT GENERATION
    # =========================================================================
    
    def create_report(self, sorter, sorted_feats: list) -> str:
        """Generate a markdown report of the sorted feats"""
        lines = [
            "# ABCs of Feats - Generated Report\n",
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            "",
            "## Statistics\n",
            f"- Total unique feats: {len(sorted_feats)}",
            f"- UUID conflicts resolved: {len(sorter.conflicts)}",
            "",
            "## Sources\n",
        ]
        
        sources = {}
        for feat in sorted_feats:
            if feat.source_mod not in sources:
                sources[feat.source_mod] = 0
            sources[feat.source_mod] += 1
        
        for source, count in sorted(sources.items()):
            lines.append(f"- **{source}**: {count} feats")
        
        lines.append("")
        lines.append("## Feat List (Alphabetical)\n")
        
        for feat in sorted_feats:
            lines.append(f"- {feat.name} ({feat.source_mod})")
        
        return '\n'.join(lines)

    # =========================================================================
    # PROCESSING
    # =========================================================================
    
    def start_processing(self):
        """Start processing in a separate thread"""
        if not self.input_dir.get():
            messagebox.showerror("Error", "Please select a source folder!")
            return
        if not self.output_dir.get():
            messagebox.showerror("Error", "Please select an output folder!")
            return
        
        self.process_button.configure(state="disabled")
        self.progress.start()
        
        thread = threading.Thread(target=self.process_feats)
        thread.daemon = True
        thread.start()
    
    def process_feats(self):
        """Main processing (executed in thread)"""
        try:
            input_dir = self.input_dir.get()
            output_base = self.output_dir.get()
            mod_name = self.mod_name.get() or "ABCs of Feats"
            mod_folder = mod_name
            
            # Create mod structure as OVERRIDE
            mod_root = Path(output_base) / mod_folder
            mods_dir = mod_root / "Mods" / mod_folder
            gustavdev_dir = mod_root / "Public" / "GustavDev" / "Feats"
            shareddev_dir = mod_root / "Public" / "SharedDev" / "Feats"
            
            mods_dir.mkdir(parents=True, exist_ok=True)
            gustavdev_dir.mkdir(parents=True, exist_ok=True)
            shareddev_dir.mkdir(parents=True, exist_ok=True)
            
            self.log(f"Mod structure: {mod_root}")
            self.log(f"  -> Override paths: Public/GustavDev/ and Public/SharedDev/")
            
            # Create sorter with vanilla feats
            self.log(f"Loading vanilla feats...")
            sorter = BG3FeatsSorter(verbose=False, include_vanilla=True)
            self.log(f"[OK] {len(sorter.feats)} vanilla feats loaded")
            
            # Apply sort aliases from YAML config (empty = none)
            if self.active_config and self.active_config.sort_aliases:
                Feat.set_sort_aliases(self.active_config.sort_aliases)
                self.log(f"[ALIAS] {len(self.active_config.sort_aliases)} sort alias(es) applied")
            else:
                Feat.set_sort_aliases({})
            
            # Find feats files
            self.log(f"Searching for Feats.lsx in: {input_dir}")
            
            if self.active_config and self.active_config.sources:
                # YAML mode: only load specified sources
                self.log(f"[YAML] Loading {len(self.active_config.sources)} specified source(s)...")
                feats_files = self.find_feats_for_sources(
                    Path(input_dir), self.active_config.sources)
            else:
                # Manual mode: load everything found
                feats_files = self.find_all_feats_files(Path(input_dir))
            
            if not feats_files:
                self.root.after(0, lambda: messagebox.showerror("Error", "No Feats.lsx file found!"))
                return
            
            self.log(f"Found {len(feats_files)} Feats.lsx file(s)")
            
            # Parse and merge (keep_last: mods override vanilla)
            for feats_file, source_name in feats_files:
                feats = sorter.parse_feats_file(feats_file, source_name)
                sorter.merge_feats(feats, "keep_last")
                self.log(f"  -> {source_name}: {len(feats)} feats")
            
            self.log(f"Total: {len(sorter.feats)} unique feats")
            
            if sorter.conflicts:
                self.log(f"[WARN] {len(sorter.conflicts)} UUID conflict(s) (resolved with keep_last)")
            
            # Neutralize specified feats
            neutralize_text = self.neutralize_text.get("1.0", "end").strip()
            if neutralize_text:
                neutralize_list = []
                for line in neutralize_text.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '(' in line:
                            uuid_part = line.split('(')[0].strip()
                            reason_part = line.split('(')[1].rstrip(')')
                        else:
                            uuid_part = line
                            reason_part = ""
                        if uuid_part:
                            neutralize_list.append(NeutralizedFeat(uuid=uuid_part, reason=reason_part))
                
                if neutralize_list:
                    self.log(f"[EXCLUDE] Processing {len(neutralize_list)} feat(s) to exclude...")
                    for item in neutralize_list:
                        uuid_lower = item.uuid.lower()
                        for feat_uuid, feat in sorter.feats.items():
                            if feat_uuid.lower() == uuid_lower:
                                self.log(f"  -> {feat.name} ({feat.source_mod}) will be excluded")
                                break
                    
                    count = sorter.neutralize_feats(neutralize_list)
                    self.log(f"[OK] {count} feat(s) excluded")
            
            # Rename specified feats
            rename_text = self.rename_text.get("1.0", "end").strip()
            if rename_text:
                renames_list = []
                for line in rename_text.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#') and '->' in line:
                        parts = line.split('->')
                        if len(parts) == 2:
                            original = parts[0].strip()
                            new_name = parts[1].strip()
                            if original and new_name:
                                renames_list.append(RenamedFeat(
                                    original_name=original, new_name=new_name))
                
                if renames_list:
                    self.log(f"[RENAME] Processing {len(renames_list)} rename(s)...")
                    count = sorter.rename_feats(renames_list)
                    self.log(f"[OK] {count} feat(s) renamed")
            
            # Generate output
            self._finish_generation(sorter, gustavdev_dir, shareddev_dir, 
                                     mods_dir, mod_root, mod_name, mod_folder)
            
        except Exception as e:
            self.log(f"[ERROR] {str(e)}")
            import traceback
            self.log(traceback.format_exc())
        finally:
            self.root.after(0, self.finish_processing)
    
    def _finish_generation(self, sorter, gustavdev_dir, shareddev_dir, 
                            mods_dir, mod_root, mod_name, mod_folder):
        """Finish the generation process"""
        sorted_feats = sorter.get_sorted_feats()
        self.log(f"Alphabetical sorting complete")
        
        vanilla_version = (4, 0, 9, 322)
        xml_content = sorter.generate_xml(sorted_feats, vanilla_version)
        
        # GustavDev
        with open(gustavdev_dir / "Feats.lsx", 'w', encoding='utf-8') as f:
            f.write(xml_content)
        self.log(f"[OK] Feats.lsx generated: Public/GustavDev/Feats/")
        
        # SharedDev
        with open(shareddev_dir / "Feats.lsx", 'w', encoding='utf-8') as f:
            f.write(xml_content)
        self.log(f"[OK] Feats.lsx generated: Public/SharedDev/Feats/")
        
        # Fixed UUID for consistent mod manager updates
        mod_uuid = "b3f7c8a2-1d4e-5f6a-9b0c-2e3d4f5a6b7c"
        
        if self.generate_meta.get():
            meta_content = MetaLsxGenerator.generate(
                name=mod_name,
                author=self.mod_author.get() or "ABCs of Feats",
                description=self.mod_description.get(),
                mod_uuid=mod_uuid,
                folder=mod_folder
            )
            with open(mods_dir / "meta.lsx", 'w', encoding='utf-8') as f:
                f.write(meta_content)
            self.log(f"[OK] meta.lsx generated (fixed UUID)")
        
        if self.generate_info_json.get():
            info_content = InfoJsonGenerator.generate(
                name=mod_name, folder=mod_folder, uuid=mod_uuid,
                author=self.mod_author.get() or "ABCs of Feats",
                description=self.mod_description.get()
            )
            with open(mod_root / "info.json", 'w', encoding='utf-8') as f:
                f.write(info_content)
            self.log(f"[OK] info.json generated")
        
        if self.generate_report.get():
            report = self.create_report(sorter, sorted_feats)
            with open(mod_root / "README_feats_list.md", 'w', encoding='utf-8') as f:
                f.write(report)
            self.log(f"[OK] Report generated")
        
        self.log("")
        self.log("=" * 50)
        self.log(f"[DONE] {len(sorted_feats)} feats sorted")
        self.log(f"Mod created in: {mod_root}")
        self.log("")
        self.log("Next step: Pack the folder with LSLib (ConverterApp)")
        self.log("=" * 50)
        
        self.root.after(0, lambda: messagebox.showinfo(
            "Success!", 
            f"Mod generated successfully!\n\n"
            f"{mod_root}\n\n"
            f"{len(sorted_feats)} feats sorted alphabetically\n\n"
            f"Next step: Pack the folder with LSLib/ConverterApp"
        ))
    
    def finish_processing(self):
        """Called when processing is finished"""
        self.progress.stop()
        self.process_button.configure(state="normal")
    
    def run(self):
        """Launch the application"""
        self.root.mainloop()


def main():
    app = BG3FeatsSorterGUI()
    app.run()


if __name__ == "__main__":
    main()
