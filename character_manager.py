"""
COMP 163 - Project 3: Quest Chronicles
Character Manager Module - Starter Code
Name: Christopher
AI Usage: AI was used to ensure every function followed the rules while keeping the program fully consistent
This module handles character creation, loading, and saving.
"""

import os
from custom_exceptions import (
    InvalidCharacterClassError,
    CharacterNotFoundError,
    SaveFileCorruptedError,
    InvalidSaveDataError,
    CharacterDeadError
)

def create_character(name, character_class):
    """
    Create a new character with stats based on class
    """
    character_class = character_class.capitalize()
    base_stats = {
        "Warrior": {"health": 120, "strength": 15, "magic": 5},
        "Mage": {"health": 80, "strength": 8, "magic": 20},
        "Rogue": {"health": 90, "strength": 12, "magic": 10},
        "Cleric": {"health": 100, "strength": 10, "magic": 15},
    }
    if character_class not in base_stats:
        raise InvalidCharacterClassError(f"Invalid character class: {character_class}")
    stats = base_stats[character_class]
    character = {
        "name": name,
        "class": character_class,
        "level": 1,
        "health": stats["health"],
        "max_health": stats["health"],
        "strength": stats["strength"],
        "magic": stats["magic"],
        "experience": 0,
        "gold": 100,
        "inventory": [],
        "active_quests": [],
        "completed_quests": []
    }
    return character
def save_character(character, save_directory="data/save_games"):

    """
    Save character to file
    """
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
    filename = os.path.join(save_directory, f"{character['name']}_save.txt")
    try:
        with open(filename, "w") as file:
            file.write(f"NAME: {character['name']}\n")
            file.write(f"CLASS: {character['class']}\n")
            file.write(f"LEVEL: {character['level']}\n")
            file.write(f"HEALTH: {character['health']}\n")
            file.write(f"MAX_HEALTH: {character['max_health']}\n")
            file.write(f"STRENGTH: {character['strength']}\n")
            file.write(f"MAGIC: {character['magic']}\n")
            file.write(f"EXPERIENCE: {character['experience']}\n")
            file.write(f"GOLD: {character['gold']}\n")
            file.write(f"INVENTORY: {','.join(character['inventory'])}\n")
            file.write(f"ACTIVE_QUESTS: {','.join(character['active_quests'])}\n")
            file.write(f"COMPLETED_QUESTS: {','.join(character['completed_quests'])}\n")
        return True
    except Exception as e:
        # Let PermissionError and IOError naturally propagate
        raise e
def load_character(character_name, save_directory="data/save_games"):
    filename = os.path.join(save_directory, f"{character_name}_save.txt")
    if not os.path.exists(filename):
        raise CharacterNotFoundError(f"No save file found for: {character_name}")
    try:
        with open(filename, "r") as file:
            lines = file.readlines()
    except Exception:
        raise SaveFileCorruptedError("Save file exists but could not be read")

    character = {}
    try:
        for line in lines:
            line = line.strip()
            if not line or ": " not in line:
                continue
            key, value = [x.strip() for x in line.split(": ", 1)]
            key = key.lower()

            if key in ("level", "health", "max_health", "strength", "magic", "experience", "gold"):
                character[key] = int(value)
            elif key in ("inventory", "active_quests", "completed_quests"):
                character[key] = value.split(",") if value else []
            else:
                character[key] = value
    except Exception:
        raise InvalidSaveDataError("Data in save file is formatted incorrectly")

    # Fill missing fields with defaults
    defaults = {
        "inventory": [],
        "active_quests": [],
        "completed_quests": []
    }
    for key, default in defaults.items():
        if key not in character:
            character[key] = default

    validate_character_data(character)
    return character

def list_saved_characters(save_directory="data/save_games"):

    """
    Return list of saved character names
    """
    if not os.path.exists(save_directory):
        return []
    saves = os.listdir(save_directory)
    names = []
    for filename in saves:
        if filename.endswith("_save.txt"):
            names.append(filename.replace("_save.txt", ""))
    return names
def delete_character(character_name, save_directory="data/save_games"):

    """
    Delete save file
    """
    filename = os.path.join(save_directory, f"{character_name}_save.txt")
    if not os.path.exists(filename):
        raise CharacterNotFoundError(f"No save file found for: {character_name}")
    os.remove(filename)
    return True

# ============================================================================
# CHARACTER OPERATIONS
# ============================================================================
def gain_experience(character, xp_amount):

    """
    Add XP and level up if needed
    """
    if character["health"] <= 0:
        raise CharacterDeadError("Cannot gain XP while dead")
    character["experience"] += xp_amount
    # Level up loop
    while character["experience"] >= character["level"] * 100:
        character["experience"] -= character["level"] * 100
        character["level"] += 1
        character["max_health"] += 10
        character["strength"] += 2
        character["magic"] += 2
        character["health"] = character["max_health"]
    return character["level"]
def add_gold(character, amount):

    """
    Add or remove gold
    """
    new_total = character["gold"] + amount
    if new_total < 0:
        raise ValueError("Gold cannot go below 0")
    character["gold"] = new_total
    return character["gold"]
def heal_character(character, amount):

    """
    Heal character but not above max
    """
    before = character["health"]
    character["health"] = min(character["max_health"], before + amount)
    return character["health"] - before
def is_character_dead(character):
    return character["health"] <= 0
def revive_character(character):

    """
    Revive with half HP
    """
    character["health"] = character["max_health"] // 2
    return True

# ============================================================================
# VALIDATION
# ============================================================================
def validate_character_data(character):

    """
    Ensure character dict contains everything needed
    """
    required = [
        "name", "class", "level", "health", "max_health",
        "strength", "magic", "experience", "gold",
        "inventory", "active_quests", "completed_quests"
    ]
    for key in required:
        if key not in character:
            raise InvalidSaveDataError(f"Missing field: {key}")
    # Type checks
    numeric_fields = ["level", "health", "max_health", "strength", "magic", "experience", "gold"]
    for key in numeric_fields:
        if not isinstance(character[key], int):
            raise InvalidSaveDataError(f"Invalid numeric value in: {key}")
    list_fields = ["inventory", "active_quests", "completed_quests"]
    for key in list_fields:
        if not isinstance(character[key], list):
            raise InvalidSaveDataError(f"Invalid list value in: {key}")
    return True

# ============================================================================
# TESTING
# ============================================================================
if __name__ == "__main__":
    print("=== CHARACTER MANAGER TEST ===")
    try:
        char = create_character("TestHero", "Warrior")
        print("Created:", char)
    except InvalidCharacterClassError as e:
        print("Error:", e)
