#!/usr/bin/env python3
"""
Metamagic Merged - BG3 Metamagic Compatibility Tool
====================================================

Merges metamagic options from multiple mods into a unified list for both
Sorcerer class (L2) and Metamagic Adept feat (L3).

Features:
- Merges metamagics via MergedInto approach (credit: Xarara)
- Blocks duplicate entries from Lumaterian
- Preserves Lumaterian's stat modifications (Heightened 2pts, Quickened 2pts, etc.)
- Game sorts metamagics automatically by name

Load order requirement:
1. Lumaterian (Metamagic Enhanced)
2. Darkcharl (Metamagic Extended)
3. Metamagic Merged - LAST

Companion patch: "Metamagic Merged - SYR Patch" locks the duplicate 
SYR_MetamagicAdept from Essential Feats.

Authors: Albator & Claude (Anthropic)
Credit: Xarara for the original MergedInto compatibility approach
Version: 1.0.0
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
from datetime import datetime
import json
import configparser
import os

# =============================================================================
# CONSTANTS
# =============================================================================

# Vanilla game list UUIDs
METAMAGIC_LIST_L2 = "49704931-e47b-4ce6-abc6-dfa7ba640752"  # Sorcerer Level 2
METAMAGIC_LIST_L3 = "c3506532-36eb-4d18-823e-497a537a9619"  # Metamagic Adept feat

# Lumaterian UUIDs to block (prevent duplicate MergedInto entries)
LUMATERIAN_L2_UUID = "01be38ea-6cbd-434a-8199-b224bcbae0be"
LUMATERIAN_L3_UUID = "ea9ff83a-b2fe-4771-bde6-46a06f6ed416"

# Fixed mod UUID for consistent updates in mod manager
MOD_UUID = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

# Config file for remembering settings
CONFIG_FILE = "metamagic_merged.ini"

# Mod definitions
MOD_METAMAGICS = {
    "Darkcharl (Metamagic Extended)": {
        "description": "Adds Empowered, Seeking, and Transmuted",
        "metamagics": [
            "Metamagic_Empowered",
            "Metamagic_Seeking",
            "Metamagic_Transmuted",
        ]
    },
    "Lumaterian (Metamagic Enhanced)": {
        "description": "LHB Empowered/Seeking + modifies vanilla stats",
        "metamagics": [
            "LHB_Metamagic_Empowered",
            "LHB_Metamagic_Seeking",
        ]
    },
}


# =============================================================================
# XML GENERATORS
# =============================================================================

class PassiveListsGenerator:
    """Generates PassiveLists.lsx using MergedInto approach"""
    
    @staticmethod
    def generate(metamagics: list, include_l2: bool = True, block_lumaterian: bool = True) -> str:
        """
        Generate PassiveLists.lsx content.
        
        Args:
            metamagics: List of metamagic passive names to add via MergedInto
            include_l2: Include Sorcerer L2 list
            block_lumaterian: Block Lumaterian's MergedInto to prevent duplicates
            
        Returns:
            XML content as string
        """
        passives_str = ";".join(metamagics)
        
        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<save>',
            '    <version major="4" minor="0" revision="9" build="322"/>',
            '    <region id="PassiveLists">',
            '        <node id="root">',
            '            <children>',
        ]
        
        # Add metamagics via MergedInto for L3 (Metamagic Adept feat)
        lines.extend([
            '                <node id="PassiveList">',
            f'                    <attribute id="MergedInto" type="guid" value="{METAMAGIC_LIST_L3}"/>',
            '                    <attribute id="Name" type="FixedString" value="Metamagic Merged L3"/>',
            f'                    <attribute id="Passives" type="LSString" value="{passives_str}"/>',
            '                    <attribute id="UUID" type="guid" value="11111111-1111-1111-1111-111111111111"/>',
            '                </node>',
        ])
        
        # Add metamagics via MergedInto for L2 (Sorcerer class)
        if include_l2:
            lines.extend([
                '                <node id="PassiveList">',
                f'                    <attribute id="MergedInto" type="guid" value="{METAMAGIC_LIST_L2}"/>',
                '                    <attribute id="Name" type="FixedString" value="Metamagic Merged L2"/>',
                f'                    <attribute id="Passives" type="LSString" value="{passives_str}"/>',
                '                    <attribute id="UUID" type="guid" value="22222222-2222-2222-2222-222222222222"/>',
                '                </node>',
            ])
        
        # Block Lumaterian's MergedInto entries by overriding with empty passives
        if block_lumaterian:
            lines.extend([
                '                <node id="PassiveList">',
                '                    <attribute id="Comment" type="LSString" value="Block Lumaterian L3 duplicates"/>',
                '                    <attribute id="Passives" type="LSString" value=""/>',
                f'                    <attribute id="UUID" type="guid" value="{LUMATERIAN_L3_UUID}"/>',
                '                </node>',
            ])
            if include_l2:
                lines.extend([
                    '                <node id="PassiveList">',
                    '                    <attribute id="Comment" type="LSString" value="Block Lumaterian L2 duplicates"/>',
                    '                    <attribute id="Passives" type="LSString" value=""/>',
                    f'                    <attribute id="UUID" type="guid" value="{LUMATERIAN_L2_UUID}"/>',
                    '                </node>',
                ])
        
        lines.extend([
            '            </children>',
            '        </node>',
            '    </region>',
            '</save>',
        ])
        
        return '\n'.join(lines)


class MetaLsxGenerator:
    """Generates meta.lsx for the mod"""
    
    @staticmethod
    def generate(name: str, author: str, description: str, folder: str) -> str:
        """Generate meta.lsx content"""
        version64 = (1 << 55) | (0 << 47) | (0 << 31) | 0  # 1.0.0.0
        
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<save>
    <version major="4" minor="0" revision="9" build="322"/>
    <region id="Config">
        <node id="root">
            <children>
                <node id="Dependencies"/>
                <node id="ModuleInfo">
                    <attribute id="Author" type="LSString" value="{author}"/>
                    <attribute id="CharacterCreationLevelName" type="FixedString" value=""/>
                    <attribute id="Description" type="LSString" value="{description}"/>
                    <attribute id="Folder" type="LSString" value="{folder}"/>
                    <attribute id="GMTemplate" type="FixedString" value=""/>
                    <attribute id="LobbyLevelName" type="FixedString" value=""/>
                    <attribute id="MD5" type="LSString" value=""/>
                    <attribute id="MainMenuBackgroundVideo" type="FixedString" value=""/>
                    <attribute id="MenuLevelName" type="FixedString" value=""/>
                    <attribute id="Name" type="LSString" value="{name}"/>
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


class InfoJsonGenerator:
    """Generates info.json for mod managers"""
    
    @staticmethod
    def generate(name: str, folder: str, author: str, description: str) -> str:
        """Generate info.json content"""
        data = {
            "Mods": [{
                "Author": author,
                "Name": name,
                "Folder": folder,
                "Version": "1.0.0.0",
                "Description": description,
                "UUID": MOD_UUID,
                "Created": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "Group": MOD_UUID
            }]
        }
        return json.dumps(data, indent=2)


# =============================================================================
# GUI APPLICATION
# =============================================================================

class MetamagicPatchToolGUI:
    """Main GUI application"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Metamagic Merged")
        self.root.geometry("700x650")
        self.root.minsize(600, 550)
        
        # Initialize variables
        self.output_dir = tk.StringVar(value=str(Path.home()))
        self.mod_name = tk.StringVar(value="Metamagic Merged")
        self.mod_author = tk.StringVar(value="Albator")
        self.include_l2 = tk.BooleanVar(value=True)
        
        # Mod selection variables
        self.mod_vars = {}
        for mod_name in MOD_METAMAGICS.keys():
            self.mod_vars[mod_name] = tk.BooleanVar(value=True)  # Both selected by default
        
        # Load saved configuration
        self.load_config()
        
        # Build UI
        self.setup_ui()
    
    def load_config(self):
        """Load configuration from INI file"""
        config = configparser.ConfigParser()
        if os.path.exists(CONFIG_FILE):
            try:
                config.read(CONFIG_FILE)
                if 'Settings' in config:
                    self.output_dir.set(config.get('Settings', 'output_dir', fallback=str(Path.home())))
                    self.mod_name.set(config.get('Settings', 'mod_name', fallback='Metamagic Merged'))
                    self.mod_author.set(config.get('Settings', 'mod_author', fallback='Albator'))
            except Exception:
                pass
    
    def save_config(self):
        """Save configuration to INI file"""
        config = configparser.ConfigParser()
        config['Settings'] = {
            'output_dir': self.output_dir.get(),
            'mod_name': self.mod_name.get(),
            'mod_author': self.mod_author.get(),
        }
        try:
            with open(CONFIG_FILE, 'w') as f:
                config.write(f)
        except Exception:
            pass
    
    def setup_ui(self):
        """Build the user interface"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        row = 0
        
        # Title
        title = ttk.Label(main_frame, text="Metamagic Merged", font=("Helvetica", 14, "bold"))
        title.grid(row=row, column=0, pady=(0, 5))
        row += 1
        
        subtitle = ttk.Label(main_frame, text="MergedInto approach - Credit: Xarara")
        subtitle.grid(row=row, column=0, pady=(0, 15))
        row += 1
        
        # Info section
        info_frame = ttk.LabelFrame(main_frame, text="How it works", padding=10)
        info_frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        
        info_text = (
            "The game sorts metamagics automatically. This patch:\n"
            "- Adds mod metamagics via MergedInto (Darkcharl + Lumaterian)\n"
            "- Blocks Lumaterian duplicates\n"
            "- Preserves Lumaterian stat changes (Heightened 2pts, Quickened 2pts)"
        )
        ttk.Label(info_frame, text=info_text, wraplength=600, justify="left").grid(row=0, column=0, sticky="w")
        row += 1
        
        # Mod selection - COMMENTED OUT: Only 2 mods supported, both always enabled
        # Uncomment this section if more mods need to be supported in the future
        # mods_frame = ttk.LabelFrame(main_frame, text="Select metamagic mods", padding=10)
        # mods_frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        # mods_frame.columnconfigure(0, weight=1)
        # 
        # mod_row = 0
        # for mod_name, mod_data in MOD_METAMAGICS.items():
        #     frame = ttk.Frame(mods_frame)
        #     frame.grid(row=mod_row, column=0, sticky="ew", pady=2)
        #     
        #     cb = ttk.Checkbutton(frame, text=mod_name, variable=self.mod_vars[mod_name])
        #     cb.grid(row=0, column=0, sticky="w")
        #     
        #     desc = ttk.Label(frame, text=f"  ({mod_data['description']})", foreground="gray")
        #     desc.grid(row=0, column=1, sticky="w")
        #     
        #     mod_row += 1
        # row += 1
        
        # Output folder
        ttk.Separator(main_frame, orient="horizontal").grid(row=row, column=0, sticky="ew", pady=10)
        row += 1
        
        ttk.Label(main_frame, text="Output folder:").grid(row=row, column=0, sticky="w")
        row += 1
        
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(output_frame, textvariable=self.output_dir).grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ttk.Button(output_frame, text="Browse...", command=self.browse_output).grid(row=0, column=1)
        row += 1
        
        # Mod options
        options_frame = ttk.Frame(main_frame)
        options_frame.grid(row=row, column=0, sticky="w", pady=5)
        
        ttk.Label(options_frame, text="Mod name:").grid(row=0, column=0, sticky="w")
        ttk.Entry(options_frame, textvariable=self.mod_name, width=30).grid(row=0, column=1, padx=5)
        
        ttk.Label(options_frame, text="Author:").grid(row=0, column=2, sticky="w", padx=(20, 0))
        ttk.Entry(options_frame, textvariable=self.mod_author, width=20).grid(row=0, column=3, padx=5)
        row += 1
        
        ttk.Checkbutton(main_frame, text="Also generate L2 list (for Sorcerer class)", 
                       variable=self.include_l2).grid(row=row, column=0, sticky="w", pady=5)
        row += 1
        
        # Buttons
        ttk.Separator(main_frame, orient="horizontal").grid(row=row, column=0, sticky="ew", pady=10)
        row += 1
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=row, column=0, pady=10)
        
        ttk.Button(btn_frame, text="Preview", command=self.preview).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Generate Patch", command=self.generate).grid(row=0, column=1, padx=5)
        row += 1
        
        # Log output
        ttk.Label(main_frame, text="Output:").grid(row=row, column=0, sticky="w", pady=(10, 5))
        row += 1
        
        self.log_text = scrolledtext.ScrolledText(main_frame, height=10, font=("Consolas", 9))
        self.log_text.grid(row=row, column=0, sticky="nsew", pady=(0, 10))
        main_frame.rowconfigure(row, weight=1)
        row += 1
        
        # Footer
        footer = ttk.Label(main_frame, text="Albator & Claude (Anthropic) | Credit: Xarara", 
                          font=("Helvetica", 8))
        footer.grid(row=row, column=0, pady=(5, 0))
    
    def browse_output(self):
        """Open folder browser dialog"""
        directory = filedialog.askdirectory(title="Select output folder")
        if directory:
            self.output_dir.set(directory)
    
    def log(self, message: str):
        """Append message to log output"""
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
    
    def clear_log(self):
        """Clear log output"""
        self.log_text.delete("1.0", "end")
    
    def get_selected_metamagics(self) -> list:
        """Get list of metamagics to add based on selection"""
        metamagics = []
        
        darkcharl = self.mod_vars.get("Darkcharl (Metamagic Extended)", tk.BooleanVar(value=False)).get()
        lumaterian = self.mod_vars.get("Lumaterian (Metamagic Enhanced)", tk.BooleanVar(value=False)).get()
        
        if darkcharl and lumaterian:
            # Use LHB versions for Empowered/Seeking, add Transmuted from Darkcharl
            metamagics = ["LHB_Metamagic_Empowered", "LHB_Metamagic_Seeking", "Metamagic_Transmuted"]
        elif darkcharl:
            metamagics = MOD_METAMAGICS["Darkcharl (Metamagic Extended)"]["metamagics"].copy()
        elif lumaterian:
            metamagics = MOD_METAMAGICS["Lumaterian (Metamagic Enhanced)"]["metamagics"].copy()
        
        return metamagics
    
    def preview(self):
        """Show preview of the patch"""
        self.clear_log()
        
        metamagics = self.get_selected_metamagics()
        lumaterian = self.mod_vars.get("Lumaterian (Metamagic Enhanced)", tk.BooleanVar(value=False)).get()
        
        self.log("=" * 50)
        self.log("METAMAGIC PATCH PREVIEW")
        self.log("=" * 50)
        self.log("")
        self.log("Vanilla metamagics (7):")
        self.log("  Careful, Distant, Extended, Heightened,")
        self.log("  Quickened, Subtle, Twinned")
        self.log("")
        
        if metamagics:
            self.log(f"Added via MergedInto ({len(metamagics)}):")
            for m in metamagics:
                display = m.replace("Metamagic_", "").replace("LHB_Metamagic_", "LHB ")
                self.log(f"  + {display}")
            self.log("")
        
        total = 7 + len(metamagics)
        self.log(f"Total in-game: {total} options (sorted automatically)")
        self.log("")
        
        if lumaterian:
            self.log("Lumaterian duplicates: BLOCKED")
            self.log("Lumaterian stat changes: PRESERVED")
            self.log("")
        
        self.log("Required load order:")
        self.log("  1. Lumaterian (Metamagic Enhanced)")
        self.log("  2. Darkcharl (Metamagic Extended)")
        self.log("  3. This patch (LAST)")
    
    def generate(self):
        """Generate the patch mod"""
        self.clear_log()
        self.save_config()
        
        metamagics = self.get_selected_metamagics()
        mod_name = self.mod_name.get() or "Metamagic Merged"
        mod_folder = mod_name.replace(" ", "_")
        mod_author = self.mod_author.get() or "Albator"
        output_base = self.output_dir.get()
        include_l2 = self.include_l2.get()
        
        lumaterian = self.mod_vars.get("Lumaterian (Metamagic Enhanced)", tk.BooleanVar(value=False)).get()
        
        self.log("=" * 50)
        self.log("GENERATING METAMAGIC PATCH")
        self.log("=" * 50)
        self.log("")
        
        try:
            # Create mod structure
            mod_root = Path(output_base) / mod_folder
            mods_dir = mod_root / "Mods" / mod_folder
            lists_dir = mod_root / "Public" / mod_folder / "Lists"
            
            mods_dir.mkdir(parents=True, exist_ok=True)
            lists_dir.mkdir(parents=True, exist_ok=True)
            
            self.log(f"[OK] Created: {mod_root}")
            
            # Generate PassiveLists.lsx
            passive_content = PassiveListsGenerator.generate(
                metamagics, 
                include_l2=include_l2,
                block_lumaterian=lumaterian
            )
            
            passive_file = lists_dir / "PassiveLists.lsx"
            with open(passive_file, 'w', encoding='utf-8') as f:
                f.write(passive_content)
            
            self.log(f"[OK] PassiveLists.lsx")
            self.log(f"     + {len(metamagics)} metamagics via MergedInto")
            if lumaterian:
                self.log(f"     + Lumaterian duplicates blocked")
            
            # Generate meta.lsx
            total = 7 + len(metamagics)
            description = f"Sorted Metamagic List with {total} options"
            meta_content = MetaLsxGenerator.generate(
                name=mod_name,
                author=mod_author,
                description=description,
                folder=mod_folder
            )
            
            meta_file = mods_dir / "meta.lsx"
            with open(meta_file, 'w', encoding='utf-8') as f:
                f.write(meta_content)
            self.log(f"[OK] meta.lsx")
            
            # Generate info.json
            info_content = InfoJsonGenerator.generate(
                name=mod_name,
                folder=mod_folder,
                author=mod_author,
                description=description
            )
            
            info_file = mod_root / "info.json"
            with open(info_file, 'w', encoding='utf-8') as f:
                f.write(info_content)
            self.log(f"[OK] info.json")
            
            self.log("")
            self.log("=" * 50)
            self.log("[DONE] Patch generated!")
            self.log("")
            self.log("Load order (IMPORTANT):")
            self.log("  1. Lumaterian (Metamagic Enhanced)")
            self.log("  2. Darkcharl (Metamagic Extended)")  
            self.log(f"  3. {mod_name} <-- LAST")
            self.log("")
            self.log("Pack with LSLib or BG3 Multitool")
            self.log("=" * 50)
            
            messagebox.showinfo("Success!", 
                f"Patch generated!\n\n"
                f"{mod_root}\n\n"
                f"{total} metamagics total\n\n"
                f"Load AFTER Lumaterian & Darkcharl!")
            
        except Exception as e:
            self.log(f"[ERROR] {str(e)}")
            import traceback
            self.log(traceback.format_exc())
            messagebox.showerror("Error", str(e))
    
    def run(self):
        """Start the application"""
        self.root.mainloop()


# =============================================================================
# MAIN
# =============================================================================

def main():
    app = MetamagicPatchToolGUI()
    app.run()


if __name__ == "__main__":
    main()
