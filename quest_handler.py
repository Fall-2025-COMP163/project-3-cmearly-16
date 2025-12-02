"""
COMP 163 - Project 3: Quest Chronicles
Quest Handler Module - Full Implementation
Name: Christopher Early
AI Usage: AI assisted in writing menu logic.
"""

from custom_exceptions import (
    QuestNotFoundError,
    QuestRequirementsNotMetError,
    QuestAlreadyCompletedError,
    QuestNotActiveError,
    InsufficientLevelError
)

import character_manager  # Needed for XP and gold rewards
# ============================================================================
# QUEST MANAGEMENT
# ============================================================================

def accept_quest(character, quest_id, quest_data_dict):
    """Accept a new quest if requirements are met."""
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' does not exist.")
    quest = quest_data_dict[quest_id]
    # Level requirement
    if character["level"] < quest["required_level"]:
        raise InsufficientLevelError("Character level too low for this quest.")
    # Prerequisite requirement
    prereq = quest["prerequisite"]
    if prereq != "NONE" and prereq not in character["completed_quests"]:
        raise QuestRequirementsNotMetError(f"Must complete '{prereq}' first.")
    # Completed already?
    if quest_id in character["completed_quests"]:
        raise QuestAlreadyCompletedError("Quest already completed.")
    # Already active?
    if quest_id in character["active_quests"]:
        raise QuestRequirementsNotMetError("Quest already active.")
    character["active_quests"].append(quest_id)
    return True

def complete_quest(character, quest_id, quest_data_dict):
    """Complete a quest and grant rewards."""
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError("Quest not found.")
    if quest_id not in character["active_quests"]:
        raise QuestNotActiveError("Quest is not currently active.")
    quest = quest_data_dict[quest_id]
    # Remove from active and add to completed
    character["active_quests"].remove(quest_id)
    character["completed_quests"].append(quest_id)
    # Rewards
    xp = quest["reward_xp"]
    gold = quest["reward_gold"]
    character_manager.gain_experience(character, xp)
    character_manager.add_gold(character, gold)
    return {
        "xp": xp,
        "gold": gold,
        "quest_title": quest["title"]
    }

def abandon_quest(character, quest_id):
    """Abandon an active quest."""
    if quest_id not in character["active_quests"]:
        raise QuestNotActiveError("Quest not active; cannot abandon.")
    character["active_quests"].remove(quest_id)
    return True

def get_active_quests(character, quest_data_dict):
    """Return list of full quest dictionaries that are active."""
    return [quest_data_dict[qid] for qid in character["active_quests"]]

def get_completed_quests(character, quest_data_dict):
    """Return list of quest dictionaries that are completed."""
    return [quest_data_dict[qid] for qid in character["completed_quests"]]

def get_available_quests(character, quest_data_dict):
    """Return list of quests that can currently be accepted."""
    available = []
    for qid, quest in quest_data_dict.items():
        if can_accept_quest(character, qid, quest_data_dict):
            available.append(quest)
    return available

# ============================================================================
# QUEST TRACKING
# ============================================================================
def is_quest_completed(character, quest_id):
    return quest_id in character["completed_quests"]

def is_quest_active(character, quest_id):
    return quest_id in character["active_quests"]

def can_accept_quest(character, quest_id, quest_data_dict):
    """Return True/False (no exceptions)."""
    if quest_id not in quest_data_dict:
        return False
    quest = quest_data_dict[quest_id]
    # Completed
    if quest_id in character["completed_quests"]:
        return False
    # Active
    if quest_id in character["active_quests"]:
        return False
    # Level too low
    if character["level"] < quest["required_level"]:
        return False
    # Prerequisite not done
    prereq = quest["prerequisite"]
    if prereq != "NONE" and prereq not in character["completed_quests"]:
        return False
    return True

def get_quest_prerequisite_chain(quest_id, quest_data_dict):
    """Return ordered list of all prerequisite quests ending in quest_id."""
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' not found.")
    chain = []
    current = quest_id
    while True:
        quest = quest_data_dict[current]
        chain.insert(0, current)
        prereq = quest["prerequisite"]
        if prereq == "NONE":
            break
        if prereq not in quest_data_dict:
            raise QuestNotFoundError(f"Invalid prerequisite '{prereq}'.")
        current = prereq
    return chain

# ============================================================================
# QUEST STATISTICS
# ============================================================================
def get_quest_completion_percentage(character, quest_data_dict):
    total = len(quest_data_dict)
    completed = len(character["completed_quests"])
    if total == 0:
        return 0.0
    return (completed / total) * 100

def get_total_quest_rewards_earned(character, quest_data_dict):
    total_xp = 0
    total_gold = 0
    for qid in character["completed_quests"]:
        quest = quest_data_dict[qid]
        total_xp += quest["reward_xp"]
        total_gold += quest["reward_gold"]
    return {"total_xp": total_xp, "total_gold": total_gold}

def get_quests_by_level(quest_data_dict, min_level, max_level):
    return [
        quest
        for quest in quest_data_dict.values()
        if min_level <= quest["required_level"] <= max_level
    ]

# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================
def display_quest_info(quest_data):
    print(f"\n=== {quest_data['title']} ===")
    print(f"Description : {quest_data['description']}")
    print(f"Required Lv.: {quest_data['required_level']}")
    print(f"Prerequisite: {quest_data['prerequisite']}")
    print(f"Rewards     : {quest_data['reward_xp']} XP, {quest_data['reward_gold']} Gold\n")

def display_quest_list(quest_list):
    if not quest_list:
        print("No quests to display.\n")
        return
    for q in quest_list:
        print(f"- {q['title']} (Lvl {q['required_level']}) | Reward: {q['reward_xp']} XP, {q['reward_gold']} Gold")
    print()

def display_character_quest_progress(character, quest_data_dict):
    active = len(character["active_quests"])
    completed = len(character["completed_quests"])
    percent = get_quest_completion_percentage(character, quest_data_dict)
    rewards = get_total_quest_rewards_earned(character, quest_data_dict)
    print("\n=== QUEST PROGRESS ===")
    print(f"Active Quests       : {active}")
    print(f"Completed Quests    : {completed}")
    print(f"Completion Rate     : {percent:.2f}%")
    print(f"Total XP Earned     : {rewards['total_xp']}")
    print(f"Total Gold Earned   : {rewards['total_gold']}\n")

# ============================================================================
# VALIDATION
# ============================================================================
def validate_quest_prerequisites(quest_data_dict):
    for qid, quest in quest_data_dict.items():
        prereq = quest["prerequisite"]
        if prereq != "NONE" and prereq not in quest_data_dict:
            raise QuestNotFoundError(
                f"Quest '{qid}' has invalid prerequisite '{prereq}'."
            )
    return True
