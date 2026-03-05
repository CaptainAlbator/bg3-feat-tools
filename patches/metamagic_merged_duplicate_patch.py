#!/usr/bin/env python3
"""
Metamagic Merged - Duplicate Patch Generator
========================================

Companion patch for "Metamagic Merged" that locks duplicate MetamagicAdept
feats from Essential Feats and/or FeatsExtra.

The locked feats show a lock icon (Charisma 30 requirement) making them
unselectable, while the LHB_MetamagicAdept from Lumaterian remains functional
(renamed to MetamagicAdept by ABCs of Feats).

Supports:
- Essential Feats only (SYR_MetamagicAdept)
- FeatsExtra only (MetamagicAdept)
- Both together

Load order requirement:
1. Essential Feats / FeatsExtra
2. This patch (AFTER the feat mods)

Author: Albator & Claude (Anthropic)
Version: 2.0.0
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from datetime import datetime
import json
import os

# =============================================================================
# CONSTANTS
# =============================================================================

MOD_NAME_BASE = "Metamagic Merged - Duplicate Patch"
MOD_UUID = "c4d5e6f7-8901-2345-abcd-ef6789012345"
MOD_AUTHOR = "Albator"
MOD_DESCRIPTION = "Locks duplicate MetamagicAdept feats"

LOCK_REQUIREMENT = "FeatRequirementAbilityGreaterEqual('Charisma',30)"

# Suffixes for output folder name based on selection
MOD_NAME_SUFFIXES = {
    frozenset(["Essential Feats"]): " (Essential)",
    frozenset(["FeatsExtra"]): " (FeatsExtra)",
    frozenset(["Essential Feats", "FeatsExtra"]): "",  # Both = no suffix
}


def get_mod_name(selected_mods: list) -> str:
    """Get the mod name with appropriate suffix based on selection"""
    key = frozenset(selected_mods)
    suffix = MOD_NAME_SUFFIXES.get(key, "")
    return MOD_NAME_BASE + suffix

# Feat definitions to lock
FEAT_DEFS = {
    "Essential Feats": {
        "name": "SYR_MetamagicAdept",
        "uuid": "9e5537b5-e1f9-4a3c-8dd5-1216cdc0d174",
        "can_be_taken_multiple": "true",
        "passives_added": "SYR_Feat_MetamagicAdept_Passive",
        "selectors": "SelectAbilities(6d64a5f2-c26a-4af9-8957-7370ff51f0de,1,1);SelectPassives(c3506532-36eb-4d18-823e-497a537a9619,2,SYR_MetamagicAdept)",
    },
    "FeatsExtra": {
        "name": "MetamagicAdept",
        "uuid": "6a695d23-6f97-488e-aa3b-deeeeeeeeeee",
        "can_be_taken_multiple": "false",
        "passives_added": "MetamagicAdept",
        "selectors": "SelectPassives(c3506532-36eb-4d18-823e-497a537a9619,2,Metamagic)",
    },
}


# =============================================================================
# GENERATORS
# =============================================================================

def generate_feat_node(feat: dict) -> str:
    """Generate a single feat XML node with lock requirement"""
    lines = [
        '                <node id="Feat">',
        f'                    <attribute id="CanBeTakenMultipleTimes" type="bool" value="{feat["can_be_taken_multiple"]}"/>',
        f'                    <attribute id="Name" type="FixedString" value="{feat["name"]}"/>',
        f'                    <attribute id="PassivesAdded" type="LSString" value="{feat["passives_added"]}"/>',
        f'                    <attribute id="Requirements" type="LSString" value="{LOCK_REQUIREMENT}"/>',
        f'                    <attribute id="Selectors" type="LSString" value="{feat["selectors"]}"/>',
        f'                    <attribute id="UUID" type="guid" value="{feat["uuid"]}"/>',
        '                </node>',
    ]
    return '\n'.join(lines)


def generate_feats_lsx(selected_mods: list) -> str:
    """Generate Feats.lsx with locked feats for selected mods"""
    feat_nodes = []
    for mod_name in selected_mods:
        feat = FEAT_DEFS[mod_name]
        feat_nodes.append(generate_feat_node(feat))
    
    nodes_str = '\n'.join(feat_nodes)
    
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<save>
    <version major="4" minor="0" revision="9" build="322"/>
    <region id="Feats">
        <node id="root">
            <children>
{nodes_str}
            </children>
        </node>
    </region>
</save>'''


def generate_meta_lsx(selected_mods: list) -> str:
    """Generate meta.lsx content"""
    version64 = (2 << 55) | (0 << 47) | (0 << 31) | 0  # 2.0.0.0
    
    mod_name = get_mod_name(selected_mods)
    mod_list = " + ".join(selected_mods)
    description = f"Locks duplicate MetamagicAdept from {mod_list}"
    
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<save>
    <version major="4" minor="0" revision="9" build="322"/>
    <region id="Config">
        <node id="root">
            <children>
                <node id="Dependencies"/>
                <node id="ModuleInfo">
                    <attribute id="Author" type="LSString" value="{MOD_AUTHOR}"/>
                    <attribute id="CharacterCreationLevelName" type="FixedString" value=""/>
                    <attribute id="Description" type="LSString" value="{description}"/>
                    <attribute id="Folder" type="LSString" value="{mod_name}"/>
                    <attribute id="GMTemplate" type="FixedString" value=""/>
                    <attribute id="LobbyLevelName" type="FixedString" value=""/>
                    <attribute id="MD5" type="LSString" value=""/>
                    <attribute id="MainMenuBackgroundVideo" type="FixedString" value=""/>
                    <attribute id="MenuLevelName" type="FixedString" value=""/>
                    <attribute id="Name" type="LSString" value="{mod_name}"/>
                    <attribute id="NumPlayers" type="uint8" value="4"/>
                    <attribute id="PhotoBooth" type="FixedString" value=""/>
                    <attribute id="StartupLevelName" type="FixedString" value=""/>
                    <attribute id="Tags" type="LSString" value=""/>
                    <attribute id="Type" type="FixedString" value="Add-on"/>
                    <attribute id="UUID" type="FixedString" value="{MOD_UUID}"/>
                    <attribute id="Version64" type="int64" value="{version64}"/>
                    <children>
                        <node id="PublishVersion">
                            <attribute id="Version64" type="int64" value="{version64}"/>
                        </node>
                        <node id="Scripts"/>
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
</save>'''


def generate_info_json(selected_mods: list) -> str:
    """Generate info.json content"""
    mod_name = get_mod_name(selected_mods)
    mod_list = " + ".join(selected_mods)
    description = f"Locks duplicate MetamagicAdept from {mod_list}"
    
    data = {
        "Mods": [{
            "Author": MOD_AUTHOR,
            "Name": mod_name,
            "Folder": mod_name,
            "Version": "2.0.0.0",
            "Description": description,
            "UUID": MOD_UUID,
            "Created": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "Group": MOD_UUID
        }]
    }
    return json.dumps(data, indent=2)


# =============================================================================
# GUI
# =============================================================================

class FeatPatchGUI:
    """GUI for generating the feat patch"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Metamagic Merged - Duplicate Patch")
        self.root.geometry("520x420")
        self.root.resizable(False, False)
        
        self.output_dir = tk.StringVar(value=str(Path.home()))
        
        # Mod selection variables
        self.essential_feats = tk.BooleanVar(value=True)
        self.feats_extra = tk.BooleanVar(value=False)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Build the UI"""
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="Metamagic Merged - Duplicate Patch",
                         font=("Helvetica", 12, "bold"))
        title.pack(pady=(0, 5))
        
        subtitle = ttk.Label(main_frame, text="v2.0 - Supports Essential Feats + FeatsExtra",
                            font=("Helvetica", 9))
        subtitle.pack(pady=(0, 15))
        
        # Description
        desc = ttk.Label(main_frame,
                        text="Locks duplicate MetamagicAdept feats with a Charisma 30\n"
                             "requirement (lock icon). The LHB_MetamagicAdept from\n"
                             "Lumaterian (renamed by ABCs of Feats) remains functional.",
                        justify="center")
        desc.pack(pady=(0, 15))
        
        # Mod selection
        mods_frame = ttk.LabelFrame(main_frame, text="Select which mods to patch", padding=10)
        mods_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Checkbutton(mods_frame, text="Essential Feats (SYR_MetamagicAdept)",
                        variable=self.essential_feats).pack(anchor="w", pady=2)
        ttk.Checkbutton(mods_frame, text="FeatsExtra (MetamagicAdept)",
                        variable=self.feats_extra).pack(anchor="w", pady=2)
        
        # Output folder
        folder_frame = ttk.Frame(main_frame)
        folder_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(folder_frame, text="Output folder:").pack(anchor="w")
        
        entry_frame = ttk.Frame(folder_frame)
        entry_frame.pack(fill="x", pady=5)
        
        ttk.Entry(entry_frame, textvariable=self.output_dir, width=50).pack(side="left", fill="x", expand=True)
        ttk.Button(entry_frame, text="Browse...", command=self.browse).pack(side="right", padx=(5, 0))
        
        # Generate button
        ttk.Button(main_frame, text="Generate Patch", command=self.generate).pack(pady=15)
        
        # Status
        self.status = ttk.Label(main_frame, text="", foreground="gray")
        self.status.pack()
        
        # Footer
        footer = ttk.Label(main_frame, text="Albator & Claude (Anthropic)",
                          font=("Helvetica", 8))
        footer.pack(side="bottom", pady=(10, 0))
    
    def browse(self):
        """Open folder browser"""
        folder = filedialog.askdirectory(title="Select output folder")
        if folder:
            self.output_dir.set(folder)
    
    def get_selected_mods(self) -> list:
        """Get list of selected mods"""
        selected = []
        if self.essential_feats.get():
            selected.append("Essential Feats")
        if self.feats_extra.get():
            selected.append("FeatsExtra")
        return selected
    
    def generate(self):
        """Generate the patch"""
        selected = self.get_selected_mods()
        
        if not selected:
            messagebox.showwarning("No selection", "Select at least one mod to patch.")
            return
        
        output_base = Path(self.output_dir.get())
        
        try:
            # Create structure with dynamic name
            mod_name = get_mod_name(selected)
            mod_root = output_base / mod_name
            mods_dir = mod_root / "Mods" / mod_name
            feats_dir = mod_root / "Public" / mod_name / "Feats"
            
            mods_dir.mkdir(parents=True, exist_ok=True)
            feats_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate files
            with open(feats_dir / "Feats.lsx", 'w', encoding='utf-8') as f:
                f.write(generate_feats_lsx(selected))
            
            with open(mods_dir / "meta.lsx", 'w', encoding='utf-8') as f:
                f.write(generate_meta_lsx(selected))
            
            with open(mod_root / "info.json", 'w', encoding='utf-8') as f:
                f.write(generate_info_json(selected))
            
            # Build summary
            locked_feats = []
            for src_mod in selected:
                feat = FEAT_DEFS[src_mod]
                locked_feats.append(f"  - {feat['name']} ({src_mod})")
            locked_str = "\n".join(locked_feats)
            
            self.status.config(text=f"Generated for: {' + '.join(selected)}", foreground="green")
            
            messagebox.showinfo("Success!",
                f"Patch generated!\n\n"
                f"{mod_root}\n\n"
                f"Locked feats:\n{locked_str}\n\n"
                f"Pack with LSLib or BG3 Multitool.\n\n"
                f"Load order:\n"
                f"1. Essential Feats / FeatsExtra\n"
                f"2. {mod_name}")
            
        except Exception as e:
            self.status.config(text=f"Error: {e}", foreground="red")
            messagebox.showerror("Error", str(e))
    
    def run(self):
        """Start the application"""
        self.root.mainloop()


# =============================================================================
# MAIN
# =============================================================================

def main():
    app = FeatPatchGUI()
    app.run()


if __name__ == "__main__":
    main()
