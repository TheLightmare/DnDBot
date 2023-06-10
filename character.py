import json
import settings

import asyncio
import discord


class Character():
    def __init__(self, author: discord.Member):
        self.author = author

        self.name = None
        self.age = None
        self.race = None
        self.job = None

        self.level = 1
        self.xp = 0

        self.stats = {
            "strength": 10,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10
        }

        self.inventory = []

        self.spells = []

    def load(self):
        with open(settings.CHARACTER_FOLDER + 'characters.json', 'r') as f:
            characters = json.load(f)

        if str(self.author.id) in characters:
            # load character
            character = characters[str(self.author)]
            #load stats
            self.stats = character["stats"]
            #load race
            self.race = character["race"]
            #load job
            self.job = character["job"]
            #load inventory
            self.inventory = character["inventory"]
            #load spells
            self.spells = character["spells"]
            #load level
            self.level = character["level"]
            #load xp
            self.xp = character["xp"]
            #load name
            self.name = character["name"]
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

            "stats": self.stats,
            "inventory": self.inventory,
            "spells": self.spells

        }

        with open(settings.CHARACTER_FOLDER + 'characters.json', 'w') as f:
            json.dump(characters, f, indent=4)