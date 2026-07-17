import random
import math
from gitquest_parser import parse_git_history

# Constants for dungeon elements
EMPTY = " "
WALL = "#"
PLAYER = "@"
BUG = "B"            # Basic Bug Enemy (from "fix" commits)
MERGE_CONFLICT = "M" # Hard Merge Conflict Enemy (from "merge" commits)
COMPILER_ERROR = "C" # Ranged Enemy
LINT_WARNING = "L"   # Fast / Annoying Enemy
MERGED_PORTAL = ">"  # Downward stairs/portal to next commit/level
PARENT_PORTAL = "<"  # Upward portal
LORE_TERMINAL = "T"  # Docs terminal (from docs / refactor)
LOOT_CHEST = "$"     # Feature / Pull Request (loot)
KEY = "k"            # SSH Key to open locked portals
LOCKED_PORTAL = "X"  # Locked git portal (requires SSH Key)

class GameCharacter:
    def __init__(self, name, hp, max_hp, attack, defense, color="\033[91m"):
        self.name = name
        self.hp = hp
        self.max_hp = max_hp
        self.attack = attack
        self.defense = defense
        self.color = color

class Enemy(GameCharacter):
    def __init__(self, name, hp, attack, defense, symbol, color, x, y, behavior="hostile"):
        super().__init__(name, hp, hp, attack, defense, color)
        self.symbol = symbol
        self.x = x
        self.y = y
        self.behavior = behavior # hostile, ranged, defensive

class Player(GameCharacter):
    def __init__(self, name="Dev"):
        super().__init__(name, 100, 100, 15, 5, "\033[92m")
        self.level = 1
        self.xp = 0
        self.xp_to_next = 50
        self.gold = 0 # "GitHub Stars"
        self.inventory = [] # list of dict items
        self.weapon = {"name": "Punch", "bonus": 0}
        self.armor = {"name": "Pyjamas", "bonus": 0}
        self.x = 0
        self.y = 0
        self.skills = {
            "Git Reset": {"desc": "Heal 25 HP (Cooldown: 10 turns)", "cooldown": 0, "max_cooldown": 10},
            "Force Push": {"desc": "Push an enemy back and deal 20 damage (Cooldown: 8 turns)", "cooldown": 0, "max_cooldown": 8},
            "Cherry Pick": {"desc": "Loot a room from afar / extra damage (Cooldown: 12 turns)", "cooldown": 0, "max_cooldown": 12},
        }

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def gain_xp(self, amount):
        self.xp += amount
        leveled_up = False
        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            self.max_hp += 15
            self.hp = self.max_hp
            self.attack += 3
            self.defense += 2
            self.xp_to_next = int(self.xp_to_next * 1.5)
            leveled_up = True
        return leveled_up

class DungeonRoom:
    def __init__(self, commit_info, width=15, height=9):
        self.commit = commit_info # Commit dict from parser
        self.width = width
        self.height = height
        self.grid = [[WALL for _ in range(width)] for _ in range(height)]
        self.enemies = []
        self.loot = {} # coordinate (x,y) -> item dict
        self.portals = {} # coordinate (x,y) -> target hash
        self.terminals = {} # coordinate (x,y) -> text list
        self.doors = {} # coordinate (x,y) -> state (locked / open)
        self.spawn_x = width // 2
        self.spawn_y = height // 2
        self._generate_layout()

    def _generate_layout(self):
        # Generate simple room layout with empty space inside
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                self.grid[y][x] = EMPTY

        # Place entry portal at (2, height // 2) if parents exist
        # and exit portal at (width - 3, height // 2)
        has_parents = len(self.commit["parents"]) > 0

        if has_parents:
            px, py = 2, self.height // 2
            self.grid[py][px] = PARENT_PORTAL
            self.portals[(px, py)] = self.commit["parents"][0] # Leads to parent commit room

        # Lead to next commits? In the game engine, we'll connect them.
        # But we can place a Merged Portal as exit at (width - 3, height // 2)
        ex, ey = self.width - 3, self.height // 2
        self.grid[ey][ex] = MERGED_PORTAL
        self.portals[(ex, ey)] = "next" # Handled dynamically by the gameplay manager

        # Add random columns/walls based on file names inside commit
        num_files = len(self.commit["modified_files"])
        random.seed(int(self.commit["hash"][:8], 16))

        # Create unique obstacles based on filenames length and counts
        for _ in range(min(5, num_files)):
            ox = random.randint(3, self.width - 4)
            oy = random.randint(2, self.height - 3)
            # Avoid blocking portals or center spawn
            if (ox, oy) not in self.portals and (ox, oy) != (self.spawn_x, self.spawn_y):
                self.grid[oy][ox] = WALL

        # Populate based on commit type
        ctype = self.commit["type"]
        if ctype == "fix":
            # Spawn Bugs!
            for _ in range(random.randint(1, 2)):
                ex, ey = self._get_free_pos()
                self.enemies.append(Enemy("Bug", 25, 8, 2, BUG, "\033[91m", ex, ey))
        elif ctype == "merge":
            # Hard Merge Conflict
            ex, ey = self._get_free_pos()
            self.enemies.append(Enemy("Merge Conflict", 50, 12, 6, MERGE_CONFLICT, "\033[31;1m", ex, ey))
        elif ctype == "feat":
            # Spawn nice loot chest
            lx, ly = self._get_free_pos()
            self.grid[ly][lx] = LOOT_CHEST
            self.loot[(lx, ly)] = {
                "name": "Feature Pull Request",
                "type": "weapon",
                "value": random.randint(3, 7),
                "gold": random.randint(10, 30)
            }
        elif ctype in ["docs", "refactor"]:
            # Spawn lore terminals
            tx, ty = self._get_free_pos()
            self.grid[ty][tx] = LORE_TERMINAL
            self.terminals[(tx, ty)] = [
                f"Author: {self.commit['author']}",
                f"Subject: {self.commit['subject']}",
                f"Modified: {', '.join(self.commit['modified_files'][:3]) or 'None'}"
            ]

        # General chance for standard enemies or items
        if random.random() < 0.4 and len(self.enemies) < 3:
            ex, ey = self._get_free_pos()
            if random.random() < 0.5:
                self.enemies.append(Enemy("Linter Warning", 15, 6, 1, LINT_WARNING, "\033[93m", ex, ey))
            else:
                self.enemies.append(Enemy("Compiler Error", 20, 10, 2, COMPILER_ERROR, "\033[95m", ex, ey, "ranged"))

        if random.random() < 0.3:
            lx, ly = self._get_free_pos()
            self.grid[ly][lx] = LOOT_CHEST
            self.loot[(lx, ly)] = {
                "name": "Code Refactoring",
                "type": "armor",
                "value": random.randint(1, 4),
                "gold": random.randint(5, 15)
            }

    def _get_free_pos(self):
        # Finds an empty, non-portal coordinate
        for _ in range(100):
            rx = random.randint(1, self.width - 2)
            ry = random.randint(1, self.height - 2)
            if self.grid[ry][rx] == EMPTY and (rx, ry) not in self.portals and (rx, ry) != (self.spawn_x, self.spawn_y):
                return rx, ry
        return self.spawn_x, self.spawn_y

class GameEngine:
    def __init__(self):
        self.commits = parse_git_history()
        # Fallback if empty
        if not self.commits:
            # Create a mock initial commit for empty repo play
            self.commits = [{
                "hash": "0000000000000000000000000000000000000000",
                "short_hash": "0000000",
                "parents": [],
                "author": "System Creator",
                "timestamp": 1700000000,
                "subject": "Initialize Virtual Git Space",
                "modified_files": ["README.md", "main.py"],
                "type": "feat"
            }]

        self.player = Player()
        self.rooms = {} # commit_hash -> DungeonRoom
        self.current_hash = self.commits[-1]["hash"] # Start at initial commit (oldest)

        # Build DAG mappings
        self.hash_to_commit = {c["hash"]: c for c in self.commits}
        self.children_map = {c["hash"]: [] for c in self.commits}
        for c in self.commits:
            for p in c["parents"]:
                if p in self.children_map:
                    self.children_map[p].append(c["hash"])

        # Create all rooms
        for c in self.commits:
            self.rooms[c["hash"]] = DungeonRoom(c)

        # Place player at spawn in first room
        room = self.rooms[self.current_hash]
        self.player.x = room.spawn_x
        self.player.y = room.spawn_y

    def get_current_room(self):
        return self.rooms[self.current_hash]

    def move_player(self, dx, dy):
        room = self.get_current_room()
        nx, ny = self.player.x + dx, self.player.y + dy

        # Check boundary
        if nx < 0 or nx >= room.width or ny < 0 or ny >= room.height:
            return "OOB"

        # Check wall
        if room.grid[ny][nx] == WALL:
            return "WALL"

        # Check enemy clash
        for enemy in room.enemies:
            if enemy.x == nx and enemy.y == ny:
                # Combat!
                return self.attack_enemy(enemy)

        # Move successful
        self.player.x = nx
        self.player.y = ny

        # Check trigger items
        cell = room.grid[ny][nx]
        if cell == LOOT_CHEST:
            item = room.loot.pop((nx, ny), None)
            room.grid[ny][nx] = EMPTY
            if item:
                self.player.gold += item["gold"]
                if item["type"] == "weapon":
                    if item["value"] > self.player.weapon["bonus"]:
                        self.player.weapon = {"name": item["name"], "bonus": item["value"]}
                        return f"LOOT_WEAPON:{item['name']}:+{item['value']}"
                elif item["type"] == "armor":
                    if item["value"] > self.player.armor["bonus"]:
                        self.player.armor = {"name": item["name"], "bonus": item["value"]}
                        return f"LOOT_ARMOR:{item['name']}:+{item['value']}"
                return f"LOOT_GOLD:{item['gold']}"

        elif cell == LORE_TERMINAL:
            info = room.terminals.get((nx, ny), [])
            return f"TERMINAL:{' | '.join(info)}"

        elif cell == PARENT_PORTAL:
            parent_hash = room.portals.get((nx, ny))
            if parent_hash and parent_hash in self.rooms:
                self.current_hash = parent_hash
                next_room = self.get_current_room()
                # Find corresponding exit portal
                for (px, py), target in next_room.portals.items():
                    if target == "next" or target in self.children_map:
                        self.player.x = px
                        self.player.y = py
                        break
                return "PORTAL_BACK"

        elif cell == MERGED_PORTAL:
            # Pick a child commit (if multiple, list or choose first/random)
            children = self.children_map.get(self.current_hash, [])
            if children:
                self.current_hash = children[0] # Move forward
                next_room = self.get_current_room()
                # Find corresponding parent portal
                for (px, py), target in next_room.portals.items():
                    if target == next_room.commit["parents"][0]:
                        self.player.x = px
                        self.player.y = py
                        break
                return "PORTAL_FORWARD"
            else:
                return "VICTORY_CANDIDATE" # reached HEAD of repo branch

        return "SUCCESS"

    def attack_enemy(self, enemy):
        # Calculate damage
        dmg = max(1, (self.player.attack + self.player.weapon["bonus"]) - enemy.defense)
        enemy.hp -= dmg
        log = f"You attack {enemy.name} for {dmg} dmg. ({enemy.hp}/{enemy.max_hp} HP)"

        if enemy.hp <= 0:
            self.get_current_room().enemies.remove(enemy)
            xp_gained = 15 + enemy.max_hp // 2
            leveled = self.player.gain_xp(xp_gained)
            log += f" Killed! +{xp_gained} XP."
            if leveled:
                log += " LEVEL UP!"
        else:
            # Counter attack
            edmg = max(1, enemy.attack - (self.player.defense + self.player.armor["bonus"]))
            self.player.hp -= edmg
            log += f" {enemy.name} counters for {edmg} dmg."
            if self.player.hp <= 0:
                log += " YOU DIED."

        return f"COMBAT:{log}"

    def update_enemies(self):
        room = self.get_current_room()
        logs = []
        for enemy in room.enemies:
            # Check distance to player
            dx = self.player.x - enemy.x
            dy = self.player.y - enemy.y
            dist = math.sqrt(dx*dx + dy*dy)

            if dist <= 1.5:
                # Attack player
                edmg = max(1, enemy.attack - (self.player.defense + self.player.armor["bonus"]))
                self.player.hp -= edmg
                logs.append(f"{enemy.name} attacks you for {edmg} dmg!")
                if self.player.hp <= 0:
                    logs.append("YOU DIED.")
            elif dist <= 4:
                # Move closer to player
                step_x = 0 if dx == 0 else int(dx / abs(dx))
                step_y = 0 if dy == 0 else int(dy / abs(dy))

                # Try step_x first
                nx, ny = enemy.x + step_x, enemy.y
                if room.grid[ny][nx] == EMPTY and not any(e.x == nx and e.y == ny for e in room.enemies) and (nx, ny) != (self.player.x, self.player.y):
                    enemy.x, enemy.y = nx, ny
                else:
                    # Try step_y
                    nx, ny = enemy.x, enemy.y + step_y
                    if room.grid[ny][nx] == EMPTY and not any(e.x == nx and e.y == ny for e in room.enemies) and (nx, ny) != (self.player.x, self.player.y):
                        enemy.x, enemy.y = nx, ny
        return logs

if __name__ == "__main__":
    print("Testing Game Engine...")
    engine = GameEngine()
    print(f"Loaded {len(engine.rooms)} rooms.")
    room = engine.get_current_room()
    print(f"Current room: {room.commit['short_hash']} | Type: {room.commit['type']}")
    print(f"Player spawn point: ({engine.player.x}, {engine.player.y})")
    print("Enemies in start room:")
    for e in room.enemies:
        print(f"- {e.name} at ({e.x}, {e.y})")
