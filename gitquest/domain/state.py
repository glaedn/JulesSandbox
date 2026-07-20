import copy

class GameState:
    def __init__(self, name="Dev"):
        # Player attributes
        self.player_name = name
        self.role = "Backend Dev"
        self.hp = 120
        self.max_hp = 120
        self.attack = 12
        self.defense = 8
        self.level = 1
        self.xp = 0
        self.xp_to_next = 50
        self.gold = 0

        # Equipment & Inventory
        self.weapon = {"name": "Punch", "bonus": 0}
        self.armor = {"name": "Pyjamas", "bonus": 0}
        self.inventory = ["git stash", "git commit --amend"]

        # Skills
        self.skills = {
            "Git Reset": {"desc": "Heal 30 HP (Cooldown: 10 turns)", "cooldown": 0, "max_cooldown": 10},
            "Force Push": {"desc": "Push back and deal 20 damage (Cooldown: 8 turns)", "cooldown": 0, "max_cooldown": 8},
            "Cherry Pick": {"desc": "Snipe for 30 HP, absorb +2 Max HP (Cooldown: 12 turns)", "cooldown": 0, "max_cooldown": 12},
        }

        # Position & Environment
        self.current_hash = ""
        self.player_x = 0
        self.player_y = 0

        # Game progression flags & counters
        self.stash_snapshot = None # Stashed game state deep copy
        self.last_chest_loot = None
        self.unresolved_room_hashes = set()
        self.cleared_room_hashes = set()
        self.completed_quest_ids = set()
        self.technical_debt = 0 # Outstanding un-resolved quests/problems
        self.chronicle_entries = [] # Narrative events log

    def clone(self):
        """Creates a complete deepcopy of the GameState for Git Stash."""
        cloned = GameState(self.player_name)
        cloned.role = self.role
        cloned.hp = self.hp
        cloned.max_hp = self.max_hp
        cloned.attack = self.attack
        cloned.defense = self.defense
        cloned.level = self.level
        cloned.xp = self.xp
        cloned.xp_to_next = self.xp_to_next
        cloned.gold = self.gold

        cloned.weapon = copy.deepcopy(self.weapon)
        cloned.armor = copy.deepcopy(self.armor)
        cloned.inventory = list(self.inventory)
        cloned.skills = copy.deepcopy(self.skills)

        cloned.current_hash = self.current_hash
        cloned.player_x = self.player_x
        cloned.player_y = self.player_y

        cloned.last_chest_loot = copy.deepcopy(self.last_chest_loot)
        cloned.unresolved_room_hashes = set(self.unresolved_room_hashes)
        cloned.cleared_room_hashes = set(self.cleared_room_hashes)
        cloned.completed_quest_ids = set(self.completed_quest_ids)
        cloned.technical_debt = self.technical_debt
        cloned.chronicle_entries = list(self.chronicle_entries)
        return cloned

    def restore_from(self, snapshot):
        """Restores current state from a snapshot."""
        self.role = snapshot.role
        self.hp = snapshot.hp
        self.max_hp = snapshot.max_hp
        self.attack = snapshot.attack
        self.defense = snapshot.defense
        self.level = snapshot.level
        self.xp = snapshot.xp
        self.xp_to_next = snapshot.xp_to_next
        self.gold = snapshot.gold

        self.weapon = copy.deepcopy(snapshot.weapon)
        self.armor = copy.deepcopy(snapshot.armor)
        self.inventory = list(snapshot.inventory)
        self.skills = copy.deepcopy(snapshot.skills)

        self.current_hash = snapshot.current_hash
        self.player_x = snapshot.player_x
        self.player_y = snapshot.player_y

        self.last_chest_loot = copy.deepcopy(snapshot.last_chest_loot)
        self.unresolved_room_hashes = set(snapshot.unresolved_room_hashes)
        self.cleared_room_hashes = set(snapshot.cleared_room_hashes)
        self.completed_quest_ids = set(snapshot.completed_quest_ids)
        self.technical_debt = snapshot.technical_debt
        self.chronicle_entries = list(snapshot.chronicle_entries)
