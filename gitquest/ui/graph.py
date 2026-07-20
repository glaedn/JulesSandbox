class DAGVisualizer:
    def __init__(self, commits):
        """commits is a list of structured commits from GitCLIAdapter."""
        self.commits = commits
        self.hash_to_commit = {c["hash"]: c for c in commits}
        self.children_map = {c["hash"]: [] for c in commits}
        for c in commits:
            for p in c["parents"]:
                if p in self.children_map:
                    self.children_map[p].append(c["hash"])

    def render_ascii_graph(self, current_hash, limit=7):
        """Renders a lane-based ASCII DAG graph, centering on current_hash."""
        if not self.commits:
            return ["(No commits found)"]

        # Locate index of current commit
        active_idx = -1
        for i, c in enumerate(self.commits):
            if c["hash"] == current_hash:
                active_idx = i
                break

        if active_idx == -1:
            active_idx = 0

        # Select surrounding commits
        start = max(0, active_idx - limit // 2)
        end = min(len(self.commits), start + limit)
        selected_commits = self.commits[start:end]

        # Simple lane-based visualizer:
        # We assign each commit a lane. Commits that share a parent can branch.
        lines = []
        active_branches = []

        for idx, c in enumerate(selected_commits):
            chash = c["hash"]
            is_active = (chash == current_hash)

            # Decide lane placement
            if chash not in active_branches:
                active_branches.append(chash)
            lane_idx = active_branches.index(chash)

            # Build connection graphic
            # Draw lanes
            lane_chars = []
            for j in range(max(1, len(active_branches))):
                if j == lane_idx:
                    node = "@" if is_active else "*"
                    if is_active:
                        node = f"\033[92;1m{node}\033[0m" # highlight green
                    lane_chars.append(node)
                else:
                    lane_chars.append("|")

            graph_part = "  ".join(lane_chars)

            # Describe commit
            subj_truncated = c["subject"][:22]
            desc = f" [{c['short_hash']}] {subj_truncated}"
            if is_active:
                desc += " \033[93m<- HEAD\033[0m"

            lines.append(f" {graph_part} {desc}")

            # Draw bridge line to next commit
            # Resolve parents
            parents = c["parents"]
            if idx < len(selected_commits) - 1:
                # Update active branches for next row
                next_commit_hash = selected_commits[idx + 1]["hash"]

                # Replace current commit with its parents in active_branches
                if chash in active_branches:
                    pos = active_branches.index(chash)
                    if parents:
                        active_branches[pos] = parents[0]
                        # append other parents as new branches
                        for other_p in parents[1:]:
                            if other_p not in active_branches:
                                active_branches.append(other_p)
                    else:
                        active_branches.pop(pos)

                # Draw vertical links
                bridge_chars = []
                for j in range(max(1, len(active_branches))):
                    bridge_chars.append("|")
                lines.append("  " + "  ".join(bridge_chars))

        return lines

if __name__ == "__main__":
    mock_commits = [
        {"hash": "c1", "short_hash": "c100000", "parents": ["c2"], "author": "Alice", "subject": "Fix token refreshing"},
        {"hash": "c2", "short_hash": "c200000", "parents": ["c3", "b1"], "author": "Bob", "subject": "Merge feature-auth"},
        {"hash": "c3", "short_hash": "c300000", "parents": ["c4"], "author": "Alice", "subject": "Core authentication foundation"},
        {"hash": "b1", "short_hash": "b100000", "parents": ["c4"], "author": "Charlie", "subject": "Add login page UI"},
        {"hash": "c4", "short_hash": "c400000", "parents": [], "author": "Bob", "subject": "Initial commit"}
    ]
    vis = DAGVisualizer(mock_commits)
    print("\n".join(vis.render_ascii_graph("c2")))
