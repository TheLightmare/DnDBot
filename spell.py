import json
from settings import *
import asyncio
import discord
import util


class Spell():
    def __init__(self):
        self.name = None
        self.level = None
        self.description = None

    def load(self, name):
        with open(CONTENT_FOLDER + "spells/" + "spells.json", 'r') as f:
            spells = json.load(f)
        spell = spells[name]
        self.name = spell["name"]
        self.level = spell["level"]
        self.description = spell["description"]

    def copy(self):
        spell = Spell()
        spell.name = self.name
        spell.level = self.level
        spell.description = self.description
        return spell
