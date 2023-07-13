from world import World

# class to manage time, turn based events, weather, etc.
class TimeManager():
    def __init__(self, world: World):
        self.world = world
        self.turn_order = []
        self.turn = 0


