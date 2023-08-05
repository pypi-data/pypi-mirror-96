#  Copyright 2020-2021 Parakoopa and the SkyTemple Contributors
#
#  This file is part of SkyTemple.
#
#  SkyTemple is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SkyTemple is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SkyTemple.  If not, see <https://www.gnu.org/licenses/>.
from enum import Enum
from typing import Dict

from skytemple_files.common.util import *
from skytemple_files.common.i18n_util import f, _


NUM_ENTITIES = 600
MD_ENTRY_LEN = 68


class Gender(Enum):
    INVALID = 0
    MALE = 1
    FEMALE = 2
    GENDERLESS = 3


class PokeType(Enum):
    NONE = 0x00
    NORMAL = 0x01
    FIRE = 0x02
    WATER = 0x03
    GRASS = 0x04
    ELECTRIC = 0x05
    ICE = 0x06
    FIGHTING = 0x07
    POISON = 0x08
    GROUND = 0x09
    FLYING = 0x0A
    PSYCHIC = 0x0B
    BUG = 0x0C
    ROCK = 0x0D
    GHOST = 0x0E
    DRAGON = 0x0F
    DARK = 0x10
    STEEL = 0x11
    NEUTRAL = 0x12


class Ability(Enum):
    STENCH = 0x1, _('Stench')
    THICK_FAT = 0x2, _('Thick Fat')
    RAIN_DISH = 0x3, _('Rain Dish')
    DRIZZLE = 0x4, _('Drizzle')
    ARENA_TRAP = 0x5, _('Arena Trap')
    INTIMIDATE = 0x6, _('Intimidate')
    ROCK_HEAD = 0x7, _('Rock Head')
    AIR_LOCK = 0x8, _('Air Lock')
    HYPER_CUTTER = 0x9, _('Hyper Cutter')
    SHADOW_TAG = 0xA, _('Shadow tag')
    SPEED_BOOST = 0xB, _('Speed Boost')
    BATTLE_ARMOR = 0xC, _('Battle Armor')
    STURDY = 0xD, _('Sturdy')
    SUCTION_CUPS = 0xE, _('Suction Cups')
    CLEAR_BODY = 0xF, _('Clear Body')
    TORRENT = 0x10, _('Torrent')
    GUTS = 0x11, _('Guts')
    ROUGH_SKIN = 0x12, _('Rough Skin')
    SHELL_ARMOR = 0x13, _('Shell Armor')
    NATURAL_CURE = 0x14, _('Natural Cure')
    DAMP = 0x15, _('Damp')
    LIMBER = 0x16, _('Limber')
    MAGNET_PULL = 0x17, _('Magnet Pull')
    WHITE_SMOKE = 0x18, _('White Smoke')
    SYNCHRONIZE = 0x19, _('Synchronize')
    OVERGROW = 0x1A, _('Overgrow')
    SWIFT_SWIM = 0x1B, _('Swift Swim')
    SAND_STREAM = 0x1C, _('Sand Stream')
    SAND_VEIL = 0x1D, _('Sand Veil')
    KEEN_EYE = 0x1E, _('Keen Eye')
    INNER_FOCUS = 0x1F, _('Inner Focus')
    STATIC = 0x20, _('Static')
    SHED_SKIN = 0x21, _('Shed Skin')
    HUGE_POWER = 0x22, _('Huge Power')
    VOLT_ABSORB = 0x23, _('Volt Absorb')
    WATER_ABSORB = 0x24, _('Water Absorb')
    FORECAST = 0x25, _('Forecast')
    SERENE_GRACE = 0x26, _('Serene Grace')
    POISON_POINT = 0x27, _('Poison Point')
    TRACE = 0x28, _('Trace')
    OBLIVIOUS = 0x29, _('Oblivious')
    TRUANT = 0x2A, _('Truant')
    RUN_AWAY = 0x2B, _('Run Away')
    STICKY_HOLD = 0x2C, _('Sticky Hold')
    CLOUD_NINE = 0x2D, _('Cloud Nine')
    ILLUMINATE = 0x2E, _('Illuminate')
    EARLY_BIRD = 0x2F, _('Early Bird')
    HUSTLE = 0x30, _('Hustle')
    DROUGHT = 0x31, _('Drought')
    LIGHTNINGROD = 0x32, _('LightningRod')
    COMPOUNDEYES = 0x33, _('CompoundEyes')
    MARVEL_SCALE = 0x34, _('Marvel Scale')
    WONDER_GUARD = 0x35, _('Wonder Guard')
    INSOMNIA = 0x36, _('Insomnia')
    LEVITATE = 0x37, _('Levitate')
    PLUS = 0x38, _('Plus')
    PRESSURE = 0x39, _('Pressure')
    LIQUID_OOZE = 0x3A, _('Liquid Ooze')
    COLOR_CHANGE = 0x3B, _('Color Change')
    SOUNDPROOF = 0x3C, _('Soundproof')
    EFFECT_SPORE = 0x3D, _('Effect Spore')
    FLAME_BODY = 0x3E, _('Flame Body')
    MINUS = 0x3F, _('Minus')
    OWN_TEMPO = 0x40, _('Own Tempo')
    MAGMA_ARMOR = 0x41, _('Magma Armor')
    WATER_VEIL = 0x42, _('Water Veil')
    SWARM = 0x43, _('Swarm')
    CUTE_CHARM = 0x44, _('Cute Charm')
    IMMUNITY = 0x45, _('Immunity')
    BLAZE = 0x46, _('Blaze')
    PICKUP = 0x47, _('Pickup')
    FLASH_FIRE = 0x48, _('Flash Fire')
    VITAL_SPIRIT = 0x49, _('Vital Spirit')
    CHLOROPHYLL = 0x4A, _('Chlorophyll')
    PURE_POWER = 0x4B, _('Pure Power')
    SHIELD_DUST = 0x4C, _('Shield Dust')
    ICE_BODY = 0x4D, _('Ice Body')
    STALL = 0x4E, _('Stall')
    ANGER_POINT = 0x4F, _('Anger Point')
    TINTED_LENS = 0x50, _('Tinted Lens')
    HYDRATION = 0x51, _('Hydration')
    FRISK = 0x52, _('Frisk')
    MOLD_BREAKER = 0x53, _('Mold Breaker')
    UNBURDEN = 0x54, _('Unburden')
    DRY_SKIN = 0x55, _('Dry Skin')
    ANTICIPATION = 0x56, _('Anticipation')
    SCRAPPY = 0x57, _('Scrappy')
    SUPER_LUCK = 0x58, _('Super Luck')
    GLUTTONY = 0x59, _('Gluttony')
    SOLAR_POWER = 0x5A, _('Solar Power')
    SKILL_LINK = 0x5B, _('Skill Link')
    RECKLESS = 0x5C, _('Reckless')
    SNIPER = 0x5D, _('Sniper')
    SLOW_START = 0x5E, _('Slow Start')
    HEATPROOF = 0x5F, _('Heatproof')
    DOWNLOAD = 0x60, _('Download')
    SIMPLE = 0x61, _('Simple')
    TANGLED_FEET = 0x62, _('Tangled Feet')
    ADAPTABILITY = 0x63, _('Adaptability')
    TECHNICIAN = 0x64, _('Technician')
    IRON_FIST = 0x65, _('Iron Fist')
    MOTOR_DRIVE = 0x66, _('Motor Drive')
    UNAWARE = 0x67, _('Unaware')
    RIVALRY = 0x68, _('Rivalry')
    BAD_DREAMS = 0x69, _('Bad Dreams')
    NO_GUARD = 0x6A, _('No Guard')
    NORMALIZE = 0x6B, _('Normalize')
    SOLID_ROCK = 0x6C, _('Solid Rock')
    QUICK_FEET = 0x6D, _('Quick Feet')
    FILTER = 0x6E, _('Filter')
    KLUTZ = 0x6F, _('Klutz')
    STEDFAST = 0x70, _('Stedfast')
    FLOWER_GIFT = 0x71, _('Flower Gift')
    POISION_HEAL = 0x72, _('Poision Heal')
    MAGIC_GUARD = 0x73, _('Magic Guard')
    INVALID = 0x74, _('$$$')
    HONEY_GATHER = 0x75, _('Honey Gather')
    AFTERMATH = 0x76, _('Aftermath')
    SNOW_CLOAK = 0x77, _('Snow Cloak')
    SNOW_WARNING = 0x78, _('Snow Warning')
    FOREWARN = 0x79, _('Forewarn')
    STORM_DRAIN = 0x7A, _('Storm Drain')
    LEAF_GUARD = 0x7B, _('Leaf Guard')
    NONE = 0xFF, _('NONE')
    NULL = 0x00, _('NULL')

    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    # ignore the first param since it's already set by __new__
    def __init__(self, _: str, print_name: str = None):
        self._print_name_ = print_name

    def __str__(self):
        return self._print_name_

    def __repr__(self):
        return f'Ability.{self.name}'

    @property
    def print_name(self):
        return self._print_name_


class IQGroup(Enum):
    A = 0x0
    B = 0x1
    C = 0x2
    D = 0x3
    E = 0x4
    F = 0x5
    G = 0x6
    H = 0x7
    UNUSED8 = 0x8
    UNUSED9 = 0x9
    I = 0xA
    J = 0xB
    UNUSEDC = 0xC
    UNUSEDD = 0xD
    UNUSEDE = 0xE
    INVALID = 0xF


class EvolutionMethod(Enum):
    NONE = 0
    LEVEL = 1       # Params: (Level required, optional evo item ID)
    IQ = 2          # Params: (IQ required, optional evo item ID)
    ITEMS = 3       # Params: (item ID, optional evo item ID)
    UNKNOWN4 = 4
    LINK_CABLE = 5  # Params: (null, 0x01)


class MovementType(Enum):
    STANDARD = 0
    UNKNOWN1 = 1
    HOVERING = 2
    PHASE_THROUGH_WALLS = 3
    LAVA = 4
    WATER = 5


class ShadowSize(Enum):
    SMALL = 0
    MEDIUM = 1
    LARGE = 2


class MdEntry(AutoString):
    def __init__(self, *, bitflag1: int, **data):
        self.md_index: int = -1
        self.entid: int = -1
        self.unk31: int = -1
        self.national_pokedex_number: int = -1
        self.base_movement_speed: int = -1
        self.pre_evo_index: int = -1
        self.evo_method: EvolutionMethod = EvolutionMethod.NONE
        self.evo_param1: int = -1
        self.evo_param2: int = -1
        self.sprite_index: int = -1
        self.gender: Gender = Gender.INVALID
        self.body_size: int = -1
        self.type_primary: PokeType = PokeType.NONE
        self.type_secondary: PokeType = PokeType.NONE
        self.movement_type: MovementType = MovementType.STANDARD
        self.iq_group: IQGroup = IQGroup.INVALID
        self.ability_primary: Ability = Ability.NONE
        self.ability_secondary: Ability = Ability.NONE
        self.bitfield1_0, self.bitfield1_1, self.bitfield1_2, self.bitfield1_3, \
            self.can_move, self.bitfield1_5, self.can_evolve, self.item_required_for_spawning = \
            (bool(bitflag1 >> i & 1) for i in range(8))
        self.exp_yield: int = -1
        self.recruit_rate1: int = -1
        self.base_hp: int = -1
        self.recruit_rate2: int = -1
        self.base_atk: int = -1
        self.base_sp_atk: int = -1
        self.base_def: int = -1
        self.base_sp_def: int = -1
        self.weight: int = -1
        self.size: int = -1
        self.unk17: int = -1
        self.unk18: int = -1
        self.shadow_size: ShadowSize = ShadowSize.SMALL
        self.chance_spawn_asleep: int = -1
        # @End:
        # The % of HP that this pokémon species regenerates at the end of each turn is equal to 1/(value * 2)
        # (Before applying any modifiers)
        # The final value is capped between 1/30 and 1/500
        self.hp_regeneration: int = -1
        self.unk21_h: int = -1
        self.base_form_index: int = -1
        self.exclusive_item1: int = -1
        self.exclusive_item2: int = -1
        self.exclusive_item3: int = -1
        self.exclusive_item4: int = -1
        self.unk27: int = -1
        self.unk28: int = -1
        self.unk29: int = -1
        self.unk30: int = -1

        for key in data:
            if not hasattr(self, key):
                raise KeyError(f"Unknown attribute key {key}.")
            setattr(self, key, data[key])

    @property
    def md_index_base(self):
        return self.md_index % NUM_ENTITIES


class Md:
    def __init__(self, data: bytes):
        if not isinstance(data, memoryview):
            data = memoryview(data)

        number_entries = read_uintle(data, 4, 4)

        self.entries: List[MdEntry] = []
        self._entries_by_entid: Dict[int, List[Tuple[int, MdEntry]]] = {}
        for i in range(0, number_entries):
            rs = lambda offset, length=2: read_sintle(data, 8 + (i * MD_ENTRY_LEN) + offset, length)
            ru = lambda offset, length=2: read_uintle(data, 8 + (i * MD_ENTRY_LEN) + offset, length)

            entry: MdEntry = MdEntry(**{
                'md_index': i,
                'entid': ru(0x00),
                'unk31': ru(0x02),
                'national_pokedex_number': ru(0x04),
                'base_movement_speed': ru(0x06),
                'pre_evo_index': ru(0x08),
                'evo_method': EvolutionMethod(ru(0x0A)),
                'evo_param1': ru(0x0C),
                'evo_param2': ru(0x0E),
                'sprite_index': rs(0x10),
                'gender': Gender(ru(0x12, 1)),
                'body_size': ru(0x13, 1),
                'type_primary': PokeType(ru(0x14, 1)),
                'type_secondary': PokeType(ru(0x15, 1)),
                'movement_type': MovementType(ru(0x16, 1)),
                'iq_group': IQGroup(ru(0x17, 1)),
                'ability_primary': Ability(ru(0x18, 1)),
                'ability_secondary': Ability(ru(0x19, 1)),
                'bitflag1': ru(0x1A),
                'exp_yield': ru(0x1C),
                'recruit_rate1': rs(0x1E),
                'base_hp': ru(0x20),
                'recruit_rate2': rs(0x22),
                'base_atk': ru(0x24, 1),
                'base_sp_atk': ru(0x25, 1),
                'base_def': ru(0x26, 1),
                'base_sp_def': ru(0x27, 1),
                'weight': rs(0x28),
                'size': rs(0x2A),
                'unk17': rs(0x2C, 1),
                'unk18': rs(0x2D, 1),
                'shadow_size': ShadowSize(rs(0x2E, 1)),
                'chance_spawn_asleep': rs(0x2F, 1),
                'hp_regeneration': ru(0x30, 1),
                'unk21_h': rs(0x31, 1),
                'base_form_index': rs(0x32),
                'exclusive_item1': rs(0x34),
                'exclusive_item2': rs(0x36),
                'exclusive_item3': rs(0x38),
                'exclusive_item4': rs(0x3A),
                'unk27': rs(0x3C),
                'unk28': rs(0x3E),
                'unk29': rs(0x40),
                'unk30': rs(0x42),
            })

            self.entries.append(entry)
            if entry.entid not in self._entries_by_entid:
                self._entries_by_entid[entry.entid] = []
            self._entries_by_entid[entry.entid].append((i, entry))

    def get_by_index(self, index) -> MdEntry:
        return self.entries[index]

    def get_by_entity_id(self, index) -> List[Tuple[int, MdEntry]]:
        return self._entries_by_entid[index]

    def __len__(self):
        return len(self.entries)

    def __getitem__(self, key):
        return self.get_by_index(key)

    def __setitem__(self, key, value):
        self.entries[key] = value

    def __delitem__(self, key):
        del self.entries[key]

    def __iter__(self):
        return iter(self.entries)
