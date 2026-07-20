import time

class ChronicleReporter:
    def __init__(self, state):
        self.state = state

    def add_event(self, description):
        """Adds a log entry with a timestamp."""
        timestamp = time.strftime("%H:%M:%S")
        self.state.chronicle_entries.append(f"[{timestamp}] {description}")

    def generate_narrative_summary(self):
        """Compiles a coherent story and software engineering report of the session."""
        summary = []
        summary.append("\033[1;36m=== GitQuest Session Chronicle & Engineering Report ===\033[0m")
        summary.append(f"Developer: {self.state.player_name} ({self.state.role}) | Level: {self.state.level}")
        summary.append(f"Wealth: {self.state.gold} GitHub Stars | Completed Quests: {len(self.state.completed_quest_ids)}")
        summary.append("-" * 60)

        # Build story narrative based on game flags
        narrative_parts = []
        if self.state.completed_quest_ids:
            narrative_parts.append(f"You completed {len(self.state.completed_quest_ids)} structural workspace quests to reduce technical debt.")
        else:
            narrative_parts.append("You prioritized raw exploration over structural task resolution.")

        if self.state.gold > 20:
            narrative_parts.append("Your work was highly valued by the community, earning considerable GitHub stars.")

        if self.state.cleared_room_hashes:
            narrative_parts.append(f"You traversed through {len(self.state.cleared_room_hashes)} distinct levels of local commit history.")

        summary.append(" ".join(narrative_parts))
        summary.append("-" * 60)
        summary.append("\033[1;35mTimeline of Achievements:\033[0m")

        if self.state.chronicle_entries:
            for entry in self.state.chronicle_entries[-10:]: # Limit to last 10 entries
                summary.append(f"  {entry}")
        else:
            summary.append("  * Walked the silent trails of the branch history.")

        summary.append("-" * 60)
        summary.append("\033[1;32mEngineering Recommendations for next session:\033[0m")
        summary.append("  - Keep the working directory clean of loose changes to avoid uncommitted state quests.")
        summary.append("  - Prioritize resolving linter and compiler-error entities before branching forward.")

        return "\n".join(summary)
