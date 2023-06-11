import json
import settings

import asyncio
import discord

import util


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

        self.inventory = []

        self.spells = []

    def set_race(self, race_name):
        races = util.load_races()
        race = races[race_name]

        self.race = race["name"]
        stat_bonus = race["stat_bonus"]
        for stat in stat_bonus:
            value = stat_bonus[stat]
            self.stat_modifiers[stat]["race"] = value

    def get_modifier(self, stat):
        modifier = 0
        for source in self.stat_modifiers[stat]:
            modifier += self.stat_modifiers[stat][source]
        return modifier


    def load(self):
        with open(settings.CHARACTER_FOLDER + 'characters.json', 'r') as f:
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
            #load spells
            self.spells = character["spells"]
            #load level
            self.level = character["level"]
            #load xp
            self.xp = character["xp"]
            #load unspent points
            self.unspent_points = character["unspent_points"]
            #load name
            self.name = character["name"]
            #load age
            self.age = character["age"]
            return True

        return False

    def save(self):
        with open(settings.CHARACTER_FOLDER + 'characters.json', 'r') as f:
            characters = json.load(f)

        characters[str(self.author.id)] = {
            "name": self.name,
            "age": self.age,
            "race": self.race,
            "class": self.job,

            "level": self.level,
            "xp": self.xp,
            "unspent_points": self.unspent_points,

            "stats": self.stats,
            "stat_modifiers": self.stat_modifiers,

            "inventory": self.inventory,
            "spells": self.spells

        }

        with open(settings.CHARACTER_FOLDER + 'characters.json', 'w') as f:
            json.dump(characters, f, indent=4)

    def delete(self):
        with open(settings.CHARACTER_FOLDER + 'characters.json', 'r') as f:
            characters = json.load(f)

        del characters[str(self.author.id)]

        with open(settings.CHARACTER_FOLDER + 'characters.json', 'w') as f:
            json.dump(characters, f, indent=4)