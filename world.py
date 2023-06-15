import discord
import asyncio
import json
from settings import *
import util
from graph import *

class City(Node):
    def __init__(self, name):
        super().__init__(name)
        self.description = ""
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
        self.starting_location = self.get_node("Marienburg")

    # save the world to a json file
    def save(self):
        world = {}
        world["cities"] = []
        world["roads"] = []

        for node in self.nodes:
            if isinstance(node, City):
                city = {}
                city["name"] = node.name
                city["description"] = node.description
                world["cities"].append(city)

        for edge in self.edges:
            if isinstance(edge, Road):
                road = {}
                road["name"] = edge.name
                road["path"] = [edge.node1, edge.node2]
                road["distance"] = edge.distance
                world["roads"].append(road)

        with open(CONTENT_FOLDER + "map/" + "world_map.json", 'w') as f:
            json.dump(world, f, indent=4)



    # load the world from a json file, in adjacency list format
    def load(self):
        with open(CONTENT_FOLDER + "map/" + "world_map.json", 'r') as f:
            world = json.load(f)

        cities = world["cities"]
        roads = world["roads"]

        for city_json in cities:
            city = City(cities[city_json]["name"])
            city.description = cities[city_json]["description"]

            self.add_node(city)


        for road_json in roads:
            road = Road(road_json, roads[road_json]["path"][0], roads[road_json]["path"][1])
            road.set_distance(roads[road_json]["distance"])

            self.add_edge(road)


