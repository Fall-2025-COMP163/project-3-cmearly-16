"""
COMP 163 - Project 3: Quest Chronicles
Combat System Module - Starter Code
Name: Christopher Early
AI Usage: AI was used to assist with the combat loop and player turn, and helped keep the codes usability as I updated it.
Handles combat mechanics
"""

import random
from custom_exceptions import (
    InvalidTargetError,
    CombatNotActiveError,
    CharacterDeadError,
    AbilityOnCooldownError
)

# ============================================================================
# ENEMY DEFINITIONS
# ============================================================================
def create_enemy(enemy_type):

    """
    Create an enemy based on type

    Returns: Enemy dictionary
    Raises: InvalidTargetError if enemy_type not recognized
    """
    et = enemy_type.lower()
    if et == "goblin":
        return {
            "name": "Goblin",
            "health": 50,
            "max_health": 50,
            "strength": 8,
            "magic": 2,
            "xp_reward": 25,
            "gold_reward": 10
        }
    elif et == "orc":
        return {
            "name": "Orc",
            "health": 80,
            "max_health": 80,
            "strength": 12,
            "magic": 5,
            "xp_reward": 50,
            "gold_reward": 25
        }
    elif et == "dragon":
        return {
            "name": "Dragon",
            "health": 200,
            "max_health": 200,
            "strength": 25,
            "magic": 15,
            "xp_reward": 200,
            "gold_reward": 100
        }
    else:
        raise InvalidTargetError(f"Unknown enemy type: {enemy_type}")
def get_random_enemy_for_level(character_level):

    """
    Get an appropriate enemy for character's level
    Level 1-2: Goblins
    Level 3-5: Orcs
    Level 6+: Dragons
    """
    if character_level <= 2:
        return create_enemy("goblin")
    elif 3 <= character_level <= 5:
        return create_enemy("orc")
    else:
        return create_enemy("dragon")

# ============================================================================
# COMBAT SYSTEM
# ============================================================================
class SimpleBattle:

    """
    Simple turn-based combat system
    Manages combat between character and enemy
    Notes about usage:
    - By default the player does a basic attack every turn (no interactive input).
    - You can set `battle.next_player_action` before calling `start_battle()` to one of:
        "attack", "ability", "run"
      to force that action on the next player turn (useful for testing).
    """
    def __init__(self, character, enemy):
        """Initialize battle with character and enemy"""
        self.character = character
        self.enemy = enemy
        self.combat_active = True
        self.turn = 0
        # Initialize ability cooldown field if missing (0 means ready)
        if "ability_cooldown" not in self.character:
            self.character["ability_cooldown"] = 0
        # non-persistent per-battle flag to indicate if player escaped
        self.escaped = False
        # next_player_action can be set externally to "attack"/"ability"/"run"
        self.next_player_action = None
    def start_battle(self):

        """
        Start the combat loop
        Returns: Dictionary with battle results:
                {'winner': 'player'|'enemy'|'escaped', 'xp_gained': int, 'gold_gained': int}
        Raises: CharacterDeadError if character is already dead
        """
        if self.character["health"] <= 0:
            raise CharacterDeadError("Character is already dead and cannot fight.")
        display_battle_log(f"Battle start! {self.character['name']} vs {self.enemy['name']}")
        # Main loop
        while self.combat_active:
            self.turn += 1
            display_battle_log(f"Turn {self.turn} begins.")
            # Player turn
            self.player_turn()
            # After player action check end
            result = self.check_battle_end()
            if result is not None:
                break
            # Enemy turn
            self.enemy_turn()
            result = self.check_battle_end()
            if result is not None:
                break
            # Cooldown decrement at end of round
            if self.character.get("ability_cooldown", 0) > 0:
                self.character["ability_cooldown"] -= 1
        # Determine result and rewards
        if self.escaped:
            self.combat_active = False
            display_battle_log("Player escaped the battle.")
            return {"winner": "escaped", "xp_gained": 0, "gold_gained": 0}
        winner = self.check_battle_end()
        if winner == "player":
            rewards = get_victory_rewards(self.enemy)
            display_battle_log(f"{self.character['name']} defeated {self.enemy['name']}!")
            # Award rewards to character
            # Character dict is expected to have 'experience' and 'gold' keys
            self.character["experience"] = self.character.get("experience", 0) + rewards["xp"]
            self.character["gold"] = self.character.get("gold", 0) + rewards["gold"]
            self.combat_active = False
            return {"winner": "player", "xp_gained": rewards["xp"], "gold_gained": rewards["gold"]}
        elif winner == "enemy":
            display_battle_log(f"{self.character['name']} was defeated by {self.enemy['name']}...")
            self.combat_active = False
            return {"winner": "enemy", "xp_gained": 0, "gold_gained": 0}
        else:
            # Should not usually reach here, but handle gracefully
            self.combat_active = False
            return {"winner": "none", "xp_gained": 0, "gold_gained": 0}
    def player_turn(self):

        """
        Handle player's turn
        Options: "attack", "ability", "run"
        Raises: CombatNotActiveError if called outside of battle
        """
        if not self.combat_active:
            raise CombatNotActiveError("Cannot take player turn when combat is not active.")
        # Choose action
        action = None
        if self.next_player_action is not None:
            action = self.next_player_action
            # reset once used (caller can set again)
            self.next_player_action = None
        else:
            # Default non-interactive behavior: basic attack
            action = "attack"
        if action == "attack":
            damage = self.calculate_damage(self.character, self.enemy)
            self.apply_damage(self.enemy, damage)
            display_battle_log(f"{self.character['name']} hits {self.enemy['name']} for {damage} damage.")
            display_combat_stats(self.character, self.enemy)
        elif action == "ability":
            # Attempt special ability
            try:
                desc = use_special_ability(self.character, self.enemy)
                display_battle_log(desc)
                display_combat_stats(self.character, self.enemy)
            except AbilityOnCooldownError as e:
                display_battle_log(str(e))
                # fallback to basic attack when ability on cooldown
                damage = self.calculate_damage(self.character, self.enemy)
                self.apply_damage(self.enemy, damage)
                display_battle_log(f"{self.character['name']} uses a basic attack instead for {damage} damage.")
                display_combat_stats(self.character, self.enemy)
        elif action == "run":
            escaped = self.attempt_escape()
            if escaped:
                self.escaped = True
                self.combat_active = False
                display_battle_log(f"{self.character['name']} successfully escaped!")
                return
            else:
                display_battle_log(f"{self.character['name']} failed to escape!")
        else:
            # Unknown action -> default to attack
            damage = self.calculate_damage(self.character, self.enemy)
            self.apply_damage(self.enemy, damage)
            display_battle_log(f"{self.character['name']} (confused) attacks for {damage} damage.")
            display_combat_stats(self.character, self.enemy)
    def enemy_turn(self):

        """
        Handle enemy's turn - simple AI (always attacks)
        Raises: CombatNotActiveError if called outside of battle
        """
        if not self.combat_active:
            raise CombatNotActiveError("Cannot take enemy turn when combat is not active.")
        damage = self.calculate_damage(self.enemy, self.character)
        self.apply_damage(self.character, damage)
        display_battle_log(f"{self.enemy['name']} attacks {self.character['name']} for {damage} damage.")
        display_combat_stats(self.character, self.enemy)
    def calculate_damage(self, attacker, defender):

        """
        Damage formula: attacker['strength'] - (defender['strength'] // 4)
        Minimum damage: 1
        """
        atk = int(attacker.get("strength", 0))
        def_str = int(defender.get("strength", 0))
        raw = atk - (def_str // 4)
        return max(1, raw)
    def apply_damage(self, target, damage):

        """
        Apply damage to a character or enemy
        """
        before = target.get("health", 0)
        target["health"] = max(0, before - int(damage))
    def check_battle_end(self):

        """
        Check if battle is over
        Returns: 'player' if enemy dead, 'enemy' if character dead, None if ongoing
        """
        if self.enemy.get("health", 0) <= 0:
            return "player"
        if self.character.get("health", 0) <= 0:
            return "enemy"
        return None
    def attempt_escape(self):

        """
        Try to escape from battle
        50% success chance
        """
        success = random.random() < 0.5
        if success:
            self.combat_active = False
        return success

# ============================================================================
# SPECIAL ABILITIES
# ============================================================================
def use_special_ability(character, enemy):

    """"
    Use character's class-specific special ability
    Returns: String describing what happened
    Raises: AbilityOnCooldownError if ability was used recently
    """
    # Ensure cooldown field exists
    if "ability_cooldown" not in character:
        character["ability_cooldown"] = 0
    if character.get("ability_cooldown", 0) > 0:
        raise AbilityOnCooldownError("Special ability is on cooldown.")
    cls = character.get("class", "").lower()
    if cls == "warrior":
        return warrior_power_strike(character, enemy)
    elif cls == "mage":
        return mage_fireball(character, enemy)
    elif cls == "rogue":
        return rogue_critical_strike(character, enemy)
    elif cls == "cleric":
        return cleric_heal(character)
    else:
        # Unknown class: fallback to simple attack
        damage = max(1, character.get("strength", 1) - (enemy.get("strength", 0) // 4))
        enemy["health"] = max(0, enemy.get("health", 0) - damage)
        # set small cooldown to avoid spamming fallback
        character["ability_cooldown"] = 1
        return f"{character.get('name')} performs a simple special attack for {damage} damage."
def warrior_power_strike(character, enemy):
    """Warrior special ability: Double strength damage"""
    damage = (character.get("strength", 0) * 2) - (enemy.get("strength", 0) // 4)
    damage = max(1, int(damage))
    enemy["health"] = max(0, enemy.get("health", 0) - damage)
    # Set cooldown to 2 turns
    character["ability_cooldown"] = 2
    return f"{character.get('name')} uses Power Strike and deals {damage} damage to {enemy.get('name')}."
def mage_fireball(character, enemy):
    """Mage special ability: Double magic damage"""
    damage = (character.get("magic", 0) * 2) - (enemy.get("strength", 0) // 4)
    damage = max(1, int(damage))
    enemy["health"] = max(0, enemy.get("health", 0) - damage)
    character["ability_cooldown"] = 2
    return f"{character.get('name')} casts Fireball and hits {enemy.get('name')} for {damage} damage."
def rogue_critical_strike(character, enemy):
    """Rogue special ability: 50% chance for triple strength damage"""
    chance = random.random()
    if chance < 0.5:
        damage = (character.get("strength", 0) * 3) - (enemy.get("strength", 0) // 4)
        damage = max(1, int(damage))
        enemy["health"] = max(0, enemy.get("health", 0) - damage)
        character["ability_cooldown"] = 2
        return f"{character.get('name')} lands a CRITICAL STRIKE for {damage} damage!"
    else:
        # Failed crit: normal damage
        damage = character.get("strength", 0) - (enemy.get("strength", 0) // 4)
        damage = max(1, int(damage))
        enemy["health"] = max(0, enemy.get("health", 0) - damage)
        character["ability_cooldown"] = 2
        return f"{character.get('name')} attempts a critical strike but hits normally for {damage} damage."
