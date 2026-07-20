class Quest:
    def __init__(self, qid, source, title, description, target_paths, objective, completion_evidence, reward_xp=25, reward_gold=10, status="Active"):
        self.id = qid
        self.source = source  # "Uncommitted Changes", "TODOs", "Failed Tests"
        self.title = title
        self.description = description
        self.target_paths = target_paths
        self.objective = objective
        self.completion_evidence = completion_evidence
        self.reward_xp = reward_xp
        self.reward_gold = reward_gold
        self.status = status

class QuestCompiler:
    def compile_quests(self, git_cli, diagnostics, test_runner):
        """Compiles real-world repository signals into structured gameplay quests."""
        quests = []

        # 1. Compile Quests from Uncommitted Changes
        uncommitted = git_cli.get_uncommitted_files()
        if uncommitted:
            # Group paths
            paths = [item["path"] for item in uncommitted]
            quests.append(Quest(
                qid="quest_uncommitted",
                source="Uncommitted Changes",
                title="Consolidate the Stage Area",
                description="You have loose modifications in the working tree. Commit or stash them!",
                target_paths=paths,
                objective="Stage and commit all loose modifications.",
                completion_evidence="Working tree is clean.",
                reward_xp=30,
                reward_gold=15
            ))

        # 2. Compile Quests from TODOs / FIXMEs
        todos = diagnostics.scan_todos()
        if todos:
            # Group by file
            file_to_todos = {}
            for t in todos:
                file_to_todos.setdefault(t["file"], []).append(t)

            # Select first 2 files with TODOs to generate concrete quests
            for file_path, file_todos in list(file_to_todos.items())[:2]:
                short_name = file_path.split("/")[-1]
                quests.append(Quest(
                    qid=f"quest_todo_{short_name}",
                    source="TODOs",
                    title=f"Resolve warnings in {short_name}",
                    description=f"Unresolved comments found: '{file_todos[0]['content']}'",
                    target_paths=[file_path],
                    objective=f"Clear all TODO/FIXME/XXX markers inside {file_path}.",
                    completion_evidence=f"Zero TODO/FIXME markers in {file_path}",
                    reward_xp=40,
                    reward_gold=20
                ))

        # 3. Compile Quests from Failing Tests
        test_results = test_runner.discover_and_run_tests()
        failing_tests = [tr for tr in test_results if not tr["passed"]]
        for ft in failing_tests:
            short_name = ft["test_file"].split("/")[-1]
            quests.append(Quest(
                qid=f"quest_test_{short_name}",
                source="Failed Tests",
                title=f"Repair broken pipeline: {short_name}",
                description="A vital verification spec is broken. Investigate and repair!",
                target_paths=[ft["test_file"]],
                objective=f"Fix execution of {ft['test_file']} until it passes cleanly.",
                completion_evidence=f"Test file {ft['test_file']} passes.",
                reward_xp=50,
                reward_gold=25
            ))

        # Fallback Default Quest if repository is completely clean & perfect
        if not quests:
            quests.append(Quest(
                qid="quest_stewardship",
                source="Stewardship",
                title="Documentation Crusade",
                description="The realm is pristine. Ensure that documentation standards are met.",
                target_paths=["README.md"],
                objective="Inspect README.md and write a new commit explaining latest updates.",
                completion_evidence="A new commit is pushed on the active branch.",
                reward_xp=20,
                reward_gold=10
            ))

        return quests

    def verify_quest_completion(self, quest, git_cli, diagnostics, test_runner):
        """Verifies if the player has produced the necessary real-world evidence to complete the quest."""
        if quest.status == "Completed":
            return True

        if quest.id == "quest_uncommitted":
            # Completed if git status --porcelain is empty
            files = git_cli.get_uncommitted_files()
            # If the only modified files are non-tracked temp/cache or empty, count as complete
            return len(files) == 0

        elif quest.id.startswith("quest_todo_"):
            # Check if diagnostics still returns any TODOs for target path
            target_path = quest.target_paths[0]
            all_todos = diagnostics.scan_todos()
            target_todos = [t for t in all_todos if t["file"] == target_path]
            return len(target_todos) == 0

        elif quest.id.startswith("quest_test_"):
            # Check if the specific test file passes now
            target_path = quest.target_paths[0]
            results = test_runner.discover_and_run_tests()
            for r in results:
                if r["test_file"] == target_path:
                    return r["passed"]
            return False

        elif quest.id == "quest_stewardship":
            # For the fallback default, check if we have any clean status
            return True

        return False
