import json
from npc import *
from npc import NPC



# abstract class for all buildings
class Building():
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.description = ""
        self.npcs = []
        self.players = []

        self.tags = []

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



class CityEntrance(Building):
    def __init__(self):
        super().__init__("City Entrance", "city_entrance")
        self.description = "The entrance to the city. You can see the city walls and the gate. There are guards patrolling the area."
        self.tags = ["entrance"]

class Tavern(Building):
    def __init__(self):
        super().__init__("Tavern", "tavern")
        self.description = "The god forsaken tavern"