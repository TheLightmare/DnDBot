import random

from character import Character


class Dice():
    def __init__(self, sides=6):
        self.sides = sides

    def roll(self):
        return random.randint(1, self.sides)

    def roll_multiple(self, times):
        results = []
        for i in range(times):
            results.append(self.roll())
        return results

    def roll_multiple_sum(self, times):
        results = self.roll_multiple(times)
        return sum(results)

    def ability_check(self, character: Character, ability: str, advantage=False, disadvantage=False, difficulty=10):
        roll_bonus = character.get_roll_bonus(ability)
        roll = 0
        if advantage:
            roll = max(self.roll(), self.roll())
        elif disadvantage:
            roll = min(self.roll(), self.roll())

        roll += roll_bonus
        return roll >= difficulty