"""
GitQuest custom Git DAG Level Designer & Scenario Builder.
Provides a step-by-step interactive command-line interface to let players
design custom Git commit topologies, types, and messages, then play them instantly.
"""

import sys
import time
from gitquest.ui.graph import DAGVisualizer

def run_interactive_builder():
    """
    Renders an interactive terminal CLI to guide the user in designing a custom Git history.
    Returns: list of constructed commit dictionaries, ready for GameEngine.
    """
    commits = []

    # Helper to clean screen and show banner
    def print_header():
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.write("\033[1;35m" + r"""
  ____ _ _    ___                  _     ____        _ _     _
 / ___(_) |_ / _ \ _   _  ___  ___| |_  | __ ) _   _(_) | __| | ___ _ __
| |  _| | __| | | | | | |/ _ \/ __| __| |  _ \| | | | | |/ _` |/ _ \ '__|
| |_| | | |_| |_| | |_| |  __/\__ \ |_  | |_) | |_| | | | (_| |  __/ |
 \____|_|\__|\__\_\\__,_|\___||___/\__| |____/ \__,_|_|_|\__,_|\___|_|

""" + "\033[0m")
        sys.stdout.write("=== GitQuest Custom DAG Level Designer & Scenario Builder ===\n")
        sys.stdout.write("Create your own Git history branches, merges, and commit dungeons!\n")
        sys.stdout.write("-" * 70 + "\n\n")

    # Start with a default root commit
    root_hash = "custom_root_commit_sha_00000000000000001"
    commits.append({
        "hash": root_hash,
        "short_hash": "root001",
        "parents": [],
        "branches": ["main"],
        "author": "Creator",
        "timestamp": int(time.time()),
        "subject": "Initial repository structure",
        "modified_files": ["README.md", "main.py"],
        "type": "feat"
    })

    id_to_hash = {"root": root_hash}

    while True:
        print_header()

        # Render current DAG using visualizer
        sys.stdout.write("\033[1;34mCurrent Git DAG Graph:\033[0m\n")
        vis = DAGVisualizer(commits)
        graph_lines = vis.render_ascii_graph(commits[-1]["hash"], limit=10)
        for line in graph_lines:
            sys.stdout.write(f"  {line}\n")
        sys.stdout.write("\n")

        # Show current commits list
        sys.stdout.write("\033[1;36mCommits Database:\033[0m\n")
        for i, c in enumerate(commits):
            sys.stdout.write(f"  [{c['short_hash']}] Type: {c['type'].upper()} | Subject: {c['subject']}\n")
        sys.stdout.write("-" * 70 + "\n")

        # Commands menu
        sys.stdout.write("Options:\n")
        sys.stdout.write("  [1] Add a New Commit (Diverge/Extend history)\n")
        sys.stdout.write("  [2] Set HEAD branch marker to the last commit\n")
        sys.stdout.write("  [3] Clear and reset to initial root commit\n")
        sys.stdout.write("  [4] Compile and Play this custom DAG dungeon!\n")
        sys.stdout.write("  [5] Exit Builder\n\n")
        sys.stdout.write("Select an option [1-5]: ")
        sys.stdout.flush()

        choice = sys.stdin.readline().strip()

        if choice == "1":
            print_header()
            sys.stdout.write("\033[1;32m--- Add New Commit ---\033[0m\n")

            # 1. Ask for identifier
            sys.stdout.write("Enter a short identifier for this commit (e.g. 'c2', 'feat1', 'fix2'): ")
            sys.stdout.flush()
            cid = sys.stdin.readline().strip().lower()
            if not cid:
                cid = f"commit{len(commits) + 1}"

            if cid in id_to_hash:
                sys.stdout.write("\nAn identifier with that name already exists! Press Enter to continue.")
                sys.stdout.flush()
                sys.stdin.readline()
                continue

            full_hash = f"custom_{cid}_sha_" + "0" * (40 - len(cid) - 11) + "1"

            # 2. Ask for parents
            sys.stdout.write("\nAvailable potential parent identifiers:\n")
            for name in id_to_hash:
                sys.stdout.write(f"  - {name}\n")
            sys.stdout.write("Enter parent identifier(s) separated by spaces (e.g. 'root' or 'c1 c2' for merges): ")
            sys.stdout.flush()
            parent_ids = sys.stdin.readline().strip().split()

            parents = []
            for pid in parent_ids:
                if pid in id_to_hash:
                    parents.append(id_to_hash[pid])

            # Fallback to last commit if no parent specified
            if not parents and commits:
                parents = [commits[-1]["hash"]]

            # 3. Ask for commit type (determines monsters / items)
            sys.stdout.write("\nCommit Types:\n")
            sys.stdout.write("  - feat     (Spawns loot chests and items)\n")
            sys.stdout.write("  - fix      (Spawns Bug monsters to fight)\n")
            sys.stdout.write("  - merge    (Spawns protected Merge Conflict Bosses)\n")
            sys.stdout.write("  - docs     (Spawns helpful Lore terminals)\n")
            sys.stdout.write("  - refactor (Spawns a mix of lore and loot)\n")
            sys.stdout.write("  - test     (Spawns ranged Compiler Errors)\n")
            sys.stdout.write("  - chore    (Spawns standard walls/layouts)\n")
            sys.stdout.write("Enter commit type: ")
            sys.stdout.flush()
            ctype = sys.stdin.readline().strip().lower()
            if ctype not in ["feat", "fix", "merge", "docs", "refactor", "test", "chore"]:
                ctype = "chore"

            # 4. Subject / Message
            sys.stdout.write("\nEnter commit subject message: ")
            sys.stdout.flush()
            subject = sys.stdin.readline().strip()
            if not subject:
                subject = f"Custom development work on {cid}"

            # 5. Modified Files (affects room layouts)
            sys.stdout.write("Enter modified files separated by spaces (e.g. 'app.py server.js'): ")
            sys.stdout.flush()
            modified = sys.stdin.readline().strip().split()
            if not modified:
                modified = ["custom_file.py"]

            # Add to DAG
            id_to_hash[cid] = full_hash
            commits.append({
                "hash": full_hash,
                "short_hash": cid[:7],
                "parents": parents,
                "branches": [],
                "author": "Creator",
                "timestamp": int(time.time()),
                "subject": subject,
                "modified_files": modified,
                "type": ctype
            })

            sys.stdout.write(f"\nSuccessfully added commit [{cid[:7]}]! Press Enter to continue.")
            sys.stdout.flush()
            sys.stdin.readline()

        elif choice == "2":
            # Add HEAD branch decoration to the very last commit so game knows where the end is
            if commits:
                for c in commits:
                    if "HEAD" in c["branches"]:
                        c["branches"].remove("HEAD")
                commits[-1]["branches"].append("HEAD")
                sys.stdout.write("\nSuccessfully set HEAD branch marker to last commit! Press Enter to continue.")
            else:
                sys.stdout.write("\nNo commits found to tag as HEAD! Press Enter to continue.")
            sys.stdout.flush()
            sys.stdin.readline()

        elif choice == "3":
            commits = [{
                "hash": root_hash,
                "short_hash": "root001",
                "parents": [],
                "branches": ["main"],
                "author": "Creator",
                "timestamp": int(time.time()),
                "subject": "Initial repository structure",
                "modified_files": ["README.md", "main.py"],
                "type": "feat"
            }]
            id_to_hash = {"root": root_hash}
            sys.stdout.write("\nReset designer to root commit! Press Enter to continue.")
            sys.stdout.flush()
            sys.stdin.readline()

        elif choice == "4":
            # Set HEAD to the last commit if not already present
            has_head = any("HEAD" in c["branches"] for c in commits)
            if not has_head and commits:
                commits[-1]["branches"].append("HEAD")
            return commits

        elif choice == "5":
            return None
        else:
            sys.stdout.write("\nInvalid choice! Press Enter to try again.")
            sys.stdout.flush()
            sys.stdin.readline()
