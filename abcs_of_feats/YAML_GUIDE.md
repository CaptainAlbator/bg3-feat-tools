# YAML Configuration Guide - ABCs of Feats

## Overview

YAML presets let you create pre-configured variants of ABCs of Feats.
Each preset defines which source mods to include, which feats to exclude or rename,
and how to handle sorting edge cases.

You can load presets via the GUI ("Load YAML Preset" button) or via CLI (`--config`).

## Included Presets

| Preset | Sources | Use case |
|--------|---------|----------|
| `Essential Only.yaml` | Essential Feats | Users with Essential Feats only |
| `Essential AIO.yaml` | Essential Feats + 10 companion mods | Full Essential Feats setup |
| `Extra AIO.yaml` | FeatsExtra + 10 companion mods | Full FeatsExtra setup |
| `Complete AIO.yaml` | Essential Feats + FeatsExtra + 10 companion mods | Everything |

## YAML Structure

```yaml
name: "ABCs of Feats - My Variant"      # Generated mod name
version: "1.0.0"                         # Semantic version
author: "YourName"                       # Mod author
description: "My custom sorted feats"    # Short description

# Source mod folders to include (folder names as they appear unpacked)
# Supports UUID-suffixed folders (e.g. DirtyFighting_16af93a9-...)
# Last source wins for UUID conflicts (keep_last strategy)
sources:
  - DirtyFighting
  - Essential_Feats
  - featsextra
  - planescape_dnd5e_voiced

# Feats to rename for proper alphabetical sorting
# Only changes the internal Name attribute; in-game display name is unchanged
rename_feats:
  - original: "Artificer_FirearmsProficiency_Gunner"
    renamed: "Gunner"
  - original: "Duellist"
    renamed: "Duelist"

# Sort aliases: sort under a different letter WITHOUT renaming
# Keeps the original name in XML (preserves description compatibility)
# Use this when renaming would break mod descriptions
sort_aliases:
  CrossbowExpert: "BowExpert"           # Sorted under B, stays CrossbowExpert in XML

# Feats to lock (Charisma 30 requirement, sorted to bottom)
# Use for semantic duplicates that have different UUIDs across mods
exclude_feats:
  - uuid: "9e5537b5-e1f9-4a3c-8dd5-1216cdc0d174"
    reason: "SYR_MetamagicAdept - duplicate with Metamagic Enhanced"

# Version history
changelog:
  "1.0.0": "Initial release"
```

## Adding a New Feat Mod

### Step 1: Unpack the mod

Use BG3 Multitool or LSLib to extract the `.pak` file.

### Step 2: Place in your sources directory

Add the unpacked folder alongside the other mod folders.

### Step 3: Edit the YAML

Add the folder name to `sources`:

```yaml
sources:
  - Essential_Feats
  - featsextra
  - NewModName           # Added
  - planescape_dnd5e_voiced
```

Folder matching is flexible: exact match, case-insensitive, or prefix match
(handles UUID-suffixed folders like `DirtyFighting_16af93a9-...`).

### Step 4: Update version and changelog

```yaml
version: "1.1.0"
changelog:
  "1.0.0": "Initial release"
  "1.1.0": "Added NewModName"
```

### Step 5: Regenerate

**GUI:** Load the YAML preset, select source folder, click Generate.

**CLI:**
```bash
python abcs_of_feats.py --config my_preset.yaml --sources ./Sources
```

## When to Use Each Field

| Situation | Field to use |
|-----------|-------------|
| Mod uses a weird internal name (e.g. `Artificer_FirearmsProficiency_Gunner`) | `rename_feats` |
| Renaming would break descriptions (e.g. CrossbowExpert) | `sort_aliases` |
| Mod prefixes like SYR_, Paitm_, LHB_ | Nothing (stripped automatically) |
| Two mods add the same feat with the same UUID | Nothing (handled by `keep_last`) |
| Two mods add the same feat with different UUIDs | `exclude_feats` on the duplicate |

### How `exclude_feats` Works with SharedDev

ABCs of Feats uses SharedDev/GustavDev override, which is additive: mods load their
feats on top of our sorted base. When we lock a feat (Charisma 30 requirement + sorted
to bottom), the source mod overlays its own version with the same UUID. The player sees
the mod's unlocked version - our locked copy stays hidden at the bottom.

Use `exclude_feats` when two installed mods provide the same feat with **different UUIDs**
(e.g. SYR_MetamagicAdept from Essential Feats vs LHB_MetamagicAdept from Metamagic
Enhanced). Lock the inferior duplicate so only the better version remains selectable.

## Creating a Custom Preset

Copy an existing preset and modify it:

```bash
cp "Essential AIO.yaml" my_custom.yaml
```

Edit `my_custom.yaml` to match your mod setup. The tool validates sources at
generation time and warns about missing folders.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Source not found | Check folder name (prefix matching handles UUID suffixes) |
| Feats not sorted | Verify the .pak is in your Mods folder and loads in SharedDev |
| Duplicate feats in-game | Add the duplicate UUID to `exclude_feats` to lock it |
| Feat sorts under wrong letter | Add to `rename_feats` or `sort_aliases` |
| ERROR: No Feat Description | Excluded feat lost its attributes - regenerate |
| PyYAML not installed | `pip install pyyaml` |
