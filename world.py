import discord
import asyncio
import json
from settings import *
import util
from graph import *

class City(Node):
    def __init__(self, name):
        super().__init__(name)
        self.npcs = []
        self.buildings = []
        self.players = []
        self.quests = []

    def add_npc(self, npc):
        self.npcs.append(npc)

    def add_building(self, building):
        self.buildings.append(building)

    def add_player(self, player):
        self.players.append(player)

    def add_quest(self, quest):
        self.quests.append(quest)

class Road(Edge):
    def __init__(self, name, node1, node2):
        super().__init__(name, node1, node2)
        self.event_pool = []
        self.distance = 0

    def set_distance(self, distance):
        self.distance = distance



class World(Graph):
    def __init__(self):
        super().__init__()
        self.load()

    # save the world to a json file, in adjacency list format
    def save(self):
        with open(CONTENT_FOLDER + "world/" + "world.json", 'w') as f:
            json.dump(self.adjacency_list(), f)

    # load the world from a json file, in adjacency list format
    def load(self):
        with open(CONTENT_FOLDER + "world/" + "world.json", 'r') as f:
            adjacency_list = json.load(f)
        for node in adjacency_list:
            self.add_node(City(node))
        for node in adjacency_list:
            for neighbor in adjacency_list[node]:
                self.add_edge(Road(node + "-" + neighbor, node, neighbor))

    # return the world as an adjacency list
    def adjacency_list(self):
        adjacency_list = {}
        for node in self.nodes:
            adjacency_list[node.name] = node.neighbors
        return adjacency_list
