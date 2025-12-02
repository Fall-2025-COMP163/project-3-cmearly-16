"""
COMP 163 - Project 3: Quest Chronicles
Game Data Module
Name: Christopher
AI Usage: AI used to assist in the def parse items section of code, was having trouble properly implementing what I wanted there.
This module handles loading and validating game data from text files.
"""

import os
from custom_exceptions import (
    InvalidDataFormatError,
    MissingDataFileError,
    CorruptedDataError
)

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================
def load_quests(filename="data/quests.txt"):
    """Load quests from file and return dictionary"""
    if not os.path.exists(filename):
        raise MissingDataFileError("Quest data file not found")
    try:
        with open(filename, "r") as f:
            content = f.read().strip()
    except Exception as e:
        raise CorruptedDataError(f"Failed to read quest file: {e}")
    if content == "":
        return {}
    quests = {}
    blocks = content.split("\n\n")
    for block in blocks:
        lines = block.strip().split("\n")
        quest_data = parse_quest_block(lines)
        validate_quest_data(quest_data)
        quests[quest_data["quest_id"]] = quest_data
    return quests
def load_items(filename="data/items.txt"):
    """Load items from file and return dictionary"""
    if not os.path.exists(filename):
        raise MissingDataFileError("Item data file not found")
    try:
        with open(filename, "r") as f:
            content = f.read().strip()
    except Exception as e:
        raise CorruptedDataError(f"Failed to read item file: {e}")
    if content == "":
        return {}
    items = {}
    blocks = content.split("\n\n")
    for block in blocks:
        lines = block.strip().split("\n")
        item_data = parse_item_block(lines)
        validate_item_data(item_data)
        items[item_data["item_id"]] = item_data
    return items

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================
def validate_quest_data(q):
    required = [
        "quest_id", "title", "description",
        "reward_xp", "reward_gold",
        "required_level", "prerequisite"
    ]
    for key in required:
        if key not in q:
            raise InvalidDataFormatError(f"Missing quest field: {key}")
    if not isinstance(q["reward_xp"], int):
        raise InvalidDataFormatError("reward_xp must be an integer")
    if not isinstance(q["reward_gold"], int):
        raise InvalidDataFormatError("reward_gold must be an integer")
    if not isinstance(q["required_level"], int):
        raise InvalidDataFormatError("required_level must be an integer")
    return True

def validate_item_data(i):
    required = ["item_id", "name", "type", "effect", "cost", "description"]
    for key in required:
        if key not in i:
            raise InvalidDataFormatError(f"Missing item field: {key}")
    if i["type"] not in ["weapon", "armor", "consumable"]:
        raise InvalidDataFormatError("Invalid item type")
    if not isinstance(i["cost"], int):
        raise InvalidDataFormatError("Item cost must be an integer")
    return True

# ============================================================================
# DEFAULT DATA CREATION
# ============================================================================
def create_default_data_files():
    """Create default quests and items files if missing"""
    if not os.path.exists("data"):
        os.makedirs("data")
    try:
        # Default quests
        if not os.path.exists("data/quests.txt"):
            with open("data/quests.txt", "w") as f:
                f.write(
                    "QUEST_ID: quest_intro\n"
                    "TITLE: First Steps\n"
                    "DESCRIPTION: Your first journey begins.\n"
                    "REWARD_XP: 50\n"
                    "REWARD_GOLD: 20\n"
                    "REQUIRED_LEVEL: 1\n"
                    "PREREQUISITE: NONE\n\n"
                )
        # Default items
        if not os.path.exists("data/items.txt"):
            with open("data/items.txt", "w") as f:
                f.write(
                    "ITEM_ID: potion_small\n"
                    "NAME: Small Health Potion\n"
                    "TYPE: consumable\n"
                    "EFFECT: health:20\n"
                    "COST: 10\n"
                    "DESCRIPTION: Restores 20 HP.\n\n"
                )
    except Exception as e:
        raise CorruptedDataError(f"Failed to create default files: {e}")

# ============================================================================
# PARSING HELPERS
# ============================================================================
def parse_quest_block(lines):
    """Parse lines into a quest dictionary"""
    quest = {}
    try:
        for line in lines:
            if ": " not in line:
                raise InvalidDataFormatError("Quest line missing ':' separator")
            key, value = line.split(": ", 1)
            if key == "QUEST_ID":
                quest["quest_id"] = value
            elif key == "TITLE":
                quest["title"] = value
            elif key == "DESCRIPTION":
                quest["description"] = value
            elif key == "REWARD_XP":
                quest["reward_xp"] = int(value)
            elif key == "REWARD_GOLD":
                quest["reward_gold"] = int(value)
            elif key == "REQUIRED_LEVEL":
                quest["required_level"] = int(value)
            elif key == "PREREQUISITE":
                quest["prerequisite"] = value
            else:
                raise InvalidDataFormatError(f"Unknown quest field: {key}")
    except ValueError:
        raise InvalidDataFormatError("Quest contained non-numeric data")
    except Exception as e:
        raise InvalidDataFormatError(f"Quest parsing error: {e}")
    return quest

def parse_item_block(lines):
    """Parse lines into an item dictionary"""
    item = {}
    try:
        for line in lines:
            if ": " not in line:
                raise InvalidDataFormatError("Item line missing ':' separator")
            key, value = line.split(": ", 1)
            if key == "ITEM_ID":
                item["item_id"] = value
            elif key == "NAME":
                item["name"] = value
            elif key == "TYPE":
                item["type"] = value
            elif key == "EFFECT":
                # Example: "strength:5"
                stat, amount = value.split(":")
                item["effect"] = {stat: int(amount)}
            elif key == "COST":
                item["cost"] = int(value)
            elif key == "DESCRIPTION":
                item["description"] = value
            else:
                raise InvalidDataFormatError(f"Unknown item field: {key}")
    except ValueError:
        raise InvalidDataFormatError("Item contained non-numeric data")
    except Exception as e:
        raise InvalidDataFormatError(f"Item parsing error: {e}")
    return item

# ============================================================================
# TESTING
# ============================================================================
if __name__ == "__main__":
    print("=== GAME DATA MODULE TEST ===")
    create_default_data_files()
    try:
        quests = load_quests()
        print("Loaded quests:", quests)
    except Exception as e:
        print("Quest load error:", e)
    try:
        items = load_items()
        print("Loaded items:", items)
    except Exception as e:
        print("Item load error:", e)
