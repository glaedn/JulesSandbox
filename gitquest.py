#!/usr/bin/env python3
import sys
from gitquest.interfaces.terminal import run_terminal_game

if __name__ == "__main__":
    try:
        run_terminal_game()
    except KeyboardInterrupt:
        sys.stdout.write("\nSession disconnected. Bye!\n")
        sys.exit(0)
