# ABCs of Feats

Alphabetically sorts all BG3 feats (vanilla + modded) into a unified, clean list.

**[Download pre-built versions on Nexus Mods](https://www.nexusmods.com/baldursgate3/mods/21741)**

## The Problem

When multiple feat mods are installed, the in-game feat selection screen shows feats in an unpredictable order. Mod prefixes (SYR_, LHB_, Goon_, etc.) further disrupt alphabetical sorting.

## The Solution

ABCs of Feats merges all feat lists and sorts them alphabetically by display name, producing a single override mod that replaces the chaotic default ordering.

## Features

- **Smart Sorting**: Sorts by display name, stripping mod prefixes (SYR_, LHB_, Goon_, etc.)
- **Alias Support**: Feats can be sorted under a different name (e.g., Bow Expert under "B" instead of CrossbowExpert under "C")
- **Auto-Renames**: Technical internal names are cleaned up when the corresponding mod is detected (e.g., DefensiveDuelist → Duellist, Artificer_FirearmsProficiency_Gunner → Gunner)
- **Conflict Resolution**: "Keep last" strategy for UUID conflicts
- **YAML Configuration**: Pre-built presets and custom configuration support
- **Automatic Mod Detection**: Detects installed mods based on folder name patterns
- **GUI and CLI**: Both interfaces included

## Pre-built Versions

| Version | Includes |
|---------|----------|
| Extra AIO | Feats Extra + all additional feat mods |
| Essential Only | Essential Feats alone |
| Essential AIO | Essential Feats + all additional feat mods |
| Complete AIO | Essential Feats + Feats Extra + all additional feat mods |

## Supported Mods

**Primary:** Essential Feats (Syrchalis), Feats Extra (LostSoulMan)

**Additional:** Arcanist Feat (actualsailorcat), Better Poison Equipment (ChizFreak), Dirty Fighting Feat (CatDude55), Enweaved Feat (Yoesph), Feat - Dexterous Weapon Master (IncogneatoBurrito), FeatsOverhaul (Cahooots), Lone Wolf Feat - SE (BaldursGoonsack)

## Usage

### GUI
```bash
python abcs_of_feats_gui.py
```

### CLI
```bash
python abcs_of_feats.py
```

Run with `--help` for options.

## Installation (generated mod)

This tool generates raw mod files. To use them in-game:

1. Run the tool to generate files for your mod combination
2. Pack the output into a `.pak` using [Modder's Multitool](https://github.com/ShinyHobo/BG3-Modders-Multitool)
3. Place the `.pak` in your BG3 Mods folder — override mod, no load order needed

## Requirements

- Python 3.10+
- PyYAML (`pip install pyyaml`)
- Tkinter

## Technical Details

- **Mod type**: Override (Public/SharedDev/Feats/ and Public/GustavDev/Feats/)
- **UUID**: `b3f7c8a2-1d4e-5f6a-9b0c-2e3d4f5a6b7c`
- **Strategy**: Reads feat StaticData from all source mods, applies sorting/renaming, generates merged Feats.lsx files
