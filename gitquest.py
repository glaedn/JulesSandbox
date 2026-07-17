import sys
import tty
import termios
import time
from gitquest_engine import GameEngine, EMPTY, WALL, PLAYER, BUG, MERGE_CONFLICT, COMPILER_ERROR, LINT_WARNING, MERGED_PORTAL, PARENT_PORTAL, LORE_TERMINAL, LOOT_CHEST

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
    COMPILER_ERROR: "\033[95mC", # Magenta compiler error
    LINT_WARNING: "\033[93mL",   # Yellow linter warning
    MERGED_PORTAL: "\033[96m>",  # Cyan portal forward
    PARENT_PORTAL: "\033[94m<",  # Blue portal backward
    LORE_TERMINAL: "\033[36mT",  # Cyan docs terminal
    LOOT_CHEST: "\033[33m$",     # Yellow loot chest
}

def get_char_at(room, x, y, player):
    # Check if player is here
    if player.x == x and player.y == y:
        return draw_text("@", "\033[92;1m")

    # Check enemies
    for enemy in room.enemies:
        if enemy.x == x and enemy.y == y:
            return draw_text(enemy.symbol, enemy.color)

    # Check general map grid cell
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

    def draw(self):
        room = self.engine.get_current_room()
        player = self.engine.player

        # Build screen buffer
        buffer = []
        buffer.append("\033[1;36m=== GitQuest: Terminal Roguelike ==\033[0m")
        buffer.append(f"Commit: \033[93m{room.commit['short_hash']}\033[0m | Author: {room.commit['author']} | Type: \033[95m{room.commit['type'].upper()}\033[0m")
        buffer.append(f"Subject: {room.commit['subject'][:50]}")
        buffer.append("-" * 40)

        # Render map grid
        for y in range(room.height):
            line = []
            for x in range(room.width):
                line.append(get_char_at(room, x, y, player))
            buffer.append("".join(line))

        buffer.append("-" * 40)
        # Stats display
        buffer.append(f"\033[92mHP: {player.hp}/{player.max_hp}\033[0m | \033[93mStars (Gold): {player.gold}\033[0m | Level: {player.level} ({player.xp}/{player.xp_to_next} XP)")
        buffer.append(f"Weapon: \033[96m{player.weapon['name']} (+{player.weapon['bonus']})\033[0m | Armor: \033[96m{player.armor['name']} (+{player.armor['bonus']})\033[0m")

        buffer.append("\033[1;35m--- Skill Cooldowns ---\033[0m")
        skills_str = []
        for name, data in player.skills.items():
            cd = data["cooldown"]
            cd_str = f"{name}: \033[91m{cd}t\033[0m" if cd > 0 else f"{name}: \033[92mREADY\033[0m"
            skills_str.append(cd_str)
        buffer.append(" | ".join(skills_str))

        buffer.append("\033[1;33m--- LOGS ---\033[0m")
        for log in self.log_messages:
            buffer.append(f"  {log}")
        while len(buffer) < 24: # Padding
            buffer.append("")

        buffer.append("\033[1mControls: WASD to Move/Attack | 1-3 Git Skills | Q to Quit\033[0m")

        # Print output all at once
        clear_screen()
        sys.stdout.write("\n".join(buffer) + "\n")
        sys.stdout.flush()

    def play_turn(self, action):
        player = self.engine.player

        # Verify valid key inputs
        if action not in ["w", "a", "s", "d", "1", "2", "3"]:
            # If the user presses an invalid key, do not advance turn
            return

        # Decrement cooldowns on movement/skills
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
            # Special Skills
            skill_idx = int(action) - 1
            skill_name = list(player.skills.keys())[skill_idx]
            skill = player.skills[skill_name]

            if skill["cooldown"] > 0:
                self.add_log(f"Skill {skill_name} is on cooldown for {skill['cooldown']} more turns!")
                return

            # Trigger skill effect
            if skill_name == "Git Reset":
                player.heal(25)
                self.add_log("Git Reset executed! Healed 25 HP.")
                skill["cooldown"] = skill["max_cooldown"]
            elif skill_name == "Force Push":
                # Find adjacent enemy and force push
                room = self.engine.get_current_room()
                pushed = False
                for enemy in room.enemies:
                    if abs(enemy.x - player.x) <= 1 and abs(enemy.y - player.y) <= 1:
                        # Determine direction to push
                        pdx = enemy.x - player.x
                        pdy = enemy.y - player.y
                        nx, ny = enemy.x + pdx, enemy.y + pdy
                        # Push back if grid cell empty
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
                # Instant damage to random enemy in the room
                room = self.engine.get_current_room()
                if room.enemies:
                    target = room.enemies[0]
                    target.hp -= 30
                    self.add_log(f"Cherry Picked enemy {target.name} for 30 HP!")
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
                self.add_log(f"Looted a {p[1]} ({p[2]})!")
            elif result.startswith("LOOT_ARMOR:"):
                p = result.split(":")
                self.add_log(f"Looted a {p[1]} ({p[2]})!")
            elif result.startswith("LOOT_GOLD:"):
                self.add_log(f"Earned {result.split(':')[1]} GitHub Stars!")
            elif result.startswith("TERMINAL:"):
                self.add_log(f"Terminal: {result.split('TERMINAL:')[1]}")
            elif result == "PORTAL_FORWARD":
                self.add_log("Traveled forward in git history!")
            elif result == "PORTAL_BACK":
                self.add_log("Traveled back in git history!")
            elif result == "VICTORY_CANDIDATE":
                # Check if there are any remaining enemies in the final level to claim pure victory
                room = self.engine.get_current_room()
                if room.enemies:
                    self.add_log("Merge Conflicts or bugs block you from merging HEAD. Defeat them first!")
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

    # Simple intro screen
    clear_screen()
    print("\033[1;36m" + r"""
  ____ _ _    ___                  _
 / ___(_) |_ / _ \ _   _  ___  ___| |_
| |  _| | __| | | | | | |/ _ \/ __| __|
| |_| | | |_| |_| | |_| |  __/\__ \ |_
 \____|_|\__|\__\_\\__,_|\___||___/\__|

""" + "\033[0m")
    print("\033[1;32mWelcome, Developer, to GitQuest!\033[0m")
    print("A git history-based dungeon crawler roguelike RPG built directly in your terminal.")
    print("Travel through your local git commits as distinct dungeon rooms.")
    print("Enemies and loot are procedural, generated dynamically from the messages and authors.")
    print("\nPress any key to load your git logs and enter the git space...")
    get_char_input()

    while not game.game_over:
        game.draw()
        ch = get_char_input().lower()
        if ch == "q":
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
