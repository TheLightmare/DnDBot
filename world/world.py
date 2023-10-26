from util.graph import *
from util.building import *
from npc import *

class City(Node):
    def __init__(self, name, id):
        super().__init__(name, id)
        self.description = ""
        self.npcs = []
        self.buildings = []
        self.players = []



    def add_npc(self, npc):
        self.npcs.append(npc)
        # add the npc to the building he is in
        for building in self.buildings:
            if building.id == npc.building:
                building.add_npc(npc)
                break


    def add_building(self, building):
        self.buildings.append(building)

    def add_player(self, player):
        self.players.append(player)

    def remove_npc(self, npc):
        self.npcs.remove(npc)
        # remove the npc from the building he is in
        for building in self.buildings:
            if building.id == npc.building:
                building.remove_npc(npc)
                break

    def remove_player(self, player):
        self.players.remove(player)
        # remove the player from the building he is in
        for building in self.buildings:
            if building.id == player.current_building:
                building.remove_player(player)
                break

    def get_building(self, id):
        for building in self.buildings:
            if building.id == id:
                return building
        return None


class Road(Edge):
    def __init__(self, name, id, node1, node2):
        super().__init__(name, id, node1, node2)
        self.event_pool = []
        self.distance = 0

    def set_distance(self, distance):
        self.distance = distance



class World(Graph):
    def __init__(self):
        super().__init__()
        # list of cities, separate from the graph
        self.cities = []
        # list of roads, separate from the graph
        self.roads = []

        self.load()
        self.starting_location = self.get_node("marienburg")

        # time goes from 0 to 24
        self.time = 12
        self.weather = "sunny"

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

        with open(CONTENT_FOLDER + "world/" + "world_map.json", 'w') as f:
            json.dump(world, f, indent=4)



    # load the world from a json file, in adjacency list format
    def load(self):
        with open(CONTENT_FOLDER + "world/" + "world_map.json", 'r') as f:
            world = json.load(f)


        # clear the graph
        self.clear()
        self.cities = []
        self.roads = []

        cities = world["cities"]
        roads = world["roads"]

        # load buildings
        with open(CONTENT_FOLDER + "world/" + "buildings.json", 'r') as f:
            buildings = json.load(f)

        for city_json in cities:
            city = City(cities[city_json]["name"], city_json)
            city.description = cities[city_json]["description"]

            for building_id in cities[city_json]["buildings"]:
                building_dict = buildings[building_id]
                building = Building(city, building_id)
                building.load(building_dict)
                city.buildings.append(building)

            for npc_id in cities[city_json]["npcs"]:
                npc = NPC()
                npc.load(npc_id)
                city.add_npc(npc)

            self.cities.append(city)
            self.add_node(city)

        # load roads
        for road_json in roads:
            # get starting and ending cities
            node1 = self.get_node(roads[road_json]["path"][0])
            node2 = self.get_node(roads[road_json]["path"][1])
            road = Road(roads[road_json]["name"], road_json, node1, node2)
            road.set_distance(roads[road_json]["distance"])

            self.roads.append(road)
            self.add_edge(road)


        # add neighbors to cities
        for city in self.cities:
            for road in self.roads:
                if road.node1.id == city.id:
                    city.add_neighbor(road.node2)
                elif road.node2.id == city.id:
                    city.add_neighbor(road.node1)


