#!/usr/bin/env python3
"""
ABCs of Feats - Alphabetical Feat Merger for Baldur's Gate 3
=============================================================

Merges and alphabetically sorts feats from multiple BG3 mods into a unified list.
Compatible with all platforms (Windows, Mac, Linux) - no Script Extender required.

Features:
- Merges vanilla feats with mod feats
- Alphabetical sorting for clean feat selection
- UUID conflict resolution (keep_last strategy)
- Neutralize duplicate feats (Charisma 30 lock)
- Rename feats for proper sorting

Original concept: LostSoulMan (featsextra_ORDERFEATS)
Tool development: Albator & Claude (Anthropic)

Usage:
    python abcs_of_feats.py --config config.yaml
    python abcs_of_feats.py --analyze sources/
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import sys
import re
import argparse
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional, ClassVar
from dataclasses import dataclass, field
from datetime import datetime
import unicodedata
import uuid as uuid_lib
import json


# =============================================================================
# VANILLA FEATS - Base game feats from BG3 (41 feats)
# Extracted from Shared.pak / Public/SharedDev/Feats/Feats.lsx
# =============================================================================

VANILLA_FEATS = [
    {
        "Name": "AbilityScoreIncrease",
        "CanBeTakenMultipleTimes": ("bool", "true"),
        "Selectors": ("LSString", "SelectAbilities(b9149c8e-52c8-46e5-9cb6-fc39301c05fe,2,2,FeatASI)"),
        "UUID": ("guid", "d215b9ad-9753-4d74-8ff9-24bf1dce53d6"),
    },
    {
        "Name": "Actor",
        "PassivesAdded": ("LSString", "Actor"),
        "UUID": ("guid", "cdcbc538-883b-401c-a8ed-1373fb6d1720"),
    },
    {
        "Name": "Alert",
        "PassivesAdded": ("LSString", "Alert"),
        "UUID": ("guid", "f57bd72c-be64-4855-9e3a-bb7d7665e656"),
    },
    {
        "Name": "Athlete",
        "PassivesAdded": ("LSString", "Athlete_StandUp"),
        "Selectors": ("LSString", "SelectAbilities(499230af-5946-4680-a7ee-4d76d421f2ef,1,1,LightlyArmoredASI)"),
        "UUID": ("guid", "d674aa33-8633-4b67-8623-b6788f0d5fc4"),
    },
    {
        "Name": "Charger",
        "PassivesAdded": ("LSString", "Charger"),
        "UUID": ("guid", "eab25714-15d6-4e26-b809-3fad832d0484"),
    },
    {
        "Name": "CrossbowExpert",
        "PassivesAdded": ("LSString", "CrossbowExpert_PointBlank;CrossbowExpert_Wounding"),
        "UUID": ("guid", "94a78b4c-a8f2-404f-8cdc-2d454c13cb97"),
    },
    {
        "Name": "DefensiveDuelist",
        "PassivesAdded": ("LSString", "DefensiveDuelist"),
        "Requirements": ("LSString", "FeatRequirementAbilityGreaterEqual(\'Dexterity\',13)"),
        "UUID": ("guid", "661eee63-ff91-4f29-9f21-3a974c9d6fe5"),
    },
    {
        "Name": "DualWielder",
        "PassivesAdded": ("LSString", "DualWielder_BonusAC;DualWielder_PassiveBonuses"),
        "UUID": ("guid", "f692f7b5-ffd5-4942-91a1-a71ebb2f5e7c"),
    },
    {
        "Name": "DungeonDelver",
        "PassivesAdded": ("LSString", "DungeonDelver_Perception;DungeonDelver_ResistTraps"),
        "UUID": ("guid", "71b65667-0eac-4e62-b878-fa862e88ebbf"),
    },
    {
        "Name": "Durable",
        "PassivesAdded": ("LSString", "Durable"),
        "UUID": ("guid", "56c3c247-35cf-4ffd-86dd-7d249cc1808f"),
    },
    {
        "Name": "ElementalAdept",
        "CanBeTakenMultipleTimes": ("bool", "true"),
        "Selectors": ("LSString", "SelectPassives(f6b6e71f-79b1-4ba3-8fd8-ee38a44d3d39,1)"),
        "UUID": ("guid", "cec2d95b-451c-40f8-8e17-9e547d363e8e"),
    },
    {
        "Name": "GreatWeaponMaster",
        "PassivesAdded": ("LSString", "GreatWeaponMaster_BonusAttack;GreatWeaponMaster_BonusDamage"),
        "UUID": ("guid", "c09815f7-282b-4ccf-bd89-a51caa1b550f"),
    },
    {
        "Name": "HeavilyArmored",
        "PassivesAdded": ("LSString", "HeavilyArmored"),
        "Requirements": ("LSString", "FeatRequirementProficiency(\'MediumArmor\')"),
        "UUID": ("guid", "7bc235ac-7eeb-49d3-8249-c3313d87af75"),
    },
    {
        "Name": "HeavyArmorMaster",
        "PassivesAdded": ("LSString", "HeavyArmorMaster"),
        "Requirements": ("LSString", "FeatRequirementProficiency(\'HeavyArmor\')"),
        "UUID": ("guid", "0de08fff-ab18-442f-a0b1-f53e7be04c03"),
    },
    {
        "Name": "LightlyArmored",
        "PassivesAdded": ("LSString", "LightlyArmored"),
        "Selectors": ("LSString", "SelectAbilities(499230af-5946-4680-a7ee-4d76d421f2ef,1,1,LightlyArmoredASI)"),
        "UUID": ("guid", "b441c722-e4d4-4702-861a-039bfd77c124"),
    },
    {
        "Name": "Lucky",
        "PassivesAdded": ("LSString", "Lucky;Lucky_Unlock"),
        "UUID": ("guid", "d84c7f36-8c5b-4b17-b95a-e1da725f9004"),
    },
    {
        "Name": "MageSlayer",
        "PassivesAdded": ("LSString", "MageSlayer_Advantage;MageSlayer_AttackCaster;MageSlayer_BreakConcentration"),
        "UUID": ("guid", "a533fde7-ee0a-46ce-92e2-9763201a54d2"),
    },
    {
        "Name": "MagicInitiateBard",
        "PassivesAdded": ("LSString", "MagicInitiate_Bard"),
        "Selectors": ("LSString", "SelectSpells(61f79a30-2cac-4a7a-b5fe-50c89d307dd6,2,0,MIBardCantrips,Charisma,,AlwaysPrepared,,92cd50b6-eb1b-4824-8adb-853e90c34c90);SelectSpells(dcb45167-86bd-4297-9b9d-c295be51af5b,1,0,MIBardSpells,Charisma,None,AlwaysPrepared,UntilRest,92cd50b6-eb1b-4824-8adb-853e90c34c90)"),
        "UUID": ("guid", "4f744a6e-8589-4a46-89ab-a95415a73245"),
    },
    {
        "Name": "MagicInitiateCleric",
        "PassivesAdded": ("LSString", "MagicInitiate_Cleric"),
        "Selectors": ("LSString", "SelectSpells(2f43a103-5bf1-4534-b14f-663decc0c525,2,0,MIClericCantrips,Wisdom,,AlwaysPrepared,,114e7aee-d1d4-4371-8d90-8a2080592faf);SelectSpells(269d1a3b-eed8-4131-8901-a562238f5289,1,0,MIClericSpells,Wisdom,None,AlwaysPrepared,UntilRest,114e7aee-d1d4-4371-8d90-8a2080592faf)"),
        "UUID": ("guid", "28e5fed3-bd41-4b74-ab48-b8e824ad3443"),
    },
    {
        "Name": "MagicInitiateDruid",
        "PassivesAdded": ("LSString", "MagicInitiate_Druid"),
        "Selectors": ("LSString", "SelectSpells(b8faf12f-ca42-45c0-84f8-6951b526182a,2,0,MIDruidCantrips,Wisdom,,AlwaysPrepared,,457d0a6e-9da8-4f95-a225-18382f0e94b5);SelectSpells(2cd54137-2fe5-4100-aad3-df64735a8145,1,0,MIDruidSpells,Wisdom,None,AlwaysPrepared,UntilRest,457d0a6e-9da8-4f95-a225-18382f0e94b5)"),
        "UUID": ("guid", "1e1a9a4d-38f4-4a05-b080-d32c2b872250"),
    },
    {
        "Name": "MagicInitiateSorcerer",
        "PassivesAdded": ("LSString", "MagicInitiate_Sorcerer"),
        "Selectors": ("LSString", "SelectSpells(485a68b4-c678-4888-be63-4a702efbe391,2,0,MISorcererCantrips,Charisma,,AlwaysPrepared,,784001e2-c96d-4153-beb6-2adbef5abc92);SelectSpells(92c4751f-6255-4f67-822c-a75d53830b27,1,0,MISorcererSpells,Charisma,None,AlwaysPrepared,UntilRest,784001e2-c96d-4153-beb6-2adbef5abc92)"),
        "UUID": ("guid", "93d41226-d7af-495c-b023-08a6af077962"),
    },
    {
        "Name": "MagicInitiateWarlock",
        "PassivesAdded": ("LSString", "MagicInitiate_Warlock"),
        "Selectors": ("LSString", "SelectSpells(f5c4af9c-5d8d-4526-9057-94a4b243cd40,2,0,MIWarlockCantrips,Charisma,,AlwaysPrepared,,b4225a4b-4bbe-4d97-9e3c-4719dbd1487c);SelectSpells(21e1e2b9-81f7-47d2-ab69-90ba67c0c74c,1,0,MIWarlockSpells,Charisma,None,AlwaysPrepared,UntilRest,b4225a4b-4bbe-4d97-9e3c-4719dbd1487c)"),
        "UUID": ("guid", "1e0ac3c4-5bb5-42d7-941c-9de58d919732"),
    },
    {
        "Name": "MagicInitiateWizard",
        "PassivesAdded": ("LSString", "MagicInitiate_Wizard"),
        "Selectors": ("LSString", "SelectSpells(3cae2e56-9871-4cef-bba6-96845ea765fa,2,0,MIWizardCantrips,Intelligence,,AlwaysPrepared,,a865965f-501b-46e9-9eaa-7748e8c04d09);SelectSpells(11f331b0-e8b7-473b-9d1f-19e8e4178d7d,1,0,MIWizardSpells,Intelligence,None,AlwaysPrepared,UntilRest,a865965f-501b-46e9-9eaa-7748e8c04d09)"),
        "UUID": ("guid", "26c6990b-d9f0-41a2-8108-209789fafc18"),
    },
    {
        "Name": "MartialAdept",
        "PassivesAdded": ("LSString", "MartialAdept"),
        "Selectors": ("LSString", "SelectPassives(e51a2ef5-3663-43f9-8e74-5e28520323f1,2,MAManeuvers)"),
        "UUID": ("guid", "455fc2d5-1c77-40e7-a010-0b51044ae74b"),
    },
    {
        "Name": "MediumArmorMaster",
        "PassivesAdded": ("LSString", "MediumArmorMaster"),
        "Requirements": ("LSString", "FeatRequirementProficiency(\'MediumArmor\')"),
        "UUID": ("guid", "17ac3605-9a8a-41f3-9504-ffc17fffa03e"),
    },
    {
        "Name": "Mobile",
        "PassivesAdded": ("LSString", "Mobile_PassiveBonuses;Mobile_CounterAttackOfOpportunity;Mobile_DashAcrossDifficultTerrain"),
        "UUID": ("guid", "0a3b07bf-a806-4c77-9c8f-6e7c0965f9dd"),
    },
    {
        "Name": "ModeratelyArmored",
        "PassivesAdded": ("LSString", "ModeratelyArmored"),
        "Requirements": ("LSString", "FeatRequirementProficiency(\'LightArmor\')"),
        "Selectors": ("LSString", "SelectAbilities(499230af-5946-4680-a7ee-4d76d421f2ef,1,1,LightlyArmoredASI)"),
        "UUID": ("guid", "681d5307-f0ed-4c94-8cf0-db0c51116f56"),
    },
    {
        "Name": "Performer",
        "PassivesAdded": ("LSString", "Performer"),
        "Selectors": ("LSString", "SelectAbilities(98acdfcb-3c74-4e1a-8707-5d6da747d430,1,1,PerformerASI)"),
        "UUID": ("guid", "60dfd716-3ba8-4611-90ee-018b59775b1d"),
    },
    {
        "Name": "PolearmMaster",
        "PassivesAdded": ("LSString", "PolearmMaster_AttackOfOpportunity;PolearmMaster_BonusAttack"),
        "UUID": ("guid", "fdf0be80-cc1e-4501-bd2e-7a1ea737362c"),
    },
    {
        "Name": "Resilient",
        "Selectors": ("LSString", "SelectPassives(d4b799b4-30e2-412b-b2c9-abb144df8e7d,1)"),
        "UUID": ("guid", "b13c4744-1d45-42da-b92c-e09f598ab1c3"),
    },
    {
        "Name": "RitualCaster",
        "CanBeTakenMultipleTimes": ("bool", "false"),
        "PassivesAdded": ("LSString", "RitualCaster_FreeSpells"),
        "Selectors": ("LSString", "SelectSpells(8c32c900-a8ea-4f2f-9f6f-eccd0d361a9d,2,0,,,,AlwaysPrepared)"),
        "UUID": ("guid", "f3370916-6b35-4c5b-af36-19ca888cb43e"),
    },
    {
        "Name": "SavageAttacker",
        "PassivesAdded": ("LSString", "SavageAttacker"),
        "UUID": ("guid", "e061a323-3430-4cff-88d3-5eae7a1779a4"),
    },
    {
        "Name": "Sentinel",
        "PassivesAdded": ("LSString", "Sentinel_Attack;Sentinel_ZeroSpeed;Sentinel_OpportunityAdvantage"),
        "UUID": ("guid", "816b1554-9384-49e9-aaa0-05dd622e60f7"),
    },
    {
        "Name": "Sharpshooter",
        "PassivesAdded": ("LSString", "Sharpshooter_AllIn;Sharpshooter_Bonuses"),
        "UUID": ("guid", "010f717e-c6e2-45cf-bbf9-298a72db4cad"),
    },
    {
        "Name": "ShieldMaster",
        "PassivesAdded": ("LSString", "ShieldMaster_PassiveBonuses;ShieldMaster_Block"),
        "UUID": ("guid", "3fe71254-d1b2-44c7-886c-927552fe5f2e"),
    },
    {
        "Name": "Skilled",
        "PassivesAdded": ("LSString", "Skilled"),
        "Selectors": ("LSString", "SelectSkills(f974ebd6-3725-4b90-bb5c-2b647d41615d,3,SkilledSkills)"),
        "UUID": ("guid", "019564a0-f136-4139-94ea-040f94bbaf19"),
    },
    {
        "Name": "SpellSniper",
        "PassivesAdded": ("LSString", "SpellSniper_Critical"),
        "Selectors": ("LSString", "SelectSpells(64784e08-e31e-4850-a743-ecfb3fd434d7,1,0,,,,AlwaysPrepared)"),
        "UUID": ("guid", "c02f22c9-9a06-4001-b917-4d5cf09be399"),
    },
    {
        "Name": "TavernBrawler",
        "PassivesAdded": ("LSString", "TavernBrawler"),
        "Selectors": ("LSString", "SelectAbilities(859878b3-9c3a-450d-a190-bc90707c9671,1,1,LightlyArmoredASI)"),
        "UUID": ("guid", "be0889d2-f9aa-472d-b942-592bff0f1ef3"),
    },
    {
        "Name": "Tough",
        "PassivesAdded": ("LSString", "Tough"),
        "UUID": ("guid", "e8d1e7f6-d841-48ff-a83c-f1aaa16597ff"),
    },
    {
        "Name": "WarCaster",
        "PassivesAdded": ("LSString", "WarCaster_Bonuses;WarCaster_OpportunitySpell"),
        "UUID": ("guid", "ed4e367d-d136-4285-abac-077147e84cf2"),
    },
    {
        "Name": "WeaponMaster",
        "PassivesAdded": ("LSString", "WeaponMaster"),
        "Selectors": ("LSString", "SelectAbilities(499230af-5946-4680-a7ee-4d76d421f2ef,1,1,LightlyArmoredASI);SelectPassives(f21e6b94-44e8-4ae0-a6f1-0c81abac03a2,4,WeaponMasterProficiencies)"),
        "UUID": ("guid", "b153e75c-27a2-4412-95cd-60b477121679"),
    },
]


# =============================================================================
# VERSION MANAGEMENT
# =============================================================================

@dataclass
class Version:
    """Semantic version handler (major.minor.patch)"""
    major: int = 1
    minor: int = 0
    patch: int = 0
    
    @classmethod
    def from_string(cls, version_str: str) -> 'Version':
        """Parse version from string like '1.2.3'"""
        parts = version_str.strip().split('.')
        return cls(
            major=int(parts[0]) if len(parts) > 0 else 1,
            minor=int(parts[1]) if len(parts) > 1 else 0,
            patch=int(parts[2]) if len(parts) > 2 else 0
        )
    
    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
    
    def to_version64(self) -> int:
        """Convert to BG3 Version64 format: (major << 55) | (minor << 47) | (revision << 31) | build"""
        return (self.major << 55) | (self.minor << 47) | (self.patch << 31) | 0
    
    def bump(self, part: str) -> 'Version':
        """Return a new version with the specified part incremented"""
        if part == 'major':
            return Version(self.major + 1, 0, 0)
        elif part == 'minor':
            return Version(self.major, self.minor + 1, 0)
        elif part == 'patch':
            return Version(self.major, self.minor, self.patch + 1)
        else:
            raise ValueError(f"Unknown version part: {part}")


@dataclass
class ModSource:
    """Represents a source mod with its metadata"""
    name: str
    path: Path
    version: str = "unknown"
    feats_count: int = 0


@dataclass
class NeutralizedFeat:
    """Represents a feat to be neutralized (made inactive)"""
    uuid: str
    reason: str = ""
    
    def to_dict(self) -> dict:
        return {"uuid": self.uuid, "reason": self.reason}
    
    @classmethod
    def from_dict(cls, data: dict) -> 'NeutralizedFeat':
        if isinstance(data, str):
            return cls(uuid=data)
        return cls(uuid=data.get("uuid", ""), reason=data.get("reason", ""))


@dataclass
class RenamedFeat:
    """Represents a feat to be renamed for sorting purposes"""
    original_name: str
    new_name: str
    
    def to_dict(self) -> dict:
        return {"original": self.original_name, "renamed": self.new_name}
    
    @classmethod
    def from_dict(cls, data: dict) -> 'RenamedFeat':
        if isinstance(data, dict):
            return cls(
                original_name=data.get("original", ""),
                new_name=data.get("renamed", "")
            )
        return cls(original_name="", new_name="")


@dataclass 
class ConfigFile:
    """Configuration for a specific variant"""
    name: str
    version: Version
    author: str
    description: str
    sources: List[str]
    changelog: Dict[str, str] = field(default_factory=dict)
    duplicate_preferences: Dict[str, str] = field(default_factory=dict)
    neutralize: List[NeutralizedFeat] = field(default_factory=list)
    renames: List[RenamedFeat] = field(default_factory=list)
    sort_aliases: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def from_yaml(cls, filepath: Path) -> 'ConfigFile':
        """Load configuration from YAML file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Parse neutralize/exclude list (support both keys)
        neutralize_data = data.get('exclude_feats', data.get('neutralize', []))
        neutralize_list = [NeutralizedFeat.from_dict(item) for item in neutralize_data]
        
        # Parse renames list (support both keys)
        renames_data = data.get('rename_feats', data.get('renames', []))
        renames_list = [RenamedFeat.from_dict(item) for item in renames_data]
        
        # Parse sort aliases
        sort_aliases = data.get('sort_aliases', {})
        
        return cls(
            name=data.get('name', 'ABCs of Feats'),
            version=Version.from_string(data.get('version', '1.0.0')),
            author=data.get('author', 'ABCs of Feats'),
            description=data.get('description', 'Alphabetically sorted feats'),
            sources=data.get('sources', []),
            changelog=data.get('changelog', {}),
            duplicate_preferences=data.get('duplicate_preferences', {}),
            neutralize=neutralize_list,
            renames=renames_list,
            sort_aliases=sort_aliases
        )
    
    def to_yaml(self, filepath: Path):
        """Save configuration to YAML file"""
        data = {
            'name': self.name,
            'version': str(self.version),
            'author': self.author,
            'description': self.description,
            'sources': self.sources,
            'changelog': self.changelog,
            'duplicate_preferences': self.duplicate_preferences,
            'exclude_feats': [n.to_dict() for n in self.neutralize] if self.neutralize else [],
            'rename_feats': [r.to_dict() for r in self.renames] if self.renames else [],
            'sort_aliases': self.sort_aliases if self.sort_aliases else {}
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


# =============================================================================
# FEAT DATA STRUCTURES
# =============================================================================

@dataclass
class Feat:
    """Represents a feat with all its attributes"""
    name: str
    uuid: str
    attributes: Dict[str, Tuple[str, str]]  # id -> (type, value)
    source_mod: str = "unknown"
    
    # Common mod prefixes/suffixes to ignore for sorting
    PREFIXES_TO_IGNORE = [
        'SYR_',      # Essential Feats (Sychralis)
        'Paitm_',    # Planescape (Bibsan)
        'MAG_',      # Magic mods
        'UNL_',      # Unlock mods
        'EXP_',      # Expanded mods
        'Sailor_',   # Arcanist mod
        'Goon_',     # LoneWolf, Enweaved mods
        'LHB_',      # Lumaterian mods
    ]
    
    SUFFIXES_TO_IGNORE = [
        '_featsextra',
        '_expanded', 
        '_feat',
        '_Feat',
    ]
    
    # Sort aliases: feats that should be sorted under a different name
    # without changing their actual name in the XML
    # This allows proper sorting while keeping mod descriptions working
    # Configurable via YAML or set programmatically - empty by default
    SORT_ALIASES: ClassVar[Dict[str, str]] = {}
    
    @classmethod
    def set_sort_aliases(cls, aliases: Dict[str, str]):
        """Set sort aliases (call before sorting). Clears previous aliases."""
        cls.SORT_ALIASES = dict(aliases) if aliases else {}
    
    def get_semantic_name(self) -> str:
        """Returns the 'semantic' name without mod prefixes/suffixes"""
        clean_name = self.name
        
        # Check for sort aliases first (e.g., CrossbowExpert -> BowExpert for sorting)
        if clean_name in self.SORT_ALIASES:
            clean_name = self.SORT_ALIASES[clean_name]
        
        # Remove prefixes
        for prefix in self.PREFIXES_TO_IGNORE:
            if clean_name.startswith(prefix):
                clean_name = clean_name[len(prefix):]
                break
        
        # Remove suffixes
        for suffix in self.SUFFIXES_TO_IGNORE:
            if clean_name.lower().endswith(suffix.lower()):
                clean_name = clean_name[:-len(suffix)]
                break
        
        return clean_name
    
    def get_sort_key(self) -> str:
        """Returns the sort key (cleaned name for alphabetical sorting)"""
        # Use semantic name for sorting
        clean_name = self.get_semantic_name().lower()
        
        # Normalize unicode characters
        clean_name = unicodedata.normalize('NFKD', clean_name)
        clean_name = clean_name.encode('ascii', 'ignore').decode('ascii')
        
        # Remove remaining underscores for more natural sorting
        clean_name = clean_name.replace('_', '')
        
        return clean_name


# =============================================================================
# MAIN SORTER CLASS
# =============================================================================

class BG3FeatsSorter:
    """Main class for merging and sorting feats"""
    
    def __init__(self, verbose: bool = True, include_vanilla: bool = True):
        self.verbose = verbose
        self.include_vanilla = include_vanilla
        self.feats: Dict[str, Feat] = {}  # UUID -> Feat
        self.conflicts: List[Tuple[str, str, str]] = []  # (uuid, mod1, mod2)
        self.semantic_duplicates: Dict[str, List[Feat]] = {}  # semantic_name -> [feats]
        self.latest_version: Tuple[int, int, int, int] = (4, 0, 9, 322)  # Default version
        self.sources_loaded: List[ModSource] = []
        
        # Load vanilla feats if requested
        if self.include_vanilla:
            self.load_vanilla_feats()
    
    def load_vanilla_feats(self):
        """Load base game feats from VANILLA_FEATS constant"""
        vanilla_feats = []
        for feat_data in VANILLA_FEATS:
            name = feat_data["Name"]
            uuid = feat_data["UUID"][1]  # (type, value) -> value
            
            # Build attributes dict
            attributes = {}
            for key, value in feat_data.items():
                if key != "Name":
                    if isinstance(value, tuple):
                        attributes[key] = value
                    else:
                        attributes[key] = ("FixedString", value)
            
            feat = Feat(name=name, uuid=uuid, attributes=attributes, source_mod="Vanilla")
            vanilla_feats.append(feat)
        
        self.merge_feats(vanilla_feats, "keep_first")
        self.log(f"  [OK] Vanilla: {len(vanilla_feats)} base game feats loaded")
        
    def log(self, message: str):
        """Print message if verbose is enabled"""
        if self.verbose:
            print(message)
    
    def find_feats_file(self, source_dir: Path) -> Optional[Path]:
        """Find Feats.lsx file in a source directory"""
        # Check common paths
        common_paths = [
            source_dir / "Feats.lsx",
            source_dir / "Public" / source_dir.name / "Feats" / "Feats.lsx",
        ]
        
        for path in common_paths:
            if path.exists():
                return path
        
        # Fallback: search recursively
        feats_files = list(source_dir.rglob("Feats.lsx"))
        if feats_files:
            return feats_files[0]
        
        return None
    
    def get_source_version(self, source_dir: Path) -> str:
        """Read version from version.txt if it exists"""
        version_file = source_dir / "version.txt"
        if version_file.exists():
            return version_file.read_text().strip()
        return "unknown"
    
    def parse_feat_node(self, node: ET.Element, source_mod: str) -> Optional[Feat]:
        """Parse a single Feat node from XML"""
        name = None
        uuid = None
        attributes = {}
        
        for attr in node.findall("attribute"):
            attr_id = attr.get("id")
            attr_type = attr.get("type")
            attr_value = attr.get("value", "")
            
            if attr_id == "Name":
                name = attr_value
            elif attr_id == "UUID":
                uuid = attr_value
                
            attributes[attr_id] = (attr_type, attr_value)
        
        if name and uuid:
            return Feat(name=name, uuid=uuid, attributes=attributes, source_mod=source_mod)
        return None
    
    def parse_feats_file(self, filepath: Path, source_name: str) -> List[Feat]:
        """Parse a Feats.lsx file and return list of feats"""
        feats = []
        
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            
            # Capture file version
            version_elem = root.find("version")
            if version_elem is not None:
                try:
                    file_version = (
                        int(version_elem.get("major", 4)),
                        int(version_elem.get("minor", 0)),
                        int(version_elem.get("revision", 0)),
                        int(version_elem.get("build", 0))
                    )
                    # Keep the most recent version
                    if file_version > self.latest_version:
                        self.latest_version = file_version
                except ValueError:
                    pass
            
            # Find all Feat nodes
            for feat_node in root.findall(".//node[@id='Feat']"):
                feat = self.parse_feat_node(feat_node, source_name)
                if feat:
                    feats.append(feat)
                    
            self.log(f"  [OK] {source_name}: {len(feats)} feats found")
            
        except ET.ParseError as e:
            self.log(f"  [ERROR] Parse error {filepath}: {e}")
        except Exception as e:
            self.log(f"  [ERROR] Error reading {filepath}: {e}")
            
        return feats
    
    def merge_feats(self, feats_list: List[Feat], strategy: str = "keep_first"):
        """
        Merge feats into main dictionary
        
        Conflict strategies:
        - keep_first: Keep the first feat found (by UUID)
        - keep_last: Keep the last feat found
        - error: Raise an error on conflict
        """
        for feat in feats_list:
            # UUID conflict detection (same feat, same mod or conflict)
            if feat.uuid in self.feats:
                existing = self.feats[feat.uuid]
                self.conflicts.append((feat.uuid, existing.source_mod, feat.source_mod))
                
                if strategy == "keep_first":
                    continue
                elif strategy == "keep_last":
                    self.feats[feat.uuid] = feat
                elif strategy == "error":
                    raise ValueError(f"UUID conflict: {feat.uuid} exists in {existing.source_mod} and {feat.source_mod}")
            else:
                self.feats[feat.uuid] = feat
            
            # Semantic duplicate detection (same base name, different UUIDs)
            semantic_name = feat.get_semantic_name().lower()
            if semantic_name not in self.semantic_duplicates:
                self.semantic_duplicates[semantic_name] = []
            
            # Check if this feat (by UUID) is already in the list
            if not any(f.uuid == feat.uuid for f in self.semantic_duplicates[semantic_name]):
                self.semantic_duplicates[semantic_name].append(feat)
    
    def get_semantic_duplicates(self) -> Dict[str, List[Feat]]:
        """Return semantic duplicates (feats with same base name but different UUIDs)"""
        return {name: feats for name, feats in self.semantic_duplicates.items() if len(feats) > 1}
    
    def get_sorted_feats(self) -> List[Feat]:
        """Return feats sorted alphabetically by name"""
        return sorted(self.feats.values(), key=lambda f: f.get_sort_key())
    
    def create_excluded_feat(self, original_feat: 'Feat', reason: str = "") -> 'Feat':
        """
        Create a locked version of a feat that sorts at the bottom of the list.
        
        The feat:
        - Keeps the same UUID (to match the original)
        - Keeps all original attributes (PassivesAdded, Selectors, Description)
        - Adds an impossible requirement (Charisma 30) so it can't be selected
        - Name prefixed with zzz_ for bottom sorting (stripped on display)
        
        The source mod will overlay its own version on top (same UUID),
        so the player sees the mod's unlocked version. This locked copy
        serves as a sorted placeholder in the base list.
        """
        # Copy all original attributes
        new_attrs = dict(original_feat.attributes)
        
        # Add the lock: Charisma 30 requirement (impossible)
        new_attrs["Requirements"] = ("LSString", "FeatRequirementAbilityGreaterEqual('Charisma',30)")
        
        excluded = Feat(
            name=f"zzz_{original_feat.name}",
            uuid=original_feat.uuid,
            attributes=new_attrs,
            source_mod="Excluded"
        )
        return excluded
    
    def neutralize_feats(self, neutralize_list: List['NeutralizedFeat']) -> int:
        """
        Lock specified feats with an impossible Charisma 30 requirement
        and sort them to the bottom of the list (zzz_ prefix).
        
        The feat keeps all its original data (PassivesAdded, Selectors, etc.)
        so it displays correctly in-game without "ERROR: No Feat Description".
        
        Args:
            neutralize_list: List of NeutralizedFeat objects with UUIDs to lock
            
        Returns:
            Number of feats locked
        """
        count = 0
        for item in neutralize_list:
            uuid = item.uuid.lower().strip()
            reason = item.reason
            
            # Find the feat by UUID
            matching_uuid = None
            original_feat = None
            for feat_uuid in list(self.feats.keys()):
                if feat_uuid.lower() == uuid:
                    matching_uuid = feat_uuid
                    original_feat = self.feats[feat_uuid]
                    break
            
            if matching_uuid and original_feat:
                excluded = self.create_excluded_feat(original_feat, reason)
                self.feats[matching_uuid] = excluded
                self.log(f"  [EXCLUDE] {original_feat.name} ({original_feat.source_mod}) -> locked (Charisma 30) + sorted last")
                if reason:
                    self.log(f"            Reason: {reason}")
                count += 1
            else:
                self.log(f"  [SKIP] UUID {uuid[:16]}... not found in loaded feats")
                if reason:
                    self.log(f"         ({reason})")
        
        return count
    
    def rename_feats(self, renames_list: List['RenamedFeat']) -> int:
        """
        Rename feats for better sorting.
        
        This changes the feat's Name attribute so it sorts correctly,
        while the in-game display name (from localization) remains unchanged.
        
        Args:
            renames_list: List of RenamedFeat objects with original->new name mappings
            
        Returns:
            Number of feats renamed
        """
        count = 0
        for item in renames_list:
            original_name = item.original_name.strip()
            new_name = item.new_name.strip()
            
            if not original_name or not new_name:
                continue
            
            # Find feat by name
            found_uuid = None
            for feat_uuid, feat in self.feats.items():
                if feat.name == original_name:
                    found_uuid = feat_uuid
                    break
            
            if found_uuid:
                old_name = self.feats[found_uuid].name
                self.feats[found_uuid].name = new_name
                self.log(f"  [RENAME] {old_name} -> {new_name}")
                count += 1
            else:
                self.log(f"  [SKIP] Feat '{original_name}' not found")
        
        return count
    
    def generate_xml(self, feats: List[Feat], version: Tuple[int, int, int, int] = (4, 0, 9, 322)) -> str:
        """Generate the Feats.lsx XML file"""
        
        # Create XML structure
        root = ET.Element("save")
        
        # Version
        version_elem = ET.SubElement(root, "version")
        version_elem.set("major", str(version[0]))
        version_elem.set("minor", str(version[1]))
        version_elem.set("revision", str(version[2]))
        version_elem.set("build", str(version[3]))
        
        # Region Feats
        region = ET.SubElement(root, "region")
        region.set("id", "Feats")
        
        root_node = ET.SubElement(region, "node")
        root_node.set("id", "root")
        
        children = ET.SubElement(root_node, "children")
        
        # Add each feat
        for feat in feats:
            feat_node = ET.SubElement(children, "node")
            feat_node.set("id", "Feat")
            
            # Preferred attribute order for readability
            attr_order = ["CanBeTakenMultipleTimes", "Name", "PassivesAdded", "PassivesRemoved", 
                         "Requirements", "Selectors", "UUID"]
            
            # Add attributes in preferred order
            added_attrs = set()
            for attr_id in attr_order:
                if attr_id == "Name":
                    # Name is stored separately in feat.name, not in attributes
                    attr_elem = ET.SubElement(feat_node, "attribute")
                    attr_elem.set("id", "Name")
                    attr_elem.set("type", "FixedString")
                    attr_elem.set("value", feat.name)
                    added_attrs.add("Name")
                elif attr_id in feat.attributes:
                    attr_type, attr_value = feat.attributes[attr_id]
                    attr_elem = ET.SubElement(feat_node, "attribute")
                    attr_elem.set("id", attr_id)
                    attr_elem.set("type", attr_type)
                    attr_elem.set("value", attr_value)
                    added_attrs.add(attr_id)
            
            # Add remaining attributes
            for attr_id, (attr_type, attr_value) in feat.attributes.items():
                if attr_id not in added_attrs:
                    attr_elem = ET.SubElement(feat_node, "attribute")
                    attr_elem.set("id", attr_id)
                    attr_elem.set("type", attr_type)
                    attr_elem.set("value", attr_value)
        
        # Format XML with indentation
        xml_string = ET.tostring(root, encoding='unicode')
        
        # Parse and reformat with minidom for better indentation
        dom = minidom.parseString(xml_string)
        pretty_xml = dom.toprettyxml(indent="    ", encoding=None)
        
        # Clean up XML (remove extra declaration and empty lines)
        lines = pretty_xml.split('\n')
        clean_lines = []
        prev_empty = False
        for line in lines:
            is_empty = not line.strip()
            if is_empty and prev_empty:
                continue
            clean_lines.append(line)
            prev_empty = is_empty
        
        # Replace declaration with BG3's format
        clean_lines[0] = '<?xml version="1.0" encoding="UTF-8"?>'
        
        return '\n'.join(clean_lines)
    
    def generate_meta_lsx(self, config: ConfigFile, mod_uuid: str) -> str:
        """Generate meta.lsx file for the mod"""
        template = '''<?xml version="1.0" encoding="UTF-8"?>
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
                    <attribute id="UUID" type="FixedString" value="{uuid}"/>
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
        
        # Build description with version and sources
        sources_str = ", ".join(self.sources_loaded[i].name for i in range(len(self.sources_loaded)))
        full_description = f"{config.description} v{config.version} - Includes: {sources_str}"
        
        return template.format(
            author=config.author,
            description=full_description,
            folder=config.name,
            name=config.name,
            uuid=mod_uuid,
            version64=config.version.to_version64()
        )
    
    def generate_info_json(self, config: ConfigFile, mod_uuid: str) -> str:
        """Generate info.json for mod managers"""
        info = {
            "Mods": [
                {
                    "Author": config.author,
                    "Name": config.name,
                    "Folder": config.name,
                    "Version": str(config.version),
                    "Description": config.description,
                    "UUID": mod_uuid,
                    "Created": datetime.now().isoformat(),
                    "MD5": ""
                }
            ]
        }
        return json.dumps(info, indent=2, ensure_ascii=False)
    
    def generate_changelog(self, config: ConfigFile) -> str:
        """Generate changelog markdown file"""
        lines = [
            f"# {config.name} - Changelog\n",
            f"## Current Version: {config.version}\n",
            ""
        ]
        
        for version, changes in config.changelog.items():
            lines.append(f"### v{version}")
            lines.append(f"- {changes}")
            lines.append("")
        
        # Add sources info
        lines.append("## Included Mods\n")
        for source in self.sources_loaded:
            lines.append(f"- **{source.name}** (v{source.version}): {source.feats_count} feats")
        
        return '\n'.join(lines)
    
    def process_config(self, config: ConfigFile, sources_dir: Path, output_dir: Path) -> bool:
        """
        Process a configuration and generate the mod
        
        Args:
            config: Configuration to process
            sources_dir: Directory containing source mod folders
            output_dir: Directory for output files
            
        Returns:
            True if successful, False otherwise
        """
        self.log(f"\n{'='*60}")
        self.log(f"ABCs of Feats - Generating: {config.name}")
        self.log(f"Version: {config.version}")
        self.log(f"{'='*60}\n")
        
        # Load sources
        self.log(f"[LOAD] Loading sources from: {sources_dir}")
        
        for source_name in config.sources:
            source_path = sources_dir / source_name
            if not source_path.exists():
                self.log(f"  [ERROR] Source not found: {source_name}")
                continue
            
            feats_file = self.find_feats_file(source_path)
            if not feats_file:
                self.log(f"  [ERROR] No Feats.lsx found in: {source_name}")
                continue
            
            # Parse feats
            feats = self.parse_feats_file(feats_file, source_name)
            self.merge_feats(feats, "keep_last")  # Later sources override earlier ones
            
            # Track source info
            source_version = self.get_source_version(source_path)
            self.sources_loaded.append(ModSource(
                name=source_name,
                path=source_path,
                version=source_version,
                feats_count=len(feats)
            ))
        
        if not self.feats:
            self.log("[ERROR] No feats found!")
            return False
        
        # Statistics
        self.log(f"\n[STATS] Statistics:")
        self.log(f"   - Unique feats: {len(self.feats)}")
        self.log(f"   - UUID conflicts resolved: {len(self.conflicts)}")
        
        if self.conflicts and self.verbose:
            self.log(f"\n[WARN] UUID conflicts (same UUID in multiple mods):")
            for uuid, mod1, mod2 in self.conflicts[:10]:
                self.log(f"   - {uuid[:8]}... : {mod1} → {mod2} (kept {mod2})")
            if len(self.conflicts) > 10:
                self.log(f"   ... and {len(self.conflicts) - 10} more")
        
        # Semantic duplicates
        semantic_dups = self.get_semantic_duplicates()
        if semantic_dups and self.verbose:
            self.log(f"\n[DUPE] Semantic duplicates detected ({len(semantic_dups)} groups):")
            self.log(f"   (Feats with same base name but from different mods)")
            for name, feats in list(semantic_dups.items())[:10]:
                feat_list = ", ".join([f"{f.name} ({f.source_mod})" for f in feats])
                self.log(f"   - '{name}': {feat_list}")
            if len(semantic_dups) > 10:
                self.log(f"   ... and {len(semantic_dups) - 10} more groups")
        
        # Neutralize specified feats
        if config.neutralize:
            self.log(f"\n[NEUTRALIZE] Processing {len(config.neutralize)} feat(s) to neutralize...")
            neutralized_count = self.neutralize_feats(config.neutralize)
            self.log(f"   {neutralized_count} feat(s) neutralized")
        
        # Rename specified feats
        if config.renames:
            self.log(f"\n[RENAME] Processing {len(config.renames)} feat rename(s)...")
            renamed_count = self.rename_feats(config.renames)
            self.log(f"   {renamed_count} feat(s) renamed")
        
        # Apply sort aliases
        if config.sort_aliases:
            Feat.set_sort_aliases(config.sort_aliases)
            self.log(f"\n[ALIAS] {len(config.sort_aliases)} sort alias(es) configured:")
            for original, alias in config.sort_aliases.items():
                self.log(f"   - {original} -> sorted as {alias}")
        
        # Sort feats
        sorted_feats = self.get_sorted_feats()
        self.log(f"\n[SORT] Sorting {len(sorted_feats)} feats alphabetically...")
        self.log(f"   XML version: {self.latest_version[0]}.{self.latest_version[1]}.{self.latest_version[2]}.{self.latest_version[3]}")
        
        # Generate mod UUID (consistent for same config name)
        mod_uuid = str(uuid_lib.uuid5(uuid_lib.NAMESPACE_DNS, config.name))
        
        # Create output structure
        mod_root = output_dir / config.name
        mods_dir = mod_root / "Mods" / config.name
        public_dir = mod_root / "Public" / config.name / "Feats"
        
        mods_dir.mkdir(parents=True, exist_ok=True)
        public_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate files
        # 1. Feats.lsx
        xml_content = self.generate_xml(sorted_feats, self.latest_version)
        feats_output = public_dir / "Feats.lsx"
        with open(feats_output, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        self.log(f"\n[OK] Generated: {feats_output}")
        
        # 2. meta.lsx
        meta_content = self.generate_meta_lsx(config, mod_uuid)
        meta_output = mods_dir / "meta.lsx"
        with open(meta_output, 'w', encoding='utf-8') as f:
            f.write(meta_content)
        self.log(f"[OK] Generated: {meta_output}")
        
        # 3. info.json
        info_content = self.generate_info_json(config, mod_uuid)
        info_output = mod_root / "info.json"
        with open(info_output, 'w', encoding='utf-8') as f:
            f.write(info_content)
        self.log(f"[OK] Generated: {info_output}")
        
        # 4. Changelog
        changelog_content = self.generate_changelog(config)
        changelog_output = mod_root / "CHANGELOG.md"
        with open(changelog_output, 'w', encoding='utf-8') as f:
            f.write(changelog_content)
        self.log(f"[OK] Generated: {changelog_output}")
        
        # Preview
        self.log(f"\n[LIST] First feats (alphabetical order):")
        for feat in sorted_feats[:10]:
            self.log(f"   - {feat.name}")
        if len(sorted_feats) > 10:
            self.log(f"   ... and {len(sorted_feats) - 10} more")
        
        self.log(f"\n{'='*60}")
        self.log(f"[DONE] Mod ready to pack in: {mod_root}")
        self.log(f"{'='*60}\n")
        
        return True
    
    def analyze_sources(self, sources_dir: Path) -> Dict[str, List[Feat]]:
        """
        Analyze all sources and return semantic duplicates
        
        Args:
            sources_dir: Directory containing source mod folders
            
        Returns:
            Dictionary of semantic duplicates
        """
        self.log(f"\n{'='*60}")
        self.log("ABCs of Feats - Source Analysis")
        self.log(f"{'='*60}\n")
        
        self.log(f"[SCAN] Scanning: {sources_dir}\n")
        
        total_feats = 0
        for source_path in sources_dir.iterdir():
            if not source_path.is_dir():
                continue
            
            feats_file = self.find_feats_file(source_path)
            if not feats_file:
                continue
            
            feats = self.parse_feats_file(feats_file, source_path.name)
            self.merge_feats(feats, "keep_first")
            total_feats += len(feats)
            
            self.sources_loaded.append(ModSource(
                name=source_path.name,
                path=source_path,
                version=self.get_source_version(source_path),
                feats_count=len(feats)
            ))
        
        self.log(f"\n[STATS] Analysis Results:")
        self.log(f"   - Sources scanned: {len(self.sources_loaded)}")
        self.log(f"   - Total feats: {total_feats}")
        self.log(f"   - Unique feats: {len(self.feats)}")
        self.log(f"   - UUID conflicts: {len(self.conflicts)}")
        
        semantic_dups = self.get_semantic_duplicates()
        self.log(f"   - Semantic duplicates: {len(semantic_dups)} groups")
        
        if semantic_dups:
            self.log(f"\n[DUPE] Semantic Duplicates Detail:\n")
            for name, feats in semantic_dups.items():
                self.log(f"   '{name}':")
                for feat in feats:
                    self.log(f"      - {feat.name} ({feat.source_mod}) UUID: {feat.uuid[:8]}...")
                self.log("")
        
        return semantic_dups


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="ABCs of Feats - Merge and sort feats from multiple mods"
    )
    
    parser.add_argument(
        '--config', '-c',
        type=Path,
        help='Path to configuration YAML file'
    )
    
    parser.add_argument(
        '--analyze', '-a',
        type=Path,
        help='Analyze sources directory for duplicates'
    )
    
    parser.add_argument(
        '--sources', '-s',
        type=Path,
        default=Path('./sources'),
        help='Path to sources directory (default: ./sources)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=Path,
        default=Path('./output'),
        help='Path to output directory (default: ./output)'
    )
    
    # Version bumping disabled - use BG3 Multitool for version management
    # parser.add_argument(
    #     '--bump',
    #     choices=['major', 'minor', 'patch'],
    #     help='Bump version before generating'
    # )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress verbose output'
    )
    
    args = parser.parse_args()
    
    sorter = BG3FeatsSorter(verbose=not args.quiet)
    
    # Analyze mode
    if args.analyze:
        sorter.analyze_sources(args.analyze)
        return
    
    # Config mode
    if args.config:
        if not args.config.exists():
            print(f"Error: Config file not found: {args.config}")
            sys.exit(1)
        
        config = ConfigFile.from_yaml(args.config)
        
        # Version bumping disabled - use BG3 Multitool for version management
        # if args.bump:
        #     config.version = config.version.bump(args.bump)
        #     config.changelog[str(config.version)] = f"Version bump ({args.bump})"
        #     config.to_yaml(args.config)
        #     print(f"Version bumped to {config.version}")
        
        success = sorter.process_config(config, args.sources, args.output)
        sys.exit(0 if success else 1)
    
    # No mode specified
    parser.print_help()


if __name__ == "__main__":
    main()
