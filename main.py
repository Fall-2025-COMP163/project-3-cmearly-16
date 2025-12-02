""""
COMP 163 - Project 3: Quest Chronicles
Main Game Module - Completed Implementation
Name: Christopher Early
AI Usage: AI assisted in writing menu logic and integration between modules.
"""

import character_manager
import inventory_system
import quest_handler
import combat_system
import game_data
from custom_exceptions import *

# ============================================================================
# GAME STATE
# ============================================================================

current_character = None
all_quests = {}
all_items = {}
game_running = False

# ============================================================================
# MAIN MENU
# ============================================================================

def main_menu():
    print("\n=== MAIN MENU ===")
    print("1. New Game")
    print("2. Load Game")
    print("3. Exit")
    choice = input("Choose an option (1-3): ")
    if choice in ("1", "2", "3"):
        return int(choice)
    else:
        print("Invalid choice. Please enter 1-3.")
        return main_menu()

def new_game():
    global current_character
    print("\n=== NEW GAME ===")
    name = input("Enter your character name: ").strip()
    print("Choose a class: Warrior, Mage, Rogue, Cleric")
    char_class = input("Class: ").strip()
    try:
        current_character = character_manager.create_character(name, char_class)
        print(f"\nCharacter '{name}' created successfully!")
        game_loop()
    except InvalidCharacterClassError:
        print("Invalid class. Please choose Warrior, Mage, Rogue, or Cleric.")
        new_game()

def load_game():
    global current_character
    print("\n=== LOAD GAME ===")
    saved_names = character_manager.list_saved_characters()
    if not saved_names:
        print("No saved characters available.")
        return
    for i, name in enumerate(saved_names):
        print(f"{i+1}. {name}")
    choice = input("Select a character number: ")
    if not choice.isdigit() or not (1 <= int(choice) <= len(saved_names)):
        print("Invalid selection.")
        return
    try:
        current_character = character_manager.load_character(saved_names[int(choice)-1])
        print(f"\nLoaded character '{current_character['name']}' successfully!")
        game_loop()
    except (CharacterNotFoundError, SaveFileCorruptedError) as e:
        print(f"Error loading character: {e}")

# ============================================================================
# GAME LOOP
# ============================================================================
def game_loop():
    global game_running
    game_running = True
    print("\n=== ENTERING GAME ===")
    while game_running:
        choice = game_menu()
        if choice == 1:
            view_character_stats()
        elif choice == 2:
            view_inventory()
        elif choice == 3:
            quest_menu()
        elif choice == 4:
            explore()
        elif choice == 5:
            shop()
        elif choice == 6:
            save_game()
            print("Game saved. Returning to main menu.")
            return

def game_menu():
    print("\n=== GAME MENU ===")
    print("1. View Character Stats")
    print("2. View Inventory")
    print("3. Quest Menu")
    print("4. Explore")
    print("5. Shop")
    print("6. Save and Quit")
    choice = input("Choose an option (1-6): ")
    if choice in ("1","2","3","4","5","6"):
        return int(choice)
    else:
        print("Invalid choice.")
        return game_menu()

# ============================================================================
# GAME ACTIONS
# ============================================================================
def view_character_stats():
    print("\n=== CHARACTER STATS ===")
    character_manager.display_character(current_character)
    quest_handler.display_quest_summary(current_character, all_quests)

def view_inventory():
    global current_character, all_items
    print("\n=== INVENTORY MENU ===")
    inventory_system.display_inventory(current_character, all_items)
    print("\n1. Use Item")
    print("2. Equip Weapon")
    print("3. Equip Armor")
    print("4. Drop Item")
    print("5. Back")
    choice = input("Choose: ")
    if choice == "1":
        item_id = input("Enter item ID to use: ")
        if item_id not in current_character["inventory"]:
            print("You don't have that item.")
            return
        try:
            print(inventory_system.use_item(current_character, item_id, all_items[item_id]))
        except Exception as e:
            print(f"Error: {e}")
    elif choice == "2":
        item_id = input("Weapon ID: ")
        try:
            print(inventory_system.equip_weapon(current_character, item_id, all_items[item_id]))
        except Exception as e:
            print(f"Error: {e}")
    elif choice == "3":
        item_id = input("Armor ID: ")
        try:
            print(inventory_system.equip_armor(current_character, item_id, all_items[item_id]))
        except Exception as e:
            print(f"Error: {e}")
    elif choice == "4":
        item_id = input("Enter item ID to drop: ")
        try:
            inventory_system.remove_item_from_inventory(current_character, item_id)
            print("Item dropped.")
        except ItemNotFoundError:
            print("You don't have that item.")

def quest_menu():
    print("\n=== QUEST MENU ===")
    print("1. View Active Quests")
    print("2. View Available Quests")
    print("3. View Completed Quests")
    print("4. Accept Quest")
    print("5. Abandon Quest")
    print("6. Complete Quest (testing)")
    print("7. Back")
    choice = input("Choose: ")
    if choice == "1":
        quest_handler.display_active_quests(current_character, all_quests)
    elif choice == "2":
        quest_handler.display_available_quests(current_character, all_quests)
    elif choice == "3":
        quest_handler.display_completed_quests(current_character, all_quests)
    elif choice == "4":
        quest_id = input("Enter quest ID to accept: ")
        try:
            quest_handler.accept_quest(current_character, quest_id, all_quests)
            print("Quest accepted.")
        except Exception as e:
            print(f"Error: {e}")
    elif choice == "5":
        quest_id = input("Enter quest ID to abandon: ")
        try:
            quest_handler.abandon_quest(current_character, quest_id)
            print("Quest abandoned.")
        except Exception as e:
            print(f"Error: {e}")
    elif choice == "6":
        quest_id = input("Enter quest ID to complete: ")
        try:
            quest_handler.complete_quest(current_character, quest_id, all_quests)
            print("Quest completed.")
        except Exception as e:
            print(f"Error: {e}")

def explore():
    print("\n=== EXPLORING... ===")
    enemy = combat_system.generate_enemy(current_character["level"])
    print(f"A wild {enemy['type']} appears!")
    try:
        battle = combat_system.SimpleBattle(current_character, enemy)
        result = battle.start_battle()
        print(result)
        if "defeat" in result.lower():
            handle_character_death()
            return
        character_manager.add_experience(current_character, enemy["xp"])
        current_character["gold"] += enemy["gold"]
        print(f"Gained {enemy['xp']} XP and {enemy['gold']} gold!")
    except Exception as e:
        print(f"Combat error: {e}")

def shop():
    global current_character, all_items
    print("\n=== SHOP ===")
    print(f"Gold: {current_character['gold']}")
    print("Items available:")
    for item_id, data in all_items.items():
        print(f"{item_id}: {data['name']} - {data['cost']} gold")
    print("\n1. Buy")
    print("2. Sell")
    print("3. Back")
    choice = input("Choose: ")
    if choice == "1":
        item_id = input("Item ID to buy: ")
        if item_id not in all_items:
            print("Invalid item ID.")
            return
        try:
            inventory_system.purchase_item(current_character, item_id, all_items[item_id])
            print("Purchase successful!")
        except Exception as e:
            print(f"Error: {e}")
    elif choice == "2":
        item_id = input("Item ID to sell: ")
        try:
            gold = inventory_system.sell_item(current_character, item_id, all_items[item_id])
            print(f"Sold for {gold} gold.")
        except Exception as e:
            print(f"Error: {e}")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def save_game():
    try:
        character_manager.save_character(current_character)
    except Exception as e:
        print(f"Error saving game: {e}")

def load_game_data():
    global all_quests, all_items
    try:
        all_quests = game_data.load_quests()
        all_items = game_data.load_items()
    except MissingDataFileError:
        print("Missing data files. Creating defaults.")
        game_data.create_default_data_files()
        all_quests = game_data.load_quests()
        all_items = game_data.load_items()
    except InvalidDataFormatError as e:
        print(f"Data error: {e}")

def handle_character_death():
    global game_running
    print("\n*** YOU HAVE FALLEN IN BATTLE ***")
    print("1. Revive (costs 20 gold)")
    print("2. Quit")
    choice = input("Choose: ")
    if choice == "1":
        try:
            character_manager.revive_character(current_character)
            print("Revived!")
        except InsufficientResourcesError:
            print("Not enough gold. Returning to menu.")
            game_running = False
    else:
        print("Returning to main menu.")
        game_running = False
def display_welcome():
    print("=" * 50)
    print("     QUEST CHRONICLES - A MODULAR RPG ADVENTURE")
    print("=" * 50)
    print("Welcome! Begin your journey.\n")

# ============================================================================
# MAIN EXECUTION
# ============================================================================
def main():
    display_welcome()
    try:
        load_game_data()
        print("Game data loaded successfully!")
    except Exception as e:
        print(f"Fatal error loading game: {e}")
        return
    while True:
        choice = main_menu()
        if choice == 1:
            new_game()
        elif choice == 2:
            load_game()
        elif choice == 3:
            print("\nThanks for playing Quest Chronicles!")
            break
if __name__ == "__main__":
    main()
