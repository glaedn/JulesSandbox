"""
GitQuest Git School: Interactive Educational Tutorial Levels
Directly maps standard git commands (stash, commit --amend, checkout, conflicts)
to interactive gameplay mechanics to teach Git concepts visually.
"""

def generate_stash_tutorial():
    """
    Tutorial 1: Git Stash (Saving working directory changes)
    Concept: Saving your current uncommitted progress to a temporary stash stack.
    Gameplay: You start in a room with a deadly bug. If you fight and die, you'll lose.
    However, if you press 'S' to stash your state, the engine saves a snapshot of your player.
    When you die, the game automatically executes a 'git stash pop' to restore you to your stashed state!
    """
    return [
        {
            "hash": "stash0000000000000000000000000000000001",
            "short_hash": "stsh001",
            "parents": [],
            "branches": ["tutorial-stash"],
            "author": "Git Teacher",
            "timestamp": 1700000000,
            "subject": "Tutorial: Learn Git Stash by saving your game state before battle!",
            "modified_files": ["main.py"],
            "type": "docs"
        },
        {
            "hash": "stash0000000000000000000000000000000002",
            "short_hash": "stsh002",
            "parents": ["stash0000000000000000000000000000000001"],
            "branches": ["HEAD"],
            "author": "Git Teacher",
            "timestamp": 1701000000,
            "subject": "Press 'S' to SAVE a Stash snapshot, then engage the Bug 'B'!",
            "modified_files": ["main.py"],
            "type": "fix" # Spawns a bug
        }
    ]

def generate_amend_tutorial():
    """
    Tutorial 2: Git Commit --Amend (Rerolling the last commit/chest)
    Concept: Amending or correcting the most recent commit.
    Gameplay: You open a Loot Chest that yields mediocre loot. If you press 'C',
    you consume a 'git commit --amend' item from your inventory to REROLL that chest's reward,
    instantly transforming it into premium code with improved stats!
    """
    return [
        {
            "hash": "amend0000000000000000000000000000000001",
            "short_hash": "amnd001",
            "parents": [],
            "branches": ["tutorial-amend"],
            "author": "Git Teacher",
            "timestamp": 1710000000,
            "subject": "Tutorial: Open the chest first, then press 'C' to AMEND/Reroll the loot!",
            "modified_files": ["setup.py"],
            "type": "feat" # Spawns a chest
        }
    ]

def generate_checkout_tutorial():
    """
    Tutorial 3: Git Checkout (Switching branches/classes)
    Concept: Switching between parallel development branches.
    Gameplay: You face a special combat situation. You must use 'B' to checkout/switch
    between 'Frontend Dev' (high speed/damage, low health) and 'Backend Dev' (sturdy tank)
    to match the defense of the enemy!
    """
    return [
        {
            "hash": "checkout000000000000000000000000000001",
            "short_hash": "chkt001",
            "parents": [],
            "branches": ["tutorial-checkout"],
            "author": "Git Teacher",
            "timestamp": 1720000000,
            "subject": "Press 'B' to checkout different branches (Frontend vs Backend class)!",
            "modified_files": ["index.html", "database.sql"],
            "type": "docs"
        },
        {
            "hash": "checkout000000000000000000000000000002",
            "short_hash": "chkt002",
            "parents": ["checkout000000000000000000000000000001"],
            "branches": ["HEAD"],
            "author": "Git Teacher",
            "timestamp": 1721000000,
            "subject": "Switch classes based on the bugs you encounter!",
            "modified_files": ["main.js"],
            "type": "fix"
        }
    ]

def generate_merge_conflict_tutorial():
    """
    Tutorial 4: Resolving Merge Conflicts
    Concept: Combining two diverging histories into a single merge commit.
    Gameplay: The 'Merge Conflict Boss' is protected by an active shield.
    You must destroy either the 'HEAD Pillar' or the 'Incoming Pillar' first to
    resolve the conflict, strip the shield, and make the boss vulnerable to damage!
    """
    return [
        {
            "hash": "merge_tut00000000000000000000000000001",
            "short_hash": "mrg001",
            "parents": [],
            "branches": ["main"],
            "author": "Git Teacher",
            "timestamp": 1730000000,
            "subject": "Tutorial: Preparing to merge parallel histories",
            "modified_files": ["app.py"],
            "type": "feat"
        },
        {
            "hash": "merge_tut00000000000000000000000000002",
            "short_hash": "mrg002",
            "parents": ["merge_tut00000000000000000000000000001"],
            "branches": ["HEAD"],
            "author": "Git Teacher",
            "timestamp": 1731000000,
            "subject": "Merge: Attack a branch pillar (H/I) to resolve the merge conflict shield!",
            "modified_files": ["app.py"],
            "type": "merge"
        }
    ]

TUTORIALS = {
    "1": {
        "name": "Lesson 1: git stash (Save & Pop Session State)",
        "generator": generate_stash_tutorial
    },
    "2": {
        "name": "Lesson 2: git commit --amend (Reroll Chest Rewards)",
        "generator": generate_amend_tutorial
    },
    "3": {
        "name": "Lesson 3: git checkout (Branch Swapping Class Roles)",
        "generator": generate_checkout_tutorial
    },
    "4": {
        "name": "Lesson 4: Git Merging & Resolving Conflict Pillars",
        "generator": generate_merge_conflict_tutorial
    }
}

def load_tutorial(choice_id):
    """Loads a simulated Git DAG list for the chosen tutorial ID."""
    if choice_id in TUTORIALS:
        return TUTORIALS[choice_id]["generator"]()
    return generate_stash_tutorial()
