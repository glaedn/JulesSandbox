#!/usr/bin/env python3
"""
GitQuest Sandbox, Scenario Arena, & Git School Dedicated Launcher.
Launches the educational and customizable simulated Git environments directly.
"""

import sys
import tty
import termios
import time

from gitquest.interfaces.terminal import TerminalInterface, clear_screen, get_char_input
from gitquest.scenarios.definitions import SCENARIOS, load_scenario
from gitquest.scenarios.tutorials import TUTORIALS, load_tutorial
from gitquest.ui.builder import run_interactive_builder

def run_sandbox_launcher():
    clear_screen()
    print("\033[1;35m" + r"""
  ____  _ _    ___                  _     ____                  _ _
 / ___|(_) |_ / _ \ _   _  ___  ___| |_  / ___|  __ _ _ __   __| | |__   _____  __
| |  _ | | __| | | | | | |/ _ \/ __| __| \___ \ / _` | '_ \ / _` | '_ \ / _ \ \/ /
| |_| || | |_| |_| | |_| |  __/\__ \ |_   ___) | (_| | | | | (_| | |_) | (_) >  <
 \____|____\__|\__\_\\__,_|\___||___/\__| |____/ \__,_|_| |_|\__,_|_.__/ \___/_/\_\

""" + "\033[0m")
    print("\033[1;32mWelcome to the Dedicated GitQuest Sandbox and Git School!\033[0m")
    print("-" * 75)
    print("Choose your simulated Git operations experience:")
    print("  [1] Scenario Arena: Play hand-crafted simulated Git DAG missions")
    print("  [2] Git School: Practice Git commands (stash, checkout, amend) interactively")
    print("  [3] Scenario Builder: Design your own custom Git commit graph dungeons")
    print("-" * 75)
    print("Select Option [1-3] or press Q to exit:")

    choice = get_char_input()
    if choice.lower() == "q":
        sys.stdout.write("\nLauncher closed. See you next commit!\n")
        return

    if choice not in ["1", "2", "3"]:
        choice = "1"

    custom_commits = None
    campaign_choice = "4"

    if choice == "1":
        campaign_choice = "4"
        clear_screen()
        print("\033[1;35m=== Scenario Arena: Choose your Mission ===\033[0m")
        print("-" * 65)
        for k, v in SCENARIOS.items():
            print(f"  [{k}] {v['name']}")
        print("-" * 65)
        print("Select Mission [1-4] or press Q to return:")
        m_choice = get_char_input()
        if m_choice.lower() == "q" or m_choice not in SCENARIOS:
            return
        custom_commits = load_scenario(m_choice)

    elif choice == "2":
        campaign_choice = "5"
        clear_screen()
        print("\033[1;36m=== Git School: Interactive Tutorial Lessons ===\033[0m")
        print("-" * 65)
        for k, v in TUTORIALS.items():
            print(f"  [{k}] {v['name']}")
        print("-" * 65)
        print("Select Lesson [1-4] or press Q to return:")
        l_choice = get_char_input()
        if l_choice.lower() == "q" or l_choice not in TUTORIALS:
            return
        custom_commits = load_tutorial(l_choice)

    elif choice == "3":
        campaign_choice = "6"
        custom_commits = run_interactive_builder()
        if not custom_commits:
            return

    game = TerminalInterface(campaign_choice=campaign_choice, custom_commits=custom_commits)

    clear_screen()
    print("\033[1;32mBooting simulated virtual timeline...\033[0m")
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
        print("\033[1;32mSimulation Completed Successfully! Deployments verified cleanly!\033[0m\n")
    else:
        print("\033[1;31m" + r"""
  ____    _    __  __ _____    _____     _______ ____
 / ___|  / \  |  \/  | ____|  / _ \ \   / / ____|  _ \
| |  _  / _ \ | |\/| |  _|   | | | \ \ / /|  _| | |_) |
| |_| |/ ___ \| |  | | |___  | |_| |\ V / | |___|  _ <
 \____/_/   \_\_|  |_|_____|  \___/  \_/  |_____|_| \_\

""" + "\033[0m")
        print("\033[1;31mSimulation pipeline aborted due to game-over state.\033[0m\n")

    print(game.chronicle.generate_narrative_summary())
    print("\nPress any key to exit Sandbox Launcher.")
    get_char_input()

if __name__ == "__main__":
    try:
        run_sandbox_launcher()
    except KeyboardInterrupt:
        sys.stdout.write("\nLauncher disconnected. Bye!\n")
        sys.exit(0)
