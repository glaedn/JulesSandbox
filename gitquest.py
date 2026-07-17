import sys
import tty
import termios
import time
from gitquest_engine import (
    GameEngine, EMPTY, WALL, PLAYER, BUG, MERGE_CONFLICT,
    HEAD_PILLAR, INCOMING_PILLAR, COMPILER_ERROR, LINT_WARNING,
    MERGED_PORTAL, PARENT_PORTAL, LORE_TERMINAL, LOOT_CHEST
)

# ANSI styling helper functions
def clear_screen():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()

def draw_text(text, color_code):
    return f"{color_code}{text}\033[0m"

# Map game entity characters to styles
COLOR_MAP = {
    WALL: "\033[37m#",          # White / Gray wall
    EMPTY: " ",
    PLAYER: "\033[92m@",        # Green player
    BUG: "\033[91mB",           # Red bug
    MERGE_CONFLICT: "\033[31;1mM", # Bright/bold red conflict
    HEAD_PILLAR: "\033[96mH",     # Cyan HEAD pillar
    INCOMING_PILLAR: "\033[93mI", # Yellow Incoming pillar
    COMPILER_ERROR: "\033[95mC", # Magenta compiler error
    LINT_WARNING: "\033[93mL",   # Yellow linter warning
    MERGED_PORTAL: "\033[96m>",  # Cyan portal forward
    PARENT_PORTAL: "\033[94m<",  # Blue portal backward
    LORE_TERMINAL: "\033[36mT",  # Cyan docs terminal
    LOOT_CHEST: "\033[33m$",     # Yellow loot chest
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
    def __init__(self):
        self.engine = GameEngine()
        self.status_message = "Welcome to GitQuest! Find your way to HEAD through the git history DAG."
        self.log_messages = []
        self.game_over = False
        self.won = False

    def add_log(self, msg):
        self.log_messages.append(msg)
        if len(self.log_messages) > 6:
            self.log_messages.pop(0)

    def draw_git_graph(self):
        """Generates real-time ASCII Git Graph of surrounding commits."""
        current_hash = self.engine.current_hash
        graph_lines = []

        # Display up to 5 commits centering around active commit
        active_idx = -1
        for i, c in enumerate(self.engine.commits):
            if c["hash"] == current_hash:
                active_idx = i
                break

        start = max(0, active_idx - 2)
        end = min(len(self.engine.commits), active_idx + 3)

        for idx in range(start, end):
            c = self.engine.commits[idx]
            marker = "*"
            if c["hash"] == current_hash:
                marker = draw_text("@", "\033[92;1m")
                desc = f"{marker} [{c['short_hash']}] (HEAD - You are here) - {c['subject'][:22]}"
            else:
                desc = f"* [{c['short_hash']}] - {c['subject'][:25]}"

            # Print connections
            if idx > start:
                graph_lines.append("  |")
            graph_lines.append(f"  {desc}")

        return graph_lines

    def draw(self):
        room = self.engine.get_current_room()
        player = self.engine.player

        # Build layout lines
        header_lines = [
            "\033[1;36m=== GitQuest: Interactive Git history DAG Roguelike ===\033[0m",
            f"Commit: \033[93m{room.commit['short_hash']}\033[0m | Branches: \033[92m{', '.join(room.commit.get('branches', [])) or 'detached'}\033[0m | Type: \033[95m{room.commit.get('type', 'chore').upper()}\033[0m",
            f"Subject: {room.commit.get('subject', '')[:65]}",
            "-" * 80
        ]

        # Side-by-side columns: Map on the left, Git Status dashboard on the right!
        grid_lines = []
        for y in range(room.height):
            line_chars = []
            for x in range(room.width):
                line_chars.append(get_char_at(room, x, y, player))
            grid_lines.append("".join(line_chars))

        # Build dashboard lines
        dash_lines = [
            f"\033[1;35mOn branch {player.role}\033[0m",
            f"HP: \033[92m{player.hp}/{player.max_hp}\033[0m | Level: {player.level} ({player.xp}/{player.xp_to_next} XP)",
            f"Stars: \033[93m{player.gold} ★\033[0m",
            f"Weapon: \033[96m{player.weapon['name']} (+{player.weapon['bonus']})\033[0m",
            f"Armor: \033[96m{player.armor['name']} (+{player.armor['bonus']})\033[0m",
            f"Stash data: {'[SAVED STATS]' if player.stash_data else '[EMPTY]'}",
            f"Inventory: {', '.join(player.inventory) if player.inventory else 'None'}",
            "",
            "\033[1;34m--- Git DAG Graph ---\033[0m",
        ] + self.draw_git_graph()

        # Padding dashboard lines to match height
        while len(dash_lines) < room.height:
            dash_lines.append("")

        # Combine columns side-by-side
        combined_body = []
        for y in range(room.height):
            # Left side (map) + separator + Right side (dashboard)
            combined_body.append(f"{grid_lines[y]}   |   {dash_lines[y]}")

        footer_lines = [
            "-" * 80,
            "\033[1;35m--- Active Skills Cooldowns ---\033[0m"
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

        while len(footer_lines) < 14: # Padding logs to keep screen stable
            footer_lines.append("")

        footer_lines.append("\033[1;37mControls:\033[0m")
        footer_lines.append("  \033[92mw/a/s/d\033[0m: Move / Attack | \033[93m1,2,3\033[0m: Active Git Skills")
        footer_lines.append("  \033[96mS\033[0m (Shift+s): git stash current state | \033[96mC\033[0m (Shift+c): git commit --amend (Reroll chest)")
        footer_lines.append("  \033[96mB\033[0m (Shift+b): git checkout branch (Swap player class) | \033[95mQ\033[0m (or q): Quit")

        # Render the full screen
        clear_screen()
        sys.stdout.write("\n".join(header_lines + combined_body + footer_lines) + "\n")
        sys.stdout.flush()

    def play_turn(self, action):
        player = self.engine.player

        # Verify valid inputs
        valid_actions = ["w", "a", "s", "d", "1", "2", "3", "S", "C", "B"]
        if action not in valid_actions:
            return

        # Special Action: git stash
        if action == "S":
            res = self.engine.stash_save()
            self.add_log(res)
            return

        # Special Action: git commit --amend
        if action == "C":
            res = self.engine.amend_chest_loot()
            self.add_log(res)
            return

        # Special Action: git checkout
        if action == "B":
            target = "Frontend Dev" if player.role == "Backend Dev" else "Backend Dev"
            success, msg = player.checkout_role(target)
            self.add_log(msg)
            return

        # Decrement skills cooldown
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
            # Skills logic
            skill_idx = int(action) - 1
            skill_name = list(player.skills.keys())[skill_idx]
            skill = player.skills[skill_name]

            if skill["cooldown"] > 0:
                self.add_log(f"Skill {skill_name} is on cooldown for {skill['cooldown']} turns!")
                return

            if skill_name == "Git Reset":
                player.heal(30)
                self.add_log("Git Reset executed! Healed 30 HP.")
                skill["cooldown"] = skill["max_cooldown"]
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
                        enemy.hp -= 20
                        self.add_log(f"Force Push executed! Pushed back {enemy.name} and dealt 20 damage.")
                        if enemy.hp <= 0:
                            room.enemies.remove(enemy)
                            player.gain_xp(15)
                            self.add_log(f"Killed {enemy.name} with Force Push!")
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
                    target.hp -= 30
                    player.max_hp += 2 # Absorb Max HP
                    player.heal(2)
                    self.add_log(f"Cherry Picked {target.name} for 30 HP and absorbed +2 Max HP!")
                    if target.hp <= 0:
                        room.enemies.remove(target)
                        player.gain_xp(15)
                        self.add_log(f"Killed {target.name} with Cherry Pick!")
                    skill["cooldown"] = skill["max_cooldown"]
                else:
                    self.add_log("Cherry Pick failed: No enemies to target in this room.")
                    return
            return

        if dx != 0 or dy != 0:
            result = self.engine.move_player(dx, dy)
            if result.startswith("COMBAT:"):
                self.add_log(result.split("COMBAT:")[1])
            elif result.startswith("LOOT_WEAPON:"):
                p = result.split(":")
                self.add_log(f"Looted a {p[1]} ({p[2]})! Type 'C' to git commit --amend.")
            elif result.startswith("LOOT_ARMOR:"):
                p = result.split(":")
                self.add_log(f"Looted a {p[1]} ({p[2]})! Type 'C' to git commit --amend.")
            elif result.startswith("LOOT_GOLD:"):
                self.add_log(f"Earned {result.split(':')[1]} GitHub Stars!")
            elif result.startswith("TERMINAL:"):
                self.add_log(f"Terminal: {result.split('TERMINAL:')[1]}")
            elif result == "PORTAL_FORWARD":
                self.add_log("Traveled forward in git history DAG branch!")
            elif result == "PORTAL_BACK":
                self.add_log("Traveled back in git history parent commit!")
            elif result == "VICTORY_CANDIDATE":
                room = self.engine.get_current_room()
                if room.enemies:
                    self.add_log("Resolve all Merge Conflicts or bugs in current HEAD commit room first!")
                else:
                    self.won = True
                    self.game_over = True

        # Update enemies if alive
        if player.hp > 0 and not self.game_over:
            enemy_logs = self.engine.update_enemies()
            for elog in enemy_logs:
                self.add_log(elog)

        if player.hp <= 0:
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
    game = TerminalGame()

    # Intro screen
    clear_screen()
    print("\033[1;36m" + r"""
  ____ _ _    ___                  _
 / ___(_) |_ / _ \ _   _  ___  ___| |_
| |  _| | __| | | | | | |/ _ \/ __| __|
| |_| | | |_| |_| | |_| |  __/\__ \ |_
 \____|_|\__|\__\_\\__,_|\___||___/\__|

""" + "\033[0m")
    print("\033[1;32mWelcome, Developer, to GitQuest: True DAG Traversal!\033[0m")
    print("A git history-based dungeon crawler roguelike RPG built directly in your terminal.")
    print("Explore multi-branch paths, checkout branch classes, stash on death, and resolve Merge Boss conflicts!")
    print("\nPress any key to load your git logs and enter the git space...")
    get_char_input()

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
        print("\033[1;32mCongratulations! You have successfully resolved all git commits, defeated all bugs, and merged into HEAD!\033[0m")
        print(f"Final Level: {game.engine.player.level} | GitHub Stars: {game.engine.player.gold}")
    else:
        print("\033[1;31m" + r"""
  ____    _    __  __ _____    _____     _______ ____
 / ___|  / \  |  \/  | ____|  / _ \ \   / / ____|  _ \
| |  _  / _ \ | |\/| |  _|   | | | \ \ / /|  _| | |_) |
| |_| |/ ___ \| |  | | |___  | |_| |\ V / | |___|  _ <
 \____/_/   \_\_|  |_|_____|  \___/  \_/  |_____|_| \_\

""" + "\033[0m")
        print("\033[1;31mYour local changes were discarded due to fatal bug exceptions. Rest in peace, Dev.\033[0m")
        print(f"Final level: {game.engine.player.level} | Gold/Stars: {game.engine.player.gold}")

if __name__ == "__main__":
    try:
        run_game()
    except KeyboardInterrupt:
        clear_screen()
        print("Discarding session. Bye!")
