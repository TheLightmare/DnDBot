import json
from util.settings import *

# generic quest class
class Quest():
    def __init__(self):
        self.type = None
        self.name = None
        self.id = None
        self.description = None
        self.difficulty = None
        self.rewards = None
        self.max_participants = 4

        self.is_completed = False
        self.is_active = False

        self.tasks = []

        # list of players who have accepted the quest
        # there should be several participants only if the quest is a group quest
        self.participants = []

    def load(self, name):
        with open(CONTENT_FOLDER + "quests/" + "quests.json", 'r') as f:
            quests = json.load(f)
        quest = quests[name]
        self.type = quest["type"]
        self.name = quest["name"]
        self.id = quest["id"]
        self.description = quest["description"]
        self.rewards = quest["rewards"]
        self.difficulty = quest["difficulty"]
        self.max_participants = quest["max_participants"]
        self.tasks = quest["tasks"]

