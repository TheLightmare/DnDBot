import json
from util.settings import *
import discord

import util
from spell import Spell

class Character():
    def __init__(self, author: discord.Member):
        self.author = author

        self.name = None
        self.age = None
        self.race = None
        self.job = None

        self.level = 1
        self.xp = 0
        self.unspent_points = 10

        self.gold = 10

        # HP = Hit Points
        self.max_hp = 10
        self.current_hp = 10

        # current location, you start nowhere because you are a loser
        self.current_location = None
        self.current_building = None

        # AC = Armor Class
        self.armor_class = 10

        self.stats = {
            "strength": 10,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10
        }
        self.stat_modifiers = {
            "strength": {
                "race": 0
            },
            "dexterity": {
                "race": 0
            },
            "constitution": {
                "race": 0
            },
            "intelligence": {
                "race": 0
            },
            "wisdom": {
                "race": 0
            },
            "charisma": {
                "race": 0
            }
        }

        self.features = []

        # TODO : rework inventory system with dicts (to keep track of item stacks)
        self.inventory = []

        self.available_spells = []
        self.spell_slots = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.spells = [
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            []
        ]

        self.proficiencies = []
        self.proficiency_bonus = 2


    def set_race(self, race_name):
        races = util.load_races()
        race = races[race_name]

        self.race = race["name"]
        stat_bonus = race["stat_bonus"]
        for stat in stat_bonus:
            value = stat_bonus[stat]
            self.stat_modifiers[stat]["race"] = value

    def set_job(self, job_name):
        classes = util.load_classes()
        job = classes[job_name]

        self.job = job["name"]
        self.spell_slots = job["levelup_pattern"][0]["spell_slots"]
        self.proficiency_bonus = job["levelup_pattern"][0]["proficiency_bonus"]

        # load available spells
        spells = util.load_spells()
        for spell in spells:
            if spells[spell]["available"] == job_name:
                self.available_spells.append(spell)

    # basically a warcrime but it works
    # you must increase the level before applying this function
    def apply_level_up(self):
        with open(CONTENT_FOLDER + 'classes/' + 'classes.json', 'r') as f:
            classes = json.load(f)
        job = classes[self.job]
        levelup_pattern = job["levelup_pattern"][self.level - 1]
        self.proficiency_bonus = levelup_pattern["proficiency_bonus"]
        features = levelup_pattern["features"]
        self.spell_slots = levelup_pattern["spell_slots"]

        for feature in features:
            # ability score improvements are managed differently
            if feature != "Ability Score Improvement":
                self.features.append(feature)
            else :
                self.unspent_points += 2


    def move_location(self, location):
        self.current_location = location
        self.current_location.add_player(self)

    def move_building(self, building):
        self.current_building = building
        self.current_building.add_player(self)

    def get_modifier(self, stat):
        modifier = 0
        for source in self.stat_modifiers[stat]:
            modifier += self.stat_modifiers[stat][source]
        return modifier


    def get_attack_stat(self):
        if self.job == "Fighter":
            return "strength"
        elif self.job == "Rogue":
            return "dexterity"
        elif self.job == "Wizard":
            return "intelligence"
        elif self.job == "Cleric":
            return "wisdom"
        elif self.job == "Bard":
            return "charisma"
        else:
            return "strength"

    def get_roll_bonus(self, stat):
        total = self.get_modifier(stat) + self.stats[stat]
        # returns the roll bonus, not the modifier
        if total >= 18:
            return 4
        elif total >= 16:
            return 3
        elif total >= 14:
            return 2
        elif total >= 12:
            return 1
        elif total >= 10:
            return 0
        elif total >= 8:
            return -1
        elif total >= 6:
            return -2
        elif total >= 4:
            return -3
        elif total >= 2:
            return -4
        else:
            return -5



    def get_spell(self, spell_name):
        for tier in self.spells:
            for spell in tier:
                if spell.name == spell_name:
                    return spell
        return None


    # json loading terribleness
    def load(self):
        with open(CHARACTER_FOLDER + 'characters.json', 'r') as f:
            characters = json.load(f)

        if str(self.author.id) in characters:
            # load character
            character = characters[str(self.author.id)]
            #load stats
            self.stats = character["stats"]
            #load stat modifiers
            self.stat_modifiers = character["stat_modifiers"]
            #load race
            self.race = character["race"]
            #load job
            self.job = character["class"]
            #load inventory
            self.inventory = character["inventory"]
            #load spell slots
            self.spell_slots = character["spell_slots"]
            #load spells
            spell_tiers = character["spells"]
            for tier in range(len(spell_tiers)):
                for spell_name in spell_tiers[tier]:
                    spell = Spell()
                    spell.load(spell_name)
                    self.spells[tier].append(spell)
            #load level
            self.level = character["level"]
            #load xp
            self.xp = character["xp"]
            #load unspent points
            self.unspent_points = character["unspent_points"]
            #load gold
            self.gold = character["gold"]
            #load features
            self.features = character["features"]
            #load name
            self.name = character["name"]
            #load age
            self.age = character["age"]
            #load proficiency bonus
            self.proficiency_bonus = character["proficiency_bonus"]
            #load proficiencies
            self.proficiencies = character["proficiencies"]
            #load max hp
            self.max_hp = character["max_hp"]
            #load current hp
            self.current_hp = character["current_hp"]
            #load armor class
            self.armor_class = character["armor_class"]
            #load current location
            self.current_location = character["current_location"]
            #load current building
            self.current_building = character["current_building"]
            return True

        return False

    def save(self):
        with open(CHARACTER_FOLDER + 'characters.json', 'r') as f:
            characters = json.load(f)

        spell_names = [[], [], [], [], [], [], [], [], []]
        for tier in range(len(self.spells)):
            for spell in self.spells[tier]:
                spell_names[tier].append(spell.name)

        characters[str(self.author.id)] = {
            "name": self.name,
            "age": self.age,
            "race": self.race,
            "class": self.job,

            "current_location": self.current_location,
            "current_building": self.current_building,

            "level": self.level,
            "xp": self.xp,
            "unspent_points": self.unspent_points,
            "gold": self.gold,

            "max_hp": self.max_hp,
            "current_hp": self.current_hp,
            "armor_class": self.armor_class,

            "proficiencies": self.proficiencies,
            "proficiency_bonus": self.proficiency_bonus,

            "stats": self.stats,
            "stat_modifiers": self.stat_modifiers,
            "features": self.features,

            "inventory": self.inventory,
            "spell_slots": self.spell_slots,
            "spells": spell_names
        }

        with open(CHARACTER_FOLDER + 'characters.json', 'w') as f:
            json.dump(characters, f, indent=4)

    def delete(self):
        with open(CHARACTER_FOLDER + 'characters.json', 'r') as f:
            characters = json.load(f)

        del characters[str(self.author.id)]

        with open(CHARACTER_FOLDER + 'characters.json', 'w') as f:
            json.dump(characters, f, indent=4)

    def get_spells_dict(self):
        spells = []
        for tier in range(len(self.spells)):
            for spell in self.spells[tier]:
                spells.append(spell.as_dict())
        return spells