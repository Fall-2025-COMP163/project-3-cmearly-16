"""
Test Game Integration
Tests that modules work together correctly
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import character_manager
import inventory_system
import quest_handler
import combat_system
import game_data

# ============================================================================
# CHARACTER INTEGRATION TESTS
# ============================================================================

def test_character_creation_and_saving():
    """Test creating and saving a character"""
    char = character_manager.create_character("IntegrationTest", "Warrior")
    
    assert char is not None
    assert char['name'] == "IntegrationTest"
    assert char['class'] == "Warrior"
    assert char['level'] == 1
    
    # Test saving
    result = character_manager.save_character(char)
    assert result == True
    
    # Test loading
    loaded = character_manager.load_character("IntegrationTest")
    assert loaded['name'] == char['name']
    assert loaded['class'] == char['class']
    
    # Cleanup
    character_manager.delete_character("IntegrationTest")

def test_character_leveling_system():
    """Test that character leveling works correctly"""
    char = character_manager.create_character("LevelTest", "Mage")
    
    original_level = char['level']
    original_health = char['max_health']
    
    # Gain enough XP to level up (100 XP for level 1)
    character_manager.gain_experience(char, 100)
    
    assert char['level'] == original_level + 1
    assert char['max_health'] > original_health
    assert char['health'] == char['max_health']  # Health restored on level up

def test_character_gold_management():
    """Test adding and spending gold"""
    char = character_manager.create_character("GoldTest", "Rogue")
    
    original_gold = char['gold']
    character_manager.add_gold(char, 50)
    assert char['gold'] == original_gold + 50
    
    character_manager.add_gold(char, -25)
    assert char['gold'] == original_gold + 25
    
    # Test insufficient gold
    with pytest.raises(ValueError):
        character_manager.add_gold(char, -1000)

# ============================================================================
# INVENTORY INTEGRATION TESTS
# ============================================================================

def test_inventory_item_management():
    """Test adding, using, and removing items"""
    char = character_manager.create_character("InventoryTest", "Cleric")
    
    # Add items
    inventory_system.add_item_to_inventory(char, "health_potion")
    assert "health_potion" in char['inventory']
    
    # Use consumable
    item_data = {'type': 'consumable', 'effect': 'health:20'}
    char['health'] = 50
    result = inventory_system.use_item(char, "health_potion", item_data)
    
    assert "health_potion" not in char['inventory']  # Consumed
    assert char['health'] == 70  # Healed

def test_equipment_system():
    """Test equipping weapons and armor"""
    char = character_manager.create_character("EquipTest", "Warrior")
    original_strength = char['strength']
    
    # Add and equip weapon
    inventory_system.add_item_to_inventory(char, "iron_sword")
    weapon_data = {'type': 'weapon', 'effect': 'strength:5'}
    
    inventory_system.equip_weapon(char, "iron_sword", weapon_data)
    
    assert char['strength'] == original_strength + 5
    assert 'equipped_weapon' in char
    assert char['equipped_weapon'] == "iron_sword"

def test_shop_system():
    """Test buying and selling items"""
    char = character_manager.create_character("ShopTest", "Mage")
    original_gold = char['gold']
    
    item_data = {'cost': 25, 'type': 'consumable'}
    
    # Purchase item
    inventory_system.purchase_item(char, "health_potion", item_data)
    
    assert char['gold'] == original_gold - 25
    assert "health_potion" in char['inventory']
    
    # Sell item
    gold_received = inventory_system.sell_item(char, "health_potion", item_data)
    
    assert gold_received == 12  # Half of cost (25 // 2)
    assert "health_potion" not in char['inventory']

# ============================================================================
# QUEST INTEGRATION TESTS
# ============================================================================

def test_quest_acceptance_and_completion():
    """Test accepting and completing quests"""
    char = character_manager.create_character("QuestTest", "Warrior")
    
    quests = {
        'test_quest': {
            'quest_id': 'test_quest',
            'title': 'Test Quest',
            'description': 'A test',
            'reward_xp': 50,
            'reward_gold': 25,
            'required_level': 1,
            'prerequisite': 'NONE'
        }
    }
    
    # Accept quest
    quest_handler.accept_quest(char, 'test_quest', quests)
    assert 'test_quest' in char['active_quests']
    
    # Complete quest
    original_xp = char['experience']
    original_gold = char['gold']
    
    result = quest_handler.complete_quest(char, 'test_quest', quests)
    
    assert 'test_quest' not in char['active_quests']
    assert 'test_quest' in char['completed_quests']
    assert char['experience'] == original_xp + 50
    assert char['gold'] == original_gold + 25

def test_quest_prerequisite_system():
    """Test that quest prerequisites work correctly"""
    char = character_manager.create_character("PrereqTest", "Rogue")
    
    quests = {
        'first_quest': {
            'quest_id': 'first_quest',
            'required_level': 1,
            'prerequisite': 'NONE'
        },
        'second_quest': {
            'quest_id': 'second_quest',
            'required_level': 1,
            'prerequisite': 'first_quest'
        }
    }
    
    # Can't accept second_quest without completing first_quest
    from custom_exceptions import QuestRequirementsNotMetError
    with pytest.raises(QuestRequirementsNotMetError):
        quest_handler.accept_quest(char, 'second_quest', quests)
    
    # Complete first_quest
    char['completed_quests'].append('first_quest')
    
    # Now can accept second_quest
    quest_handler.accept_quest(char, 'second_quest', quests)
    assert 'second_quest' in char['active_quests']

# ============================================================================
# COMBAT INTEGRATION TESTS
# ============================================================================

def test_combat_system_basic_battle():
    """Test basic combat functionality"""
    char = character_manager.create_character("CombatTest", "Warrior")
    enemy = combat_system.create_enemy("goblin")
    
    assert enemy['name'] == "Goblin"
    assert enemy['health'] > 0
    
    # Test battle creation
    battle = combat_system.SimpleBattle(char, enemy)
    assert battle.character == char
    assert battle.enemy == enemy

def test_combat_victory_rewards():
    """Test that winning combat grants rewards"""
    char = character_manager.create_character("RewardTest", "Mage")
    original_xp = char['experience']
    original_gold = char['gold']
    
    enemy = combat_system.create_enemy("goblin")
    expected_xp = enemy['xp_reward']
    expected_gold = enemy['gold_reward']
    
    # Kill the enemy (simulate victory)
    enemy['health'] = 0
    
    rewards = combat_system.get_victory_rewards(enemy)
    
    assert rewards['xp'] == expected_xp
    assert rewards['gold'] == expected_gold

# ============================================================================
# DATA LOADING INTEGRATION TESTS
# ============================================================================

def test_load_game_data():
    """Test that game data loads correctly"""
    quests = game_data.load_quests("data/quests.txt")
    items = game_data.load_items("data/items.txt")
    
    assert len(quests) > 0
    assert len(items) > 0
    
    # Test quest data structure
    for quest_id, quest in quests.items():
        assert 'quest_id' in quest
        assert 'title' in quest
        assert 'reward_xp' in quest
        assert 'reward_gold' in quest
        assert 'required_level' in quest
    
    # Test item data structure
    for item_id, item in items.items():
        assert 'item_id' in item
        assert 'name' in item
        assert 'type' in item
        assert 'cost' in item

def test_data_validation():
    """Test that data validation works"""
    valid_quest = {
        'quest_id': 'test',
        'title': 'Test',
        'description': 'Test',
        'reward_xp': 50,
        'reward_gold': 25,
        'required_level': 1,
        'prerequisite': 'NONE'
    }
    
    assert game_data.validate_quest_data(valid_quest) == True
    
    valid_item = {
        'item_id': 'test',
        'name': 'Test',
        'type': 'consumable',
        'effect': 'health:20',
        'cost': 25,
        'description': 'Test'
    }
    
    assert game_data.validate_item_data(valid_item) == True

# ============================================================================
# FULL GAME WORKFLOW TEST
# ============================================================================

def test_complete_game_workflow():
    """Test a complete game workflow from start to victory"""
    # Create character
    char = character_manager.create_character("WorkflowTest", "Warrior")
    
    # Load game data
    quests = game_data.load_quests("data/quests.txt")
    items = game_data.load_items("data/items.txt")
    
    # Accept a quest
    quest_handler.accept_quest(char, 'first_steps', quests)
    
    # Fight an enemy
    enemy = combat_system.create_enemy("goblin")
    battle = combat_system.SimpleBattle(char, enemy)
    
    # Simulate victory (just kill enemy for testing)
    enemy['health'] = 0
    rewards = combat_system.get_victory_rewards(enemy)
    
    # Grant rewards
    character_manager.gain_experience(char, rewards['xp'])
    character_manager.add_gold(char, rewards['gold'])
    
    # Complete quest
    quest_handler.complete_quest(char, 'first_steps', quests)
    
    # Buy an item
    inventory_system.purchase_item(char, 'health_potion', items['health_potion'])
    
    # Save character
    character_manager.save_character(char)
    
    # Verify workflow
    assert char['level'] >= 1
    assert len(char['completed_quests']) == 1
    assert len(char['inventory']) >= 1
    assert char['gold'] >= 0
    
    # Cleanup
    character_manager.delete_character("WorkflowTest")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

