from util.settings import *
import json

# abstract Item class for everything basically
class Item():
    def __init__(self, id):
        self.id = id

        # fancy stuff
        self.name = ""
        self.description = ""
        self.image = None

        self.value = 0

        # How many times you can use the item (set to -1 for unlimited uses)
        self.durability = -1

        # How many per slot
        self.max_stack = 1

        # stores as strings all the weird effects it has
        self.properties = {
            "usable_on": [],
        }

    def load(self):
        with open(CONTENT_FOLDER + "items/" + "items.json", "r") as f:
            items_dict = json.load(f)

        item = items_dict[self.id]
        self.name = item["name"]
        self.description = item["description"]
        self.image = item["image"]
        self.value = item["value"]
        self.durability = item["durability"]
        self.max_stack = item["max_stack"]
        self.properties = item["properties"]

    def use(self):
        pass


# Generic potion class, should work for every potion with no inheritance needed
class Potion(Item):
    def __init__(self, id):
        super().__init__(id)
        self.stack = 3

        # directly load the potion on init
        self.load()

    def load(self):
        with open(CONTENT_FOLDER + "items/" + "potions.json", "r") as f:
            potions_dict = json.load(f)

        potion = potions_dict[self.id]
        self.name = potion["name"]
        self.description = potion["description"]

class Weapon(Item):
    def __init__(self, id):
        super().__init__(id)

        # directly load the weapon on init
        self.tier = None
        self.attack = None
        self.twoHanded = False

        self.load()

    def load(self):
        with open(CONTENT_FOLDER + "items/" + "weapons.json", "r") as f:
            weapons_dict = json.load(f)

        weapon = weapons_dict[self.id]
        self.name = weapon["name"]
        self.description = weapon["description"]
        self.image = weapon["image"]
        self.twoHanded = weapon["twoHanded"]
        self.attack = weapon["attack"]
        self.tier = weapon["tier"]
        self.value = weapon["value"]

# MISCELLANEOUS ITEMS (often lolz)

# this item is unique in the game, and its purpose is mysterious...
class EndOfEverything(Item):
    def __init__(self):
        super().__init__()

        self.id = "end_of_everything"
        self.name = "End of Everything"

        self.description = "You feel like you should not be having this..."


