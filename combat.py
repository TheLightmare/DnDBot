

class Combat():
    def __init__(self, players : list, player_characters : list, enemies : list):
        self.players = players
        self.player_characters = player_characters
        self.enemies = enemies
        self.turn = 0

        self.initiative_order = []
        # TODO : add a real initiative system, because this is heresy
        self.initiative_order.extend(self.players)
        self.initiative_order.extend(self.enemies)

    def make_turn(self):
        self.turn += 1
        for character in self.initiative_order:
            if character.is_alive():
                # TODO : add a real combat system, because this is heresy
                pass