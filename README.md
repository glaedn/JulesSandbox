# 🎮 GitQuest: The Interactive Git history DAG Roguelike RPG

Welcome to **GitQuest**, a genuinely novel, highly entertaining, and interactive terminal-based Roguelike game built entirely from scratch!

What makes **GitQuest** entirely unique is that **it dynamically generates the gameplay experience directly from your local git repository's DAG history!**

Every commit in your repository becomes a unique dungeon level (room). The enemies you face, the items/loot you find, and the map topology are completely procedurally generated based on the commit metadata, modified files, type of commit (e.g. `feat`, `fix`, `docs`, `merge`), and commit messages!

---

## 🌟 Expanded Git Metaphor Features

### 1. Multi-Branch Navigation (True DAG Traversal)
- Real repositories diverge and merge! GitQuest supports multiple parent and child portals per room based on your branch forks and merges.
- Standing near or entering portals lets you traverse parallel feature branches.

### 2. Interactive "Git Status" Dashboard & Real-Time Graph
- Features a side-by-side terminal dashboard.
- Displays your character's class/role as `On branch <class>`.
- Displays a real-time ASCII representation of surrounding commits on your active Git commit DAG!

### 3. Git-Themed Inventory & Commands
- **`git stash` (Press `S`)**: Stashes/Saves your exact player state (cooldowns, HP, stats, gold). If you die, your session is automatically restored via `git stash pop` so you don't lose progress!
- **`git commit --amend` (Press `C`)**: Rerolls the reward of the last chest you opened, guaranteeing an improved bonus!
- **`git checkout` (Press `B`)**: Swaps between two unique player roles (branches):
  - 🖥️ **Frontend Dev**: Fast & agile (80 Max HP, 22 Basic Attack, 3 Defense).
  - ⚙️ **Backend Dev**: Sturdy & robust (120 Max HP, 12 Basic Attack, 8 Defense).

### 4. Merge Conflict Boss Shield Mechanic
- In `merge` commits, you will encounter the **Merge Conflict Boss (`M`)**.
- The boss is protected by a strong shield as long as any of its conflict pillars (**`HEAD Pillar` (`H`)** and **`Incoming Pillar` (`I`)**) are active.
- To make the boss vulnerable, you must attack and destroy either of the pillars to "resolve" the conflict and strip the boss's shield!

---

## 🎮 How to Play

### Controls
- **`W`, `A`, `S`, `D`**: Move Up, Left, Down, and Right or attack adjacent enemies/pillars.
- **`1`**: Cast *Git Reset* (Heal skill).
- **`2`**: Cast *Force Push* (Push and damage skill).
- **`3`**: Cast *Cherry Pick* (Snipe & Max HP absorb skill).
- **`S`**: Execute `git stash` (Save current state).
- **`C`**: Execute `git commit --amend` (Reroll last chest loot).
- **`B`**: Execute `git checkout branch` (Swap Frontend/Backend Dev roles).
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
