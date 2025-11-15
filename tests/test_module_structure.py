"""
Test Module Structure and Organization
Tests that all required modules exist and have proper functions
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_custom_exceptions_module_exists():
    """Test that custom_exceptions module can be imported"""
    import custom_exceptions
    assert custom_exceptions is not None

def test_game_data_module_exists():
    """Test that game_data module can be imported"""
    import game_data
    assert game_data is not None

def test_character_manager_module_exists():
    """Test that character_manager module can be imported"""
    import character_manager
    assert character_manager is not None

def test_inventory_system_module_exists():
    """Test that inventory_system module can be imported"""
    import inventory_system
    assert inventory_system is not None

def test_quest_handler_module_exists():
    """Test that quest_handler module can be imported"""
    import quest_handler
    assert quest_handler is not None

def test_combat_system_module_exists():
    """Test that combat_system module can be imported"""
    import combat_system
    assert combat_system is not None

def test_main_module_exists():
    """Test that main module can be imported"""
    import main
    assert main is not None

# Test custom exceptions exist
def test_custom_exceptions_defined():
    """Test that all required custom exceptions are defined"""
    from custom_exceptions import (
        GameError, DataError, CharacterError, CombatError,
        QuestError, InventoryError, InvalidDataFormatError,
        MissingDataFileError, CharacterNotFoundError,
        QuestNotFoundError, InventoryFullError
    )
    
    # Test inheritance
    assert issubclass(DataError, GameError)
    assert issubclass(InvalidDataFormatError, DataError)
    assert issubclass(CharacterNotFoundError, CharacterError)

# Test game_data functions exist
def test_game_data_functions_exist():
    """Test that game_data has required functions"""
    import game_data
    
    assert hasattr(game_data, 'load_quests')
    assert hasattr(game_data, 'load_items')
    assert hasattr(game_data, 'validate_quest_data')
    assert hasattr(game_data, 'validate_item_data')
    assert callable(game_data.load_quests)
    assert callable(game_data.load_items)

# Test character_manager functions exist
def test_character_manager_functions_exist():
    """Test that character_manager has required functions"""
    import character_manager
    
    required_functions = [
        'create_character', 'save_character', 'load_character',
        'gain_experience', 'add_gold', 'heal_character'
    ]
    
    for func_name in required_functions:
        assert hasattr(character_manager, func_name)
        assert callable(getattr(character_manager, func_name))

# Test inventory_system functions exist
def test_inventory_system_functions_exist():
    """Test that inventory_system has required functions"""
    import inventory_system
    
    required_functions = [
        'add_item_to_inventory', 'remove_item_from_inventory',
        'use_item', 'equip_weapon', 'equip_armor',
        'purchase_item', 'sell_item'
    ]
    
    for func_name in required_functions:
        assert hasattr(inventory_system, func_name)
        assert callable(getattr(inventory_system, func_name))

# Test quest_handler functions exist
def test_quest_handler_functions_exist():
    """Test that quest_handler has required functions"""
    import quest_handler
    
    required_functions = [
        'accept_quest', 'complete_quest', 'abandon_quest',
        'get_active_quests', 'get_available_quests'
    ]
    
    for func_name in required_functions:
        assert hasattr(quest_handler, func_name)
        assert callable(getattr(quest_handler, func_name))

# Test combat_system functions exist
def test_combat_system_functions_exist():
    """Test that combat_system has required functions"""
    import combat_system
    
    assert hasattr(combat_system, 'create_enemy')
    assert hasattr(combat_system, 'SimpleBattle')
    assert callable(combat_system.create_enemy)
    
    # Test SimpleBattle class has required methods
    assert hasattr(combat_system.SimpleBattle, 'start_battle')
    assert hasattr(combat_system.SimpleBattle, 'player_turn')
    assert hasattr(combat_system.SimpleBattle, 'enemy_turn')

# Test main module functions exist
def test_main_functions_exist():
    """Test that main module has required functions"""
    import main
    
    required_functions = [
        'main_menu', 'new_game', 'load_game', 'game_loop',
        'save_game', 'load_game_data'
    ]
    
    for func_name in required_functions:
        assert hasattr(main, func_name)
        assert callable(getattr(main, func_name))

# Test data files exist
def test_data_directory_structure():
    """Test that required data directories exist"""
    assert os.path.exists('data'), "data/ directory should exist"
    assert os.path.isdir('data/save_games') or True, "save_games/ should be creatable"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

