# Metamagic Merged

Merges metamagic options from Metamagic Enhanced and Metamagic Extended into a unified, alphabetically sorted list for your Sorcerer.

**[Download pre-built versions on Nexus Mods](https://www.nexusmods.com/baldursgate3/mods/21743)**

## The Problem

When using both Metamagic Enhanced (Lumaterian) and Metamagic Extended (Darkcharl), the metamagic selection screen becomes cluttered with unsorted and duplicated options.

## The Solution

Metamagic Merged uses the MergedInto approach (credit: Xarara) to combine all metamagic options into unified lists for both the Sorcerer class (L2) and the Metamagic Adept feat (L3), while preserving each mod's stat modifications.

## Features

- **MergedInto Approach**: Combines mod metamagics without overwriting vanilla entries
- **Duplicate Removal**: Prevents overlapping entries from appearing twice
- **Stat Preservation**: Keeps Lumaterian's modifications (Heightened, Quickened, Distant, Twinned)
- **Dual List Support**: Handles both Sorcerer class and Metamagic Adept feat lists
- **Alphabetical Sorting**: All options sorted for easy browsing

## Requirements

- [Metamagic Enhanced](https://www.nexusmods.com/baldursgate3/mods/9543) by Lumaterian (required)
- [Metamagic Extended](https://www.nexusmods.com/baldursgate3/mods/405) by Darkcharl (required)

**Important:** If you use [Xarara's metamagic compatibility patch](https://www.nexusmods.com/baldursgate3/mods/5674), disable it first — Metamagic Merged replaces its functionality.

## Load Order

1. Sorcerer class/subclass mods (if any)
2. Metamagic Enhanced
3. Metamagic Extended
4. **Metamagic Merged**
5. **Duplicate Patch** (optional)

## Optional: Duplicate Patches

See the [patches/](../patches/) folder. Three variants are available to lock redundant Metamagic Adept feats:

| Patch | Requires |
|-------|----------|
| Duplicate Patch (Essential Feats) | ABCs of Feats + Essential Feats |
| Duplicate Patch (Feats Extra) | ABCs of Feats + Feats Extra |
| Duplicate Patch (Both) | ABCs of Feats + Essential Feats + Feats Extra |

All three share UUID `c4d5e6f7-8901-2345-abcd-ef6789012345` — install only one.

## Usage

### GUI
```bash
python metamagic_merged.py
```

### CLI
Run with `--help` for options.

## Technical Details

- **Mod type**: Normal mod (not override)
- **UUID**: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`
- **Approach**: MergedInto PassiveLists, preserving mod stat modifications
- **Duplicate lock mechanism**: Charisma 30 requirement (unreachable naturally)
