import sys
import tty
import termios
import time
from gitquest_engine import (
    GameEngine, EMPTY, WALL, PLAYER, BUG, MERGE_CONFLICT,
    HEAD_PILLAR, INCOMING_PILLAR, COMPILER_ERROR, LINT_WARNING,
    MERGED_PORTAL, PARENT_PORTAL, LORE_TERMINAL, LOOT_CHEST
)
from gitquest.domain.events import EventBus, DamageApplied, EnemyDefeated, QuestCompleted
from gitquest.domain.state import GameState
from gitquest.adapters.git_cli import GitCLIAdapter
from gitquest.adapters.diagnostics import DiagnosticsAdapter
from gitquest.adapters.test_runner import TestRunnerAdapter
from gitquest.analysis.quest_compiler import QuestCompiler
from gitquest.ui.graph import DAGVisualizer
from gitquest.reports.chronicle import ChronicleReporter

def clear_screen():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()

def draw_text(text, color_code):
    return f"{color_code}{text}\033[0m"

# Map game entity characters to styles
COLOR_MAP = {
    WALL: "\033[37m#",
    EMPTY: " ",
    PLAYER: "\033[92m@",
    BUG: "\033[91mB",
    MERGE_CONFLICT: "\033[31;1mM",
    HEAD_PILLAR: "\033[96mH",
    INCOMING_PILLAR: "\033[93mI",
    COMPILER_ERROR: "\033[95mC",
    LINT_WARNING: "\033[93mL",
    MERGED_PORTAL: "\033[96m>",
    PARENT_PORTAL: "\033[94m<",
    LORE_TERMINAL: "\033[36mT",
    LOOT_CHEST: "\033[33m$",
}

def get_char_at(room, x, y, player):
    if player.x == x and player.y == y:
        return draw_text("@", "\033[92;1m")
    for enemy in room.enemies:
        if enemy.x == x and enemy.y == y:
            return draw_text(enemy.symbol, enemy.color)
    cell = room.grid[y][x]
    if cell in COLOR_MAP:
        return COLOR_MAP[cell]
    return cell

class TerminalGame:
    def __init__(self, campaign_choice="1"):
        # Initialize Adapters & State
        self.git_cli = GitCLIAdapter()
        self.diagnostics = DiagnosticsAdapter()
        self.test_runner = TestRunnerAdapter()
        self.quest_compiler = QuestCompiler()

        # Build state
        self.state = GameState()
        self.chronicle = ChronicleReporter(self.state)
        self.event_bus = EventBus()

        # Subscribe event listeners
        self.event_bus.subscribe(DamageApplied, self._on_damage_applied)
        self.event_bus.subscribe(EnemyDefeated, self._on_enemy_defeated)
        self.event_bus.subscribe(QuestCompleted, self._on_quest_completed)

        # Load engine
        self.engine = GameEngine()
        self.state.current_hash = self.engine.current_hash
        self.state.player_x = self.engine.player.x
        self.state.player_y = self.engine.player.y

        # Compile active quests
        self.quests = self.quest_compiler.compile_quests(self.git_cli, self.diagnostics, self.test_runner)
        self.active_quest = self.quests[0] if self.quests else None

        # Visualization
        self.visualizer = DAGVisualizer(self.engine.commits)

        self.campaign_choice = campaign_choice
        self.status_message = "GitQuest Active campaign initialized."
        self.log_messages = []
        self.game_over = False
        self.won = False

        campaign_names = {
            "1": "Archive Expedition (Explore Ruins)",
            "2": "Active Campaign (Codebase Quests)",
            "3": "Release Raid (Deployment Prep)"
        }
        self.add_log(f"Started campaign: {campaign_names.get(campaign_choice, 'Default')}")
        self.chronicle.add_event(f"Initialized GitQuest campaign: {campaign_names.get(campaign_choice, 'Default')}")

    def _on_damage_applied(self, ev):
        self.chronicle.add_event(f"{ev.attacker_name} hit {ev.target_name} for {ev.damage} dmg. (Remaining: {ev.remaining_hp} HP)")

    def _on_enemy_defeated(self, ev):
        self.chronicle.add_event(f"Defeated {ev.enemy_name}! Earned +{ev.xp_gained} XP.")

    def _on_quest_completed(self, ev):
        self.chronicle.add_event(f"★ QUEST COMPLETED ★: {ev.title} (ID: {ev.quest_id})")

    def add_log(self, msg):
        self.log_messages.append(msg)
        if len(self.log_messages) > 6:
            self.log_messages.pop(0)

    def draw(self):
        room = self.engine.get_current_room()
        player = self.engine.player

        # Keep GameState synchronized for visualization / stashing
        self.state.hp = player.hp
        self.state.max_hp = player.max_hp
        self.state.level = player.level
        self.state.xp = player.xp
        self.state.xp_to_next = player.xp_to_next
        self.state.gold = player.gold
        self.state.role = player.role
        self.state.weapon = player.weapon
        self.state.armor = player.armor
        self.state.inventory = player.inventory
        self.state.current_hash = self.engine.current_hash
        self.state.player_x = player.x
        self.state.player_y = player.y

        # Render left-side map grid
        grid_lines = []
        for y in range(room.height):
            chars = []
            for x in range(room.width):
                chars.append(get_char_at(room, x, y, player))
            grid_lines.append("".join(chars))

        # Compile side-by-side HUD dashboard
        dash_lines = [
            f"\033[1;35mOn branch {self.state.role}\033[0m",
            f"HP: \033[92m{self.state.hp}/{self.state.max_hp}\033[0m | Level: {self.state.level} ({self.state.xp}/{self.state.xp_to_next} XP)",
            f"Stars: \033[93m{self.state.gold} ★\033[0m | Inventory: {', '.join(self.state.inventory) or 'None'}",
            "",
            "\033[1;34m--- Active Quest ---\033[0m",
        ]

        if self.active_quest:
            status_color = "\033[92m" if self.active_quest.status == "Completed" else "\033[93m"
            dash_lines.append(f"Title: {self.active_quest.title} {status_color}[{self.active_quest.status}]\033[0m")
            dash_lines.append(f"Objective: {self.active_quest.objective[:45]}")
        else:
            dash_lines.append("No active quests loaded.")
            dash_lines.append("")

        dash_lines.append("")
        dash_lines.append("\033[1;34m--- Local Git DAG Graph ---\033[0m")
        dash_lines.extend(self.visualizer.render_ascii_graph(self.state.current_hash, limit=5))

        # Ensure HUD list matches map height
        while len(dash_lines) < room.height:
            dash_lines.append("")

        # Draw header
        header_lines = [
            "\033[1;36m=== GitQuest: The Playable Repository Cockpit ===\033[0m",
            f"Commit: \033[93m{room.commit['short_hash']}\033[0m | Author: {room.commit['author']} | Type: \033[95m{room.commit.get('type', 'chore').upper()}\033[0m",
            "-" * 85
        ]

        combined_body = []
        for y in range(room.height):
            combined_body.append(f"{grid_lines[y]}   |   {dash_lines[y]}")

        # Footer
        footer_lines = [
            "-" * 85,
            "\033[1;35m--- Skills ---\033[0m"
        ]
        skills_str = []
        for name, data in player.skills.items():
            cd = data["cooldown"]
            cd_str = f"{name}: \033[91m{cd}t\033[0m" if cd > 0 else f"{name}: \033[92mREADY\033[0m"
            skills_str.append(cd_str)
        footer_lines.append(" | ".join(skills_str))

        footer_lines.append("\033[1;33m--- Git Logs & Output ---\033[0m")
        for log in self.log_messages:
            footer_lines.append(f"  {log}")

        while len(footer_lines) < 14:
            footer_lines.append("")

        footer_lines.append("\033[1;37mControls:\033[0m")
        footer_lines.append("  \033[92mw/a/s/d\033[0m: Move / Attack | \033[93m1,2,3\033[0m: Git Skills")
        footer_lines.append("  \033[96mS\033[0m: git stash state | \033[96mC\033[0m: git commit --amend (Reroll chest) | \033[96mB\033[0m: git checkout (Swap class)")
        footer_lines.append("  \033[95mQ\033[0m: Quit")

        clear_screen()
        sys.stdout.write("\n".join(header_lines + combined_body + footer_lines) + "\n")
        sys.stdout.flush()

    def check_active_quest_validation(self):
        """Re-scans real workspace using adapters to check active quest completion evidence."""
        if not self.active_quest or self.active_quest.status == "Completed":
            return

        completed = self.quest_compiler.verify_quest_completion(
            self.active_quest, self.git_cli, self.diagnostics, self.test_runner
        )
        if completed:
            self.active_quest.status = "Completed"
            self.state.completed_quest_ids.add(self.active_quest.id)

            # Publish event
            self.event_bus.publish(QuestCompleted(self.active_quest.id, self.active_quest.title))

            # Award rewards
            self.engine.player.gain_xp(self.active_quest.reward_xp)
            self.engine.player.gold += self.active_quest.reward_gold

            self.add_log(f"★ Quest Verified! Complete! +{self.active_quest.reward_xp} XP, +{self.active_quest.reward_gold} Stars!")
            self.chronicle.add_event(f"Verified quest proof: {self.active_quest.title}")

    def play_turn(self, action):
        player = self.engine.player

        valid_actions = ["w", "a", "s", "d", "1", "2", "3", "S", "C", "B"]
        if action not in valid_actions:
            return

        # Special Action: stash save
        if action == "S":
            self.state.stash_snapshot = self.state.clone()
            self.add_log("Stashed current working directory state!")
            self.chronicle.add_event("Executed: git stash save")
            return

        # Special Action: commit amend
        if action == "C":
            if "git commit --amend" not in player.inventory:
                self.add_log("No '--amend' item in your inventory!")
                return
            if not player.last_chest_loot:
                self.add_log("No chest opened recently to amend!")
                return
            player.inventory.remove("git commit --amend")
            self.chronicle.add_event("Executed: git commit --amend")

            # Reroll
            prev = player.last_chest_loot
            new_val = prev["value"] + 2
            new_name = "Amended Refined Codebase"
            player.weapon = {"name": new_name, "bonus": new_val}
            player.last_chest_loot = {"name": new_name, "type": "weapon", "value": new_val, "gold": 10}
            self.add_log(f"Amended! Rerolled weapon into: {new_name} (+{new_val})!")
            return

        # Special Action: checkout
        if action == "B":
            target = "Frontend Dev" if player.role == "Backend Dev" else "Backend Dev"
            success, msg = player.checkout_role(target)
            self.add_log(msg)
            if success:
                self.chronicle.add_event(f"Checked out class to: {target}")
            return

        # Decrement cooldowns
        for s_name in player.skills:
            if player.skills[s_name]["cooldown"] > 0:
                player.skills[s_name]["cooldown"] -= 1

        dx, dy = 0, 0
        if action == "w":
            dy = -1
        elif action == "s":
            dy = 1
        elif action == "a":
            dx = -1
        elif action == "d":
            dx = 1
        elif action in ["1", "2", "3"]:
            # Active Skills
            skill_idx = int(action) - 1
            skill_name = list(player.skills.keys())[skill_idx]
            skill = player.skills[skill_name]

            if skill["cooldown"] > 0:
                self.add_log(f"Skill {skill_name} is on cooldown!")
                return

            if skill_name == "Git Reset":
                player.heal(30)
                self.add_log("Git Reset executed! Healed 30 HP.")
                skill["cooldown"] = skill["max_cooldown"]
                self.chronicle.add_event("Cast: Git Reset (Heal)")
            elif skill_name == "Force Push":
                room = self.engine.get_current_room()
                pushed = False
                for enemy in room.enemies:
                    if abs(enemy.x - player.x) <= 1 and abs(enemy.y - player.y) <= 1:
                        pdx = enemy.x - player.x
                        pdy = enemy.y - player.y
                        nx, ny = enemy.x + pdx, enemy.y + pdy
                        if nx >= 0 and nx < room.width and ny >= 0 and ny < room.height and room.grid[ny][nx] == EMPTY:
                            enemy.x, enemy.y = nx, ny

                        # Apply unified engine damage check
                        dmg_res = self.engine.damage_enemy(enemy, 20)
                        self.add_log(f"Force Push executed! {dmg_res}")
                        self.event_bus.publish(DamageApplied("Player (Force Push)", enemy.name, 20, enemy.hp))
                        if enemy.hp <= 0:
                            self.event_bus.publish(EnemyDefeated(enemy.name, 15))
                        pushed = True
                        break
                if not pushed:
                    self.add_log("Force Push failed: No adjacent enemies.")
                    return
                skill["cooldown"] = skill["max_cooldown"]
            elif skill_name == "Cherry Pick":
                room = self.engine.get_current_room()
                if room.enemies:
                    target = room.enemies[0]
                    player.max_hp += 2
                    player.heal(2)

                    # Apply unified engine damage check
                    dmg_res = self.engine.damage_enemy(target, 30)
                    self.add_log(f"Cherry Picked {target.name}! {dmg_res}")
                    self.event_bus.publish(DamageApplied("Player (Cherry Pick)", target.name, 30, target.hp))
                    if target.hp <= 0:
                        self.event_bus.publish(EnemyDefeated(target.name, 15))
                    skill["cooldown"] = skill["max_cooldown"]
                else:
                    self.add_log("Cherry Pick failed: No enemies.")
                    return
            return

        if dx != 0 or dy != 0:
            result = self.engine.move_player(dx, dy)
            if result.startswith("COMBAT:"):
                # Parse out combat log
                combat_log = result.split("COMBAT:")[1]
                self.add_log(combat_log)
                self.chronicle.add_event(f"Engaged in combat: {combat_log}")
            elif result == "PORTAL_FORWARD":
                self.add_log("Traveled forward in git DAG timeline!")
                self.state.cleared_room_hashes.add(self.state.current_hash)
            elif result == "PORTAL_BACK":
                self.add_log("Traveled back in git history parent commit!")
                self.state.cleared_room_hashes.add(self.state.current_hash)
            elif result == "VICTORY_CANDIDATE":
                room = self.engine.get_current_room()
                if room.enemies:
                    self.add_log("Resolve all Merge Conflicts first!")
                else:
                    self.won = True
                    self.game_over = True

        # Check real-world validations!
        self.check_active_quest_validation()

        # Update enemies
        if player.hp > 0 and not self.game_over:
            enemy_logs = self.engine.update_enemies()
            for elog in enemy_logs:
                self.add_log(elog)

        if player.hp <= 0:
            # Check stash pop restore
            if self.state.stash_snapshot:
                self.state.restore_from(self.state.stash_snapshot)
                player.hp = self.state.hp
                player.max_hp = self.state.max_hp
                player.x = self.state.player_x
                player.y = self.state.player_y
                player.role = self.state.role
                player.weapon = self.state.weapon
                player.armor = self.state.armor
                player.inventory = self.state.inventory
                self.engine.current_hash = self.state.current_hash
                self.state.stash_snapshot = None
                self.add_log("★ Session restored from git stash pop! You were saved!")
                self.chronicle.add_event("Died in battle. State successfully restored from git stash!")
            else:
                self.game_over = True

def get_char_input():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def run_game():
    clear_screen()
    print("\033[1;36m" + r"""
  ____ _ _    ___                  _
 / ___(_) |_ / _ \ _   _  ___  ___| |_
| |  _| | __| | | | | | |/ _ \/ __| __|
| |_| | | |_| |_| | |_| |  __/\__ \ |_
 \____|_|\__|\__\_\\__,_|\___||___/\__|

""" + "\033[0m")
    print("\033[1;32mWelcome to GitQuest: The Playable Repository Cockpit!\033[0m")
    print("-" * 60)
    print("Choose your cockpit Campaign select:")
    print("  [1] Archive Expedition: Explore the historical timeline of your repository commits")
    print("  [2] Active Campaign: Accept structured quests compiled directly from active code signals (TODOs, changes)")
    print("  [3] Release Raid: Prepare the current working tree and HEAD for safe deployment")
    print("-" * 60)
    print("Select Campaign [1-3] or press Q to exit:")

    choice = get_char_input()
    if choice.lower() == "q":
        return

    if choice not in ["1", "2", "3"]:
        choice = "1"

    game = TerminalGame(campaign_choice=choice)

    clear_screen()
    print("\033[1;32mEntering the cockpit timeline...\033[0m")
    time.sleep(1)

    while not game.game_over:
        game.draw()
        ch = get_char_input()
        if ch.lower() == "q":
            break
        game.play_turn(ch)

    clear_screen()
    if game.won:
        print("\033[1;32;5m" + r"""
__     _____ ____ _____ ___  ______     __
\ \   / /_ _/ ___|_   _/ _ \|  _ \ \   / /
 \ \ / / | | |     | || | | | |_) \ \ / /
  \ V /  | | |___  | || |_| |  _ < \ V /
   \_/  |___\____| |_| \___/|_| \_\ \_/

""" + "\033[0m")
        print("\033[1;32mVictory! All merge commits resolved, quality validations proved, and merged cleanly into HEAD!\033[0m\n")
    else:
        print("\033[1;31m" + r"""
  ____    _    __  __ _____    _____     _______ ____
 / ___|  / \  |  \/  | ____|  / _ \ \   / / ____|  _ \
| |  _  / _ \ | |\/| |  _|   | | | \ \ / /|  _| | |_) |
| |_| |/ ___ \| |  | | |___  | |_| |\ V / | |___|  _ <
 \____/_/   \_\_|  |_|_____|  \___/  \_/  |_____|_| \_\

""" + "\033[0m")
        print("\033[1;31mPipeline aborted due to severe uncommitted changes/unhandled exceptions!\033[0m\n")

    # Generate and print the beautiful Narrative Engineering Chronicle!
    print(game.chronicle.generate_narrative_summary())
    print("\nPress any key to exit GitQuest.")
    get_char_input()

if __name__ == "__main__":
    try:
        run_game()
    except KeyboardInterrupt:
        clear_screen()
        print("Session disconnected.")
