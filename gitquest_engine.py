import random
import math
from gitquest_parser import parse_git_history

# Constants for dungeon elements
EMPTY = " "
WALL = "#"
PLAYER = "@"
BUG = "B"            # Basic Bug Enemy (from "fix" commits)
MERGE_CONFLICT = "M" # Hard Merge Conflict Boss (from "merge" commits)
HEAD_PILLAR = "H"    # HEAD branch pillar for boss shield
INCOMING_PILLAR = "I" # Incoming branch pillar for boss shield
COMPILER_ERROR = "C" # Ranged Enemy
LINT_WARNING = "L"   # Fast / Annoying Enemy
MERGED_PORTAL = ">"  # Downward stairs/portal to next commit/level
PARENT_PORTAL = "<"  # Upward portal
LORE_TERMINAL = "T"  # Docs terminal (from docs / refactor)
LOOT_CHEST = "$"     # Feature / Pull Request (loot)

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
        self.role = "Backend Dev" # Default role
        self.level = 1
        self.xp = 0
        self.xp_to_next = 50
        self.gold = 0 # "GitHub Stars"
        self.inventory = ["git stash", "git commit --amend"] # Starting items
        self.weapon = {"name": "Punch", "bonus": 0}
        self.armor = {"name": "Pyjamas", "bonus": 0}
        self.x = 0
        self.y = 0
        self.skills = {
            "Git Reset": {"desc": "Heal 30 HP (Cooldown: 10 turns)", "cooldown": 0, "max_cooldown": 10},
            "Force Push": {"desc": "Push an enemy back and deal 20 damage (Cooldown: 8 turns)", "cooldown": 0, "max_cooldown": 8},
            "Cherry Pick": {"desc": "Snipe an enemy for 30 HP and absorb 2 Max HP (Cooldown: 12 turns)", "cooldown": 0, "max_cooldown": 12},
        }
        # Stash save slot
        self.stash_data = None
        self.last_chest_loot = None

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def gain_xp(self, amount):
        self.xp += amount
        leveled_up = False
        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            if self.role == "Backend Dev":
                self.max_hp += 20
                self.attack += 2
                self.defense += 3
            else: # Frontend Dev
                self.max_hp += 12
                self.attack += 4
                self.defense += 1
            self.hp = self.max_hp
            self.xp_to_next = int(self.xp_to_next * 1.5)
            leveled_up = True
        return leveled_up

    def checkout_role(self, role_name):
        """Swaps active character classes."""
        if role_name == self.role:
            return False, "Already on this branch!"

        hp_ratio = self.hp / self.max_hp
        if role_name == "Frontend Dev":
            self.role = "Frontend Dev"
            self.max_hp = 80 + (self.level - 1) * 12
            self.attack = 22 + (self.level - 1) * 4
            self.defense = 3 + (self.level - 1) * 1
        elif role_name == "Backend Dev":
            self.role = "Backend Dev"
            self.max_hp = 120 + (self.level - 1) * 20
            self.attack = 12 + (self.level - 1) * 2
            self.defense = 8 + (self.level - 1) * 3
        else:
            return False, "Unknown branch!"

        self.hp = max(1, int(self.max_hp * hp_ratio))
        return True, f"Checked out to branch: {role_name}!"

class DungeonRoom:
    def __init__(self, commit_info, children_hashes=None, width=15, height=9):
        self.commit = commit_info # Commit dict from parser
        self.children_hashes = children_hashes or []
        self.width = width
        self.height = height
        self.grid = [[WALL for _ in range(width)] for _ in range(height)]
        self.enemies = []
        self.loot = {} # coordinate (x,y) -> item dict
        self.portals = {} # coordinate (x,y) -> target hash
        self.terminals = {} # coordinate (x,y) -> text list
        self.doors = {} # coordinate (x,y) -> state
        self.spawn_x = width // 2
        self.spawn_y = height // 2
        self._generate_layout()

    def _generate_layout(self):
        # Generate simple room layout with empty space inside
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                self.grid[y][x] = EMPTY

        # Place multiple parent portals on the left side
        parents = self.commit.get("parents", [])
        for i, parent_hash in enumerate(parents):
            if i < 3: # limit to max 3 vertical portals
                py = 2 + i * 2
                px = 2
                self.grid[py][px] = PARENT_PORTAL
                self.portals[(px, py)] = parent_hash

        # Place multiple children portals on the right side
        for i, child_hash in enumerate(self.children_hashes):
            if i < 3:
                cy = 2 + i * 2
                cx = self.width - 3
                self.grid[cy][cx] = MERGED_PORTAL
                self.portals[(cx, cy)] = child_hash

        # Fallback if no children exist (HEAD of branch)
        if not self.children_hashes:
            cy = self.height // 2
            cx = self.width - 3
            self.grid[cy][cx] = MERGED_PORTAL
            self.portals[(cx, cy)] = "HEAD" # Represents end-game merge option

        # Add random columns/walls based on file names inside commit
        num_files = len(self.commit.get("modified_files", []))
        random.seed(int(self.commit["hash"][:8], 16))

        for _ in range(min(5, num_files)):
            ox = random.randint(3, self.width - 4)
            oy = random.randint(2, self.height - 3)
            # Avoid blocking portals or center spawn
            if (ox, oy) not in self.portals and (ox, oy) != (self.spawn_x, self.spawn_y):
                self.grid[oy][ox] = WALL

        # Populate based on commit type
        ctype = self.commit.get("type", "chore")
        if ctype == "fix":
            for _ in range(random.randint(1, 2)):
                ex, ey = self._get_free_pos()
                self.enemies.append(Enemy("Bug", 25, 8, 2, BUG, "\033[91m", ex, ey))
        elif ctype == "merge":
            # Spawn the Merge Conflict Boss and its protective Pillars
            ex, ey = self._get_free_pos()
            self.enemies.append(Enemy("Merge Conflict Boss", 80, 16, 6, MERGE_CONFLICT, "\033[31;1m", ex, ey))

            # Spawn HEAD and Incoming Pillars nearby
            px1, py1 = self._get_free_pos()
            self.enemies.append(Enemy("HEAD Pillar", 10, 0, 1, HEAD_PILLAR, "\033[96m", px1, py1))

            px2, py2 = self._get_free_pos()
            self.enemies.append(Enemy("Incoming Pillar", 10, 0, 1, INCOMING_PILLAR, "\033[93m", px2, py2))

        elif ctype == "feat":
            lx, ly = self._get_free_pos()
            self.grid[ly][lx] = LOOT_CHEST
            self.loot[(lx, ly)] = {
                "name": "Feature Pull Request",
                "type": "weapon",
                "value": random.randint(4, 9),
                "gold": random.randint(15, 35)
            }
        elif ctype in ["docs", "refactor"]:
            tx, ty = self._get_free_pos()
            self.grid[ty][tx] = LORE_TERMINAL
            self.terminals[(tx, ty)] = [
                f"Author: {self.commit['author']}",
                f"Subject: {self.commit['subject']}",
                f"Modified: {', '.join(self.commit['modified_files'][:3]) or 'None'}"
            ]

        # General random spawns
        if random.random() < 0.4 and len(self.enemies) < 3 and ctype != "merge":
            ex, ey = self._get_free_pos()
            if random.random() < 0.5:
                self.enemies.append(Enemy("Linter Warning", 15, 6, 1, LINT_WARNING, "\033[93m", ex, ey))
            else:
                self.enemies.append(Enemy("Compiler Error", 20, 10, 2, COMPILER_ERROR, "\033[95m", ex, ey, "ranged"))

        if random.random() < 0.3 and ctype != "feat":
            lx, ly = self._get_free_pos()
            self.grid[ly][lx] = LOOT_CHEST
            self.loot[(lx, ly)] = {
                "name": "Code Refactoring",
                "type": "armor",
                "value": random.randint(2, 6),
                "gold": random.randint(10, 20)
            }

    def _get_free_pos(self):
        for _ in range(100):
            rx = random.randint(1, self.width - 2)
            ry = random.randint(1, self.height - 2)
            if self.grid[ry][rx] == EMPTY and (rx, ry) not in self.portals and (rx, ry) != (self.spawn_x, self.spawn_y):
                if not any(e.x == rx and e.y == ry for e in self.enemies):
                    return rx, ry
        return self.spawn_x, self.spawn_y

class GameEngine:
    def __init__(self):
        self.commits = parse_git_history()
        # Fallback if empty
        if not self.commits:
            self.commits = [{
                "hash": "0000000000000000000000000000000000000000",
                "short_hash": "0000000",
                "parents": [],
                "branches": ["main"],
                "author": "System Creator",
                "timestamp": 1700000000,
                "subject": "Initialize Virtual Git Space",
                "modified_files": ["README.md", "main.py"],
                "type": "feat"
            }]

        self.player = Player()
        self.rooms = {} # commit_hash -> DungeonRoom
        self.current_hash = self.commits[-1]["hash"] # Start at oldest commit

        # Build DAG mappings
        self.hash_to_commit = {c["hash"]: c for c in self.commits}
        self.children_map = {c["hash"]: [] for c in self.commits}
        for c in self.commits:
            for p in c["parents"]:
                if p in self.children_map:
                    self.children_map[p].append(c["hash"])

        # Create all rooms, passing calculated children hashes
        for c in self.commits:
            self.rooms[c["hash"]] = DungeonRoom(c, self.children_map[c["hash"]])

        # Place player at spawn in first room
        room = self.rooms[self.current_hash]
        self.player.x = room.spawn_x
        self.player.y = room.spawn_y

    def get_current_room(self):
        return self.rooms[self.current_hash]

    def stash_save(self):
        """Saves player state into a virtual git stash."""
        self.player.stash_data = {
            "hp": self.player.hp,
            "max_hp": self.player.max_hp,
            "level": self.player.level,
            "xp": self.player.xp,
            "xp_to_next": self.player.xp_to_next,
            "gold": self.player.gold,
            "role": self.player.role,
            "weapon": self.player.weapon.copy(),
            "armor": self.player.armor.copy(),
            "current_hash": self.current_hash,
            "x": self.player.x,
            "y": self.player.y,
            "inventory": list(self.player.inventory)
        }
        return "Stashed current working directory state!"

    def stash_pop(self):
        """Restores player state from stash on death."""
        if not self.player.stash_data:
            return False
        d = self.player.stash_data
        self.player.hp = d["hp"]
        self.player.max_hp = d["max_hp"]
        self.player.level = d["level"]
        self.player.xp = d["xp"]
        self.player.xp_to_next = d["xp_to_next"]
        self.player.gold = d["gold"]
        self.player.role = d["role"]
        self.player.weapon = d["weapon"]
        self.player.armor = d["armor"]
        self.current_hash = d["current_hash"]
        self.player.x = d["x"]
        self.player.y = d["y"]
        self.player.inventory = d["inventory"]
        self.player.stash_data = None # consume stash
        return True

    def amend_chest_loot(self):
        """Rerolls the last chest opened using git commit --amend."""
        if "git commit --amend" not in self.player.inventory:
            return "No '--amend' item in your stash/inventory!"
        if not self.player.last_chest_loot:
            return "No chest opened recently to amend!"

        # Remove the amend item
        self.player.inventory.remove("git commit --amend")

        prev = self.player.last_chest_loot
        # Undo previous loot bonuses
        if prev["type"] == "weapon" and self.player.weapon["name"] == prev["name"]:
            self.player.weapon = {"name": "Punch", "bonus": 0}
        elif prev["type"] == "armor" and self.player.armor["name"] == prev["name"]:
            self.player.armor = {"name": "Pyjamas", "bonus": 0}
        self.player.gold = max(0, self.player.gold - prev["gold"])

        # Keep same type of loot slot for the amend reroall
        new_type = prev["type"]
        new_val = random.randint(prev["value"] + 1, prev["value"] + 5) # Guaranteed better!
        new_gold = random.randint(15, 45)

        self.player.gold += new_gold
        if new_type == "weapon":
            new_name = "Amended Master Branch Pull Request"
            self.player.weapon = {"name": new_name, "bonus": new_val}
            desc = f"Weapon: {new_name} (+{new_val})"
        else:
            new_name = "Amended Clean Refactoring"
            self.player.armor = {"name": new_name, "bonus": new_val}
            desc = f"Armor: {new_name} (+{new_val})"

        self.player.last_chest_loot = {
            "name": new_name,
            "type": new_type,
            "value": new_val,
            "gold": new_gold
        }
        return f"Amended! Rerolled loot into: {desc} & {new_gold} Stars!"

    def move_player(self, dx, dy):
        room = self.get_current_room()
        nx, ny = self.player.x + dx, self.player.y + dy

        if nx < 0 or nx >= room.width or ny < 0 or ny >= room.height:
            return "OOB"

        if room.grid[ny][nx] == WALL:
            return "WALL"

        # Combat Clash
        for enemy in room.enemies:
            if enemy.x == nx and enemy.y == ny:
                return self.attack_enemy(enemy)

        self.player.x = nx
        self.player.y = ny

        cell = room.grid[ny][nx]
        if cell == LOOT_CHEST:
            item = room.loot.pop((nx, ny), None)
            room.grid[ny][nx] = EMPTY
            if item:
                self.player.gold += item["gold"]
                self.player.last_chest_loot = item
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
                old_hash = self.current_hash
                self.current_hash = parent_hash
                next_room = self.get_current_room()
                # Spawn player near corresponding merged portal
                found = False
                for (px, py), target in next_room.portals.items():
                    if target == old_hash:
                        self.player.x = px - 1 if px > 1 else px + 1
                        self.player.y = py
                        found = True
                        break
                if not found:
                    self.player.x = next_room.spawn_x
                    self.player.y = next_room.spawn_y
                return f"PORTAL_BACK"

        elif cell == MERGED_PORTAL:
            child_hash = room.portals.get((nx, ny))
            if child_hash == "HEAD":
                return "VICTORY_CANDIDATE"

            if child_hash and child_hash in self.rooms:
                old_hash = self.current_hash
                self.current_hash = child_hash
                next_room = self.get_current_room()
                # Spawn player near parent portal
                found = False
                for (px, py), target in next_room.portals.items():
                    if target == old_hash:
                        self.player.x = px + 1 if px < next_room.width - 2 else px - 1
                        self.player.y = py
                        found = True
                        break
                if not found:
                    self.player.x = next_room.spawn_x
                    self.player.y = next_room.spawn_y
                return f"PORTAL_FORWARD"

        return "SUCCESS"

    def attack_enemy(self, enemy):
        room = self.get_current_room()

        # Shield mechanism for Merge Conflict Boss
        if enemy.name == "Merge Conflict Boss":
            has_pillars = any(e.name in ["HEAD Pillar", "Incoming Pillar"] for e in room.enemies)
            if has_pillars:
                return "COMBAT:Your attack bounce off! The Merge Conflict Boss is shielded by HEAD and Incoming branch pillars! Destroy a pillar to resolve."

        # Calculate standard damage
        dmg = max(1, (self.player.attack + self.player.weapon["bonus"]) - enemy.defense)
        enemy.hp -= dmg
        log = f"You attack {enemy.name} for {dmg} dmg. ({enemy.hp}/{enemy.max_hp} HP)"

        if enemy.hp <= 0:
            room.enemies.remove(enemy)

            # Special interaction: Destroying a Merge Boss Pillar resolves both of them and breaks the shield
            if enemy.name in ["HEAD Pillar", "Incoming Pillar"]:
                # Remove both pillars
                room.enemies = [e for e in room.enemies if e.name not in ["HEAD Pillar", "Incoming Pillar"]]
                log += " Pillar destroyed! Merge Conflict resolved. The Boss's shield is shattered!"

            xp_gained = 15 + enemy.max_hp // 2
            leveled = self.player.gain_xp(xp_gained)
            log += f" Killed! +{xp_gained} XP."
            if leveled:
                log += " LEVEL UP!"
        else:
            # Counter attack
            if enemy.attack > 0:
                edmg = max(1, enemy.attack - (self.player.defense + self.player.armor["bonus"]))
                self.player.hp -= edmg
                log += f" {enemy.name} counters for {edmg} dmg."
                if self.player.hp <= 0:
                    # Check stash restore
                    if self.stash_pop():
                        log += " CRITICAL FAULT! Your session was restored using git stash pop!"
                    else:
                        log += " YOU DIED."

        return f"COMBAT:{log}"

    def update_enemies(self):
        room = self.get_current_room()
        logs = []
        for enemy in room.enemies:
            if enemy.attack == 0:
                continue # Pillars don't move or attack

            dx = self.player.x - enemy.x
            dy = self.player.y - enemy.y
            dist = math.sqrt(dx*dx + dy*dy)

            if dist <= 1.5:
                # Attack player
                edmg = max(1, enemy.attack - (self.player.defense + self.player.armor["bonus"]))
                self.player.hp -= edmg
                logs.append(f"{enemy.name} attacks you for {edmg} dmg!")
                if self.player.hp <= 0:
                    if self.stash_pop():
                        logs.append("CRITICAL FAULT! Session restored from git stash pop!")
                    else:
                        logs.append("YOU DIED.")
            elif dist <= 4:
                # Move closer to player
                step_x = 0 if dx == 0 else int(dx / abs(dx))
                step_y = 0 if dy == 0 else int(dy / abs(dy))

                nx, ny = enemy.x + step_x, enemy.y
                if room.grid[ny][nx] == EMPTY and not any(e.x == nx and e.y == ny for e in room.enemies) and (nx, ny) != (self.player.x, self.player.y):
                    enemy.x, enemy.y = nx, ny
                else:
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
