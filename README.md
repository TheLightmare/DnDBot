# DnDBot

Discord bot made using discord.py API.

The goal is to make a bot for playing DnD-style game within Discord.
The main features will be :
- DnD character creation
- playing with friends
- travel and explore the world
- hand-crafted dungeons, quests and adventures
- randomly generated dungeons and quests
- fully-fledged combat system for PvE and PvP (both in teams and solo)

I will also try my best to implement a real sense of freedom and "crafting your own stuff". 
For example making an alchemy system, allowing the creation of a potion of love, that you throw on a goblin so he becomes your friend.
Or even crafting your own weapons and tools.

## Character creation

The character creation will be based on the DnD 5e ruleset, but will be simplified to fit the Discord format.
I made as few concessions as possible, and most of them are connected to combat in one way or another.

## Combat

Combat will also be based on DnD 5e ruleset, with a few modifications as to make it more practical and fun in a Discord environment.
Combat will be turn-based, with an actual graphical representation of the battlefield. 
The combat will be played on a grid, with each character having a certain amount of movement points, and a certain amount of action points.
The movement points will be used to move around the battlefield, and the action points will be used to perform actions such as attacking, casting spells, etc.

## Travel and exploration

Travel and exploration will be a big part of the game.
The world is a graph, with each node being a location, and each edge being a path between two locations.
The player will be able to travel from one location to another, and explore the world.

If the player is member of a party, only the party leader can move the party around the world.
If the player is not member of a party, he can move around the world freely.
And party or not, movement within a single location is always free.

## Dungeons, quests and adventures

Dungeons and quests will be either hand-crafted or randomly generated.
As to provide a reliable source of endless fun, and leveling up.

Adventures will be exclusively hand-crafted, with a dedicated interface for the DM to create them.

## Crafting

Crafting will be a big part of the game, as to allow the player to create his own stuff, and to solve puzzles in a creative way.
The crafting system will be quite procedural, and will allow the player to create his own items, weapons, tools, potions, etc.

## Installation and usage

### Installation

First, clone the repository or download the source code.
Then, install the dependencies using pip:
```bash
pip install -r requirements.txt
```

### Usage

To run the bot, you need to create a file named `token.txt` in the root directory of the project, and put your bot token in it.
Then, run the bot using the following command:
```bash
python main.py
```

