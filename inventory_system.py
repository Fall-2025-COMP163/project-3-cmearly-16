"""
COMP 163 - Project 3: Quest Chronicles
Inventory System Module - Completed Implementation
Name: Christopher Early
AI Usage: AI was used to ensure exceptions, data formats, and functions worked properly.
"""

from custom_exceptions import (
    InventoryFullError,
    ItemNotFoundError,
    InsufficientResourcesError,
    InvalidItemTypeError
)
MAX_INVENTORY_SIZE = 20

# ============================================================================
# INVENTORY MANAGEMENT
# ============================================================================
def add_item_to_inventory(character, item_id):
    if len(character["inventory"]) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full.")
    character["inventory"].append(item_id)
    return True

def remove_item_from_inventory(character, item_id):
    if item_id not in character["inventory"]:
        raise ItemNotFoundError(f"Item '{item_id}' not found in inventory.")
    character["inventory"].remove(item_id)
    return True

def has_item(character, item_id):
    return item_id in character["inventory"]

def count_item(character, item_id):
    return character["inventory"].count(item_id)

def get_inventory_space_remaining(character):
    return MAX_INVENTORY_SIZE - len(character["inventory"])

def clear_inventory(character):
    removed = list(character["inventory"])
    character["inventory"].clear()
    return removed

# ============================================================================
# ITEM USAGE
# ============================================================================
def use_item(character, item_id, item_data):
    if item_id not in character["inventory"]:
        raise ItemNotFoundError(f"Item '{item_id}' not in inventory.")
    if item_data["type"] != "consumable":
        raise InvalidItemTypeError("Only consumable items can be used.")
    stat, value = parse_item_effect(item_data["effect"])
    apply_stat_effect(character, stat, value)
    character["inventory"].remove(item_id)
    return f"{character['name']} used {item_data['name']}! {stat} increased by {value}."

def equip_weapon(character, item_id, item_data):
    if item_id not in character["inventory"]:
        raise ItemNotFoundError("Weapon not in inventory.")
    if item_data["type"] != "weapon":
        raise InvalidItemTypeError("Item is not a weapon.")
    if "equipped_weapon" in character and character["equipped_weapon"] is not None:
        old = character["equipped_weapon"]
        stat, val = parse_item_effect(character["equipped_weapon_effect"])
        apply_stat_effect(character, stat, -val)
        if len(character["inventory"]) >= MAX_INVENTORY_SIZE:
            raise InventoryFullError("Cannot unequip weapon; inventory full.")
        character["inventory"].append(old)
    stat, value = parse_item_effect(item_data["effect"])
    apply_stat_effect(character, stat, value)
    character["equipped_weapon"] = item_id
    character["equipped_weapon_effect"] = item_data["effect"]
    character["inventory"].remove(item_id)
    return f"{character['name']} equipped {item_data['name']} (+{value} {stat})."

def equip_armor(character, item_id, item_data):
    if item_id not in character["inventory"]:
        raise ItemNotFoundError("Armor not in inventory.")
    if item_data["type"] != "armor":
        raise InvalidItemTypeError("Item is not armor.")
    if "equipped_armor" in character and character["equipped_armor"] is not None:
        old = character["equipped_armor"]
        stat, val = parse_item_effect(character["equipped_armor_effect"])
        apply_stat_effect(character, stat, -val)
        if len(character["inventory"]) >= MAX_INVENTORY_SIZE:
            raise InventoryFullError("Cannot unequip armor; inventory full.")
        character["inventory"].append(old)
    stat, value = parse_item_effect(item_data["effect"])
    apply_stat_effect(character, stat, value)
    character["equipped_armor"] = item_id
    character["equipped_armor_effect"] = item_data["effect"]
    character["inventory"].remove(item_id)
    return f"{character['name']} equipped {item_data['name']} (+{value} {stat})."

def unequip_weapon(character):
    if "equipped_weapon" not in character or character["equipped_weapon"] is None:
        return None
    if len(character["inventory"]) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Not enough space to unequip weapon.")
    item_id = character["equipped_weapon"]
    stat, val = parse_item_effect(character["equipped_weapon_effect"])
    apply_stat_effect(character, stat, -val)
    character["inventory"].append(item_id)
    character["equipped_weapon"] = None
    character["equipped_weapon_effect"] = None
    return item_id

def unequip_armor(character):
    if "equipped_armor" not in character or character["equipped_armor"] is None:
        return None
    if len(character["inventory"]) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Not enough space to unequip armor.")
    item_id = character["equipped_armor"]
    stat, val = parse_item_effect(character["equipped_armor_effect"])
    apply_stat_effect(character, stat, -val)
    character["inventory"].append(item_id)
    character["equipped_armor"] = None
    character["equipped_armor_effect"] = None
    return item_id

# ============================================================================
# SHOP SYSTEM
# ============================================================================
def purchase_item(character, item_id, item_data):
    cost = item_data["cost"]
    if character["gold"] < cost:
        raise InsufficientResourcesError("Not enough gold.")
    if len(character["inventory"]) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full.")
    character["gold"] -= cost
    character["inventory"].append(item_id)
    return True

def sell_item(character, item_id, item_data):
    if item_id not in character["inventory"]:
        raise ItemNotFoundError("Cannot sell item you don't have.")
    sell_price = item_data["cost"] // 2
    character["inventory"].remove(item_id)
    character["gold"] += sell_price
    return sell_price

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def parse_item_effect(effect_string):
    if ":" not in effect_string:
        raise InvalidItemTypeError("Invalid effect format.")
    stat, value = effect_string.split(":")
    return stat.strip(), int(value)

def apply_stat_effect(character, stat_name, value):
    if stat_name not in ["health", "max_health", "strength", "magic"]:
        return
    character[stat_name] += value
    if stat_name == "health":
        if character["health"] > character["max_health"]:
            character["health"] = character["max_health"]

def display_inventory(character, item_data_dict):
    inv = character["inventory"]
    print("\n=== INVENTORY ===")
    if len(inv) == 0:
        print("Inventory is empty.")
        return
    counted = {}
    for item_id in inv:
        counted[item_id] = counted.get(item_id, 0) + 1
    for item_id, qty in counted.items():
        item = item_data_dict[item_id]
        print(f"{item['name']} (x{qty}) - {item['type']}")

