import random

from character import Character


class Dice():
    def __init__(self, sides=6):
        self.sides = sides

    # returns a single roll
    def roll(self):
        return random.randint(1, self.sides)

    # returns a list of rolls
    def roll_multiple(self, times):
        results = []
        for i in range(times):
            results.append(self.roll())
        return results

    # returns the sum of the rolls
    def roll_multiple_sum(self, times):
        results = self.roll_multiple(times)
        return sum(results)

    # ability check, returns true if the roll is greater than or equal to the difficulty
    def ability_check(self, character: Character, ability: str, advantage=False, disadvantage=False, difficulty=10):
        roll_bonus = character.get_roll_bonus(ability)
        roll = 0
        if advantage:
            roll = max(self.roll(), self.roll())
        elif disadvantage:
            roll = min(self.roll(), self.roll())
        else:
            roll = self.roll()

        roll += roll_bonus
        return roll >= difficulty

    # attack roll, returns true if the roll is greater than or equal to the target's armor class
    def attack_roll(self, character: Character, target, advantage=False, disadvantage=False):
        attack_stat = character.get_attack_stat()
        roll_bonus = character.get_roll_bonus(attack_stat)
        roll = 0
        if advantage:
            roll = max(self.roll(), self.roll())
        elif disadvantage:
            roll = min(self.roll(), self.roll())

        roll += roll_bonus
        return roll >= target.get_armor_class()