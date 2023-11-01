import json
from util.settings import *


# abstract class for all NPCs
class NPC():
    def __init__(self):
        self.id = None
        self.name = None
        self.description = None

        # health and armor class
        self.health = 100
        self.max_health = 100
        self.armor_class = 10

        # current location
        self.location = None
        self.building = None

        # image
        self.image = None

        # dialogue
        self.dialogue = []
        self.default_dialogue = []

        # is he a quest giver?
        self.quest = None

        # is he packin' ?
        self.spells = []
        self.inventory = []
        self.gold = 0

        # is merchant?
        self.is_merchant = False


    def load(self, id):
        with open(CONTENT_FOLDER + "world/" + "npcs.json", 'r') as f:
            npcs = json.load(f)
        npc = npcs[id]
        self.id = id
        self.name = npc["name"]
        self.description = npc["description"]
        self.health = npc["health"]
        self.max_health = npc["max_health"]
        self.armor_class = npc["armor_class"]
        self.location = npc["location"]
        self.building = npc["building"]
        self.image = npc["image"]
        self.quest = npc["quest"]
        self.spells = npc["spells"]
        self.inventory = npc["inventory"]
        self.gold = npc["gold"]
        self.is_merchant = npc["is_merchant"]
        self.dialogue = npc["dialogue"]
        self.default_dialogue = npc["default_dialogue"]


    def talk(self, current_line):
        if self.dialogue is None:
            return (self.default_dialogue, True, current_line)
        else:
            if current_line >= len(self.dialogue):
                #self.current_line = 0
                return (self.default_dialogue, True, current_line)
            text = self.dialogue[current_line]
            current_line += 1
            return (text, False, current_line)

    def reset_dialogue(self):
        self.current_line = 0

    def get_available_actions(self):
        actions = ["steal"]
        if self.quest is not None:
            actions.append("demand_quest")
        if self.is_merchant:
            actions.append("demand_trade")
        return actions

    def get_armor_class(self):
        return self.armor_class

    def give_quest(self):
        if self.quest is None:
            return "I have no quest for you."
        else:
            return self.quest

    def buy(self, item):
        if self.is_merchant:
            if item in self.inventory:
                self.inventory.remove(item)
                return "Here you go."
            else:
                return "I don't have that."
        else:
            return "I don't sell anything."

    def sell(self, item):
        if self.is_merchant:
            self.inventory.append(item)
            return "Thank you."
        else:
            return "I don't buy anything."


    def move_to(self, location, building):
        self.location = location
        self.building = building