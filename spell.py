import json
from util.settings import *


class Spell():
    def __init__(self):
        self.name = None
        self.level = None
        self.description = None

    def cast(self, caster, target = None):
        if target is None:
            return "You cast " + self.name + "!"
        return "You cast " + self.name + " on " + target.name + "! Die !"

    def load(self, id):
        with open(CONTENT_FOLDER + "spells/" + "spells.json", 'r') as f:
            spells = json.load(f)
        spell = spells[id]
        self.name = spell["name"]
        self.level = spell["level"]
        self.description = spell["description"]

    def copy(self):
        spell = Spell()
        spell.name = self.name
        spell.level = self.level
        spell.description = self.description
        return spell

    def as_dict(self):
        return {
            "name": self.name,
            "level": self.level,
            "description": self.description
        }

