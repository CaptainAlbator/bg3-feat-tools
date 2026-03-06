# BG3 Feat Tools

A suite of modding tools for **Baldur's Gate 3** that organize and improve compatibility between feat and metamagic mods.

When multiple feat mods are installed together, the in-game feat selection screen becomes chaotic — feats appear in unpredictable order, duplicates emerge, and metamagic options conflict. These tools solve that.

## Tools

### [ABCs of Feats](abcs_of_feats/)

Alphabetically sorts all feats (vanilla + modded) into a unified, clean list. Features smart prefix-aware sorting, automatic mod detection, conflict resolution via "keep last" strategy, and alias support for feats whose internal names don't match player expectations.

Available as both a command-line script and a GUI application. Pre-built `.pak` files are available for common mod combinations.

**[Download on Nexus Mods](https://www.nexusmods.com/baldursgate3/mods/21741)**

### [Metamagic Merged](metamagic_merged/)

Merges metamagic options from [Metamagic Enhanced](https://www.nexusmods.com/baldursgate3/mods/9543) (Lumaterian) and [Metamagic Extended](https://www.nexusmods.com/baldursgate3/mods/405) (Darkcharl) into a unified, alphabetically sorted list for both the Sorcerer class and the Metamagic Adept feat. Uses the MergedInto approach (credit: Xarara) to preserve mod-specific stat modifications.

Includes optional **Duplicate Patches** to lock redundant Metamagic Adept feats from Essential Feats and/or Feats Extra.

**[Download on Nexus Mods](https://www.nexusmods.com/baldursgate3/mods/21743)**

## Supported Mods

**Primary feat mods:**
- [Essential Feats](https://www.nexusmods.com/baldursgate3/mods/5623) by Syrchalis
- [Feats Extra](https://www.nexusmods.com/baldursgate3/mods/167) by LostSoulMan

**Additional feat mods:**
- [Arcanist Feat](https://www.nexusmods.com/baldursgate3/mods/1087) by actualsailorcat
- [Better Poison Equipment](https://www.nexusmods.com/baldursgate3/mods/12413) by ChizFreak
- [Dirty Fighting Feat](https://www.nexusmods.com/baldursgate3/mods/14049) by CatDude55
- [Enweaved Feat](https://www.nexusmods.com/baldursgate3/mods/13310) by Yoesph
- [Feat - Dexterous Weapon Master](https://www.nexusmods.com/baldursgate3/mods/19197) by IncogneatoBurrito
- [FeatsOverhaul](https://www.nexusmods.com/baldursgate3/mods/15044) by Cahooots
- [Lone Wolf Feat - SE](https://www.nexusmods.com/baldursgate3/mods/14351) by BaldursGoonsack

**Metamagic mods:**
- [Metamagic Enhanced](https://www.nexusmods.com/baldursgate3/mods/9543) by Lumaterian
- [Metamagic Extended](https://www.nexusmods.com/baldursgate3/mods/405) by Darkcharl

## Requirements

- Python 3.10+
- PyYAML (`pip install pyyaml`)
- Tkinter (included with most Python installations)
- [Modder's Multitool](https://github.com/ShinyHobo/BG3-Modders-Multitool) for packing generated files into `.pak` mods

## Quick Start

1. Clone this repository
2. Navigate to the tool you need (`abcs_of_feats/` or `metamagic_merged/`)
3. Run the GUI version: `python abcs_of_feats_gui.py`
4. Or the CLI version: `python abcs_of_feats.py`
5. Pack the generated output into a `.pak` using Modder's Multitool

See each tool's README for detailed usage instructions.

## Pre-built Downloads

If you just want the ready-to-use `.pak` files without running the Python tools:

- [ABCs of Feats on Nexus Mods](https://www.nexusmods.com/baldursgate3/mods/21741)
- [Metamagic Merged on Nexus Mods](https://www.nexusmods.com/baldursgate3/mods/21743)

## Language Support

These tools currently support **English only**. The alphabetical sorting is based on internal English feat names — in other languages, the sort order would no longer be correct. Localization may be added in future updates depending on community interest.

## Credits

**Author:**
- **CaptainAlbator**

**Community:**
- **BaldursGoonsack and the BG3 Modding Discord** — guidance, feedback, and technical wisdom
- **WTFBengt** — technical insights on feat StaticData and SE implementation
- **ChizFreak** — advice on mod testing, load order management, and mod page presentation
- **Xarara** — original MergedInto compatibility approach

**Supported mod authors:**
- **LostSoulMan** — Feats Extra (and featsextra_ORDERFEATS, the foundation ABCs of Feats is built upon)
- **Syrchalis** — Essential Feats
- **Lumaterian** — Metamagic Enhanced
- **Darkcharl** — Metamagic Extended
- **actualsailorcat** — Arcanist Feat
- **Cahooots** — FeatsOverhaul
- **CatDude55** — Dirty Fighting Feat
- **IncogneatoBurrito** — Feat - Dexterous Weapon Master
- **Yoesph** — Enweaved Feat

## License

This project is licensed under the [MIT License](LICENSE).
