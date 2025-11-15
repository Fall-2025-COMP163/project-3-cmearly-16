"""
Test Exception Handling
Tests that custom exceptions are raised appropriately
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from custom_exceptions import *
import character_manager
import inventory_system
import quest_handler
import game_data

# ============================================================================
# CHARACTER MANAGER EXCEPTION TESTS
# ============================================================================

def test_invalid_character_class_exception():
    """Test that InvalidCharacterClassError is raised for invalid class"""
    with pytest.raises(InvalidCharacterClassError):
        character_manager.create_character("Test", "InvalidClass")

def test_character_not_found_exception():
    """Test that CharacterNotFoundError is raised for missing character"""
    with pytest.raises(CharacterNotFoundError):
        character_manager.load_character("NonexistentCharacter")

def test_character_dead_exception():
    """Test that CharacterDeadError is raised when appropriate"""
    char = character_manager.create_character("Test", "Warrior")
    char['health'] = 0
    
    with pytest.raises(CharacterDeadError):
        character_manager.gain_experience(char, 50)

# ============================================================================
# INVENTORY EXCEPTION TESTS
# ============================================================================

def test_inventory_full_exception():
    """Test that InventoryFullError is raised when inventory is full"""
    char = {'inventory': ['item'] * inventory_system.MAX_INVENTORY_SIZE, 'gold': 100}
    
    with pytest.raises(InventoryFullError):
        inventory_system.add_item_to_inventory(char, "new_item")

def test_item_not_found_exception():
    """Test that ItemNotFoundError is raised for missing items"""
    char = {'inventory': [], 'gold': 100}
    
    with pytest.raises(ItemNotFoundError):
        inventory_system.remove_item_from_inventory(char, "missing_item")

def test_insufficient_resources_exception():
    """Test that InsufficientResourcesError is raised when not enough gold"""
    char = {'inventory': [], 'gold': 10}
    item_data = {'cost': 100}
    
    with pytest.raises(InsufficientResourcesError):
        inventory_system.purchase_item(char, "expensive_item", item_data)

def test_invalid_item_type_exception():
    """Test that InvalidItemTypeError is raised for wrong item types"""
    char = {'inventory': ['weapon1'], 'health': 80, 'max_health': 100}
    item_data = {'type': 'weapon', 'effect': 'strength:5'}
    
    # Trying to "use" a weapon should raise exception
    with pytest.raises(InvalidItemTypeError):
        inventory_system.use_item(char, "weapon1", item_data)

# ============================================================================
# QUEST HANDLER EXCEPTION TESTS
# ============================================================================

def test_quest_not_found_exception():
    """Test that QuestNotFoundError is raised for invalid quests"""
    char = {'level': 5, 'active_quests': [], 'completed_quests': []}
    quests = {}
    
    with pytest.raises(QuestNotFoundError):
        quest_handler.accept_quest(char, "fake_quest", quests)

def test_insufficient_level_exception():
    """Test that InsufficientLevelError is raised for level requirements"""
    char = {'level': 1, 'active_quests': [], 'completed_quests': []}
    quests = {
        'hard_quest': {
            'quest_id': 'hard_quest',
            'required_level': 10,
            'prerequisite': 'NONE'
        }
    }
    
    with pytest.raises(InsufficientLevelError):
        quest_handler.accept_quest(char, "hard_quest", quests)

def test_quest_requirements_not_met_exception():
    """Test that QuestRequirementsNotMetError is raised for prerequisites"""
    char = {'level': 10, 'active_quests': [], 'completed_quests': []}
    quests = {
        'second_quest': {
            'quest_id': 'second_quest',
            'required_level': 1,
            'prerequisite': 'first_quest'
        }
    }
    
    with pytest.raises(QuestRequirementsNotMetError):
        quest_handler.accept_quest(char, "second_quest", quests)

def test_quest_already_completed_exception():
    """Test that QuestAlreadyCompletedError is raised for completed quests"""
    char = {'level': 5, 'active_quests': [], 'completed_quests': ['done_quest']}
    quests = {
        'done_quest': {
            'quest_id': 'done_quest',
            'required_level': 1,
            'prerequisite': 'NONE'
        }
    }
    
    with pytest.raises(QuestAlreadyCompletedError):
        quest_handler.accept_quest(char, "done_quest", quests)

def test_quest_not_active_exception():
    """Test that QuestNotActiveError is raised when completing inactive quest"""
    char = {'level': 5, 'active_quests': [], 'completed_quests': []}
    quests = {
        'test_quest': {
            'quest_id': 'test_quest',
            'required_level': 1
        }
    }
    
    with pytest.raises(QuestNotActiveError):
        quest_handler.complete_quest(char, "test_quest", quests)

# ============================================================================
# GAME DATA EXCEPTION TESTS
# ============================================================================

def test_missing_data_file_exception():
    """Test that MissingDataFileError is raised for missing files"""
    with pytest.raises(MissingDataFileError):
        game_data.load_quests("nonexistent_file.txt")

def test_invalid_data_format_exception():
    """Test that InvalidDataFormatError is raised for bad data"""
    # Create a temporary file with invalid format
    with open("test_bad_data.txt", "w") as f:
        f.write("This is not valid quest data")
    
    try:
        with pytest.raises(InvalidDataFormatError):
            game_data.load_quests("test_bad_data.txt")
    finally:
        os.remove("test_bad_data.txt")

# ============================================================================
# COMBAT EXCEPTION TESTS
# ============================================================================

def test_invalid_target_exception():
    """Test that InvalidTargetError is raised for invalid enemies"""
    import combat_system
    
    with pytest.raises(InvalidTargetError):
        combat_system.create_enemy("fake_enemy_type")

def test_combat_not_active_exception():
    """Test that CombatNotActiveError is raised outside of combat"""
    import combat_system
    
    char = {'name': 'Test', 'health': 100}
    enemy = {'name': 'Goblin', 'health': 50}
    
    battle = combat_system.SimpleBattle(char, enemy)
    battle.combat_active = False  # Manually set to inactive
    
    with pytest.raises(CombatNotActiveError):
        battle.player_turn()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

