

class Node():
    def __init__(self, name, description, x, y):
        self.name = name
        self.description = description
        self.x = x
        self.y = y
        self.roads = []

    def add_road(self, road):
        self.roads.append(road)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name