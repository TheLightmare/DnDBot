import json
from npc import *
from npc import NPC



# abstract class for all buildings
class Building():
    def __init__(self, city, id):
        self.city = city
        self.name = ""
        self.id = id
        self.description = ""
        self.npcs = []
        self.players = []

        self.tags = []

    def load(self, dict):
        self.name = dict["name"]
        self.description = dict["description"]
        self.tags = dict["tags"]

    def get_npc(self, id):
        for npc in self.npcs:
            if npc.id == id:
                return npc
        return None

    def add_npc(self, npc):
        self.npcs.append(npc)

    def add_player(self, player):
        self.players.append(player)

    def remove_npc(self, npc):
        self.npcs.remove(npc)

    def remove_player(self, player):
        self.players.remove(player)

    def get_present_npcs(self):
        return self.npcs

    def get_present_players(self):
        return self.players


