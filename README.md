# 🎮 GitQuest: The Terminal Git Roguelike RPG

Welcome to **GitQuest**, a genuinely novel, highly entertaining, and interactive terminal-based Roguelike game built entirely from scratch!

What makes **GitQuest** entirely unique is that **it dynamically generates the gameplay experience directly from your local git repository's DAG history!**

Every commit in your repository becomes a unique dungeon level (room). The enemies you face, the items/loot you find, and the map topology are completely procedurally generated based on the commit metadata, modified files, type of commit (e.g. `feat`, `fix`, `docs`, `merge`), and commit messages!

---

## 🌟 Features

- **Procedural DAG-Based Dungeon Generation:** Walk forward or backward through your git commits! Merged/Forward portals (`>`) lead to younger commits, while Parent/Backward portals (`<`) lead to older parent commits.
- **Dynamic Git Elements:**
  - 🐛 **Bugs (`B`)**: Spawned inside `fix` commits. Watch out for these pesky critters!
  - 💥 **Merge Conflicts (`M`)**: Giant miniboss enemies spawned in `merge` commits. Extremely sturdy!
  - ❌ **Compiler Errors (`C`)**: Ranged enemies that attack when you get close.
  - ⚠️ **Linter Warnings (`L`)**: Highly agile, annoying enemies.
  - 📜 **Lore Terminals (`T`)**: Terminals showing real commit metadata, author information, and file names!
  - 💰 **Pull Requests & Code Refactoring (`$`)**: Loot chests containing real upgradeable items like weapons or armor and GitHub Stars (Gold).
- **Turn-based Tactical Roguelike combat:** Grid-based tactical movement and calculations. Enemies respond to your moves.
- **Git-Themed Special Skills:**
  - `1` **Git Reset**: Restore 25 HP to undo your mistakes.
  - `2` **Force Push**: Strike and push back adjacent enemies, dealing 20 damage.
  - `3` **Cherry Pick**: Target and execute a random enemy in the room from a distance.

---

## 🎮 How to Play

### Controls
- **`W`, `A`, `S`, `D`**: Move Up, Left, Down, and Right or attack adjacent enemies.
- **`1`**: Cast *Git Reset* (Heal skill).
- **`2`**: Cast *Force Push* (Push and damage skill).
- **`3`**: Cast *Cherry Pick* (Snipe skill).
- **`Q`**: Quit/Discard local changes.

### Objective
Your goal is to start from the root (initial commit) of your local git repository and fight your way forward to the **HEAD** of your branch. Clear all bugs and compile problems in the final commit to achieve pure deployment victory!

---

## 🛠️ System Requirements & Running

GitQuest is completely built in **Python 3** with zero external dependencies! It runs directly on any UNIX-like shell (Linux, macOS, BSD, WSL).

To launch GitQuest in any of your git repositories:
```bash
python3 gitquest.py
```

To run the automated test suite:
```bash
python3 -m unittest test_gitquest.py
```

Enjoy your descent into git history! Remember, any bugs you left in your commits will literally come back to bite you! 😉
