import unittest
from gitquest.domain.state import GameState
from gitquest.domain.events import EventBus, DamageApplied, QuestCompleted
from gitquest.adapters.git_cli import GitCLIAdapter
from gitquest.adapters.diagnostics import DiagnosticsAdapter
from gitquest.analysis.quest_compiler import QuestCompiler, Quest

class TestGitQuestModular(unittest.TestCase):

    def test_game_state_snapshot_clone_restore(self):
        """Test unified GameState deepcopy cloning and restoration (stash)."""
        state = GameState("TestDev")
        state.hp = 50
        state.gold = 35
        state.weapon = {"name": "Master PR", "bonus": 5}
        state.cleared_room_hashes.add("commit_base")

        # Take Snapshot
        snapshot = state.clone()
        self.assertEqual(snapshot.hp, 50)
        self.assertEqual(snapshot.gold, 35)
        self.assertEqual(snapshot.weapon["name"], "Master PR")
        self.assertIn("commit_base", snapshot.cleared_room_hashes)

        # Modify active state
        state.hp = 10
        state.gold = 0
        state.weapon = {"name": "Punch", "bonus": 0}
        state.cleared_room_hashes.clear()

        # Restore
        state.restore_from(snapshot)
        self.assertEqual(state.hp, 50)
        self.assertEqual(state.gold, 35)
        self.assertEqual(state.weapon["name"], "Master PR")
        self.assertIn("commit_base", state.cleared_room_hashes)

    def test_event_driven_bus(self):
        """Test subscribing and publishing events on EventBus."""
        bus = EventBus()
        captured_events = []

        def on_damage(ev):
            captured_events.append(ev)

        bus.subscribe(DamageApplied, on_damage)

        # Publish
        bus.publish(DamageApplied("Player", "Bug", 15, 10))
        self.assertEqual(len(captured_events), 1)
        self.assertEqual(captured_events[0].attacker_name, "Player")
        self.assertEqual(captured_events[0].damage, 15)

    def test_quest_compiler_generation(self):
        """Test QuestCompiler generates correct fallback quests on empty parameters."""
        class MockGitCLI:
            def get_uncommitted_files(self): return []
        class MockDiagnostics:
            def scan_todos(self): return []
        class MockTestRunner:
            def discover_and_run_tests(self): return []

        compiler = QuestCompiler()
        quests = compiler.compile_quests(MockGitCLI(), MockDiagnostics(), MockTestRunner())
        self.assertGreater(len(quests), 0)
        self.assertEqual(quests[0].id, "quest_stewardship") # Fallback quest

    def test_quest_compiler_real_signals(self):
        """Test QuestCompiler compiles specific quests based on code signal presence."""
        class MockGitCLI:
            def get_uncommitted_files(self):
                return [{"path": "main.py", "status": "M"}]
        class MockDiagnostics:
            def scan_todos(self):
                return [{"file": "main.py", "line_number": 5, "content": "TODO: fix leak", "severity": "Medium"}]
        class MockTestRunner:
            def discover_and_run_tests(self):
                return [{"test_file": "test_auth.py", "passed": False, "output": "Failed"}]

        compiler = QuestCompiler()
        quests = compiler.compile_quests(MockGitCLI(), MockDiagnostics(), MockTestRunner())

        qids = [q.id for q in quests]
        self.assertIn("quest_uncommitted", qids)
        self.assertIn("quest_todo_main.py", qids)
        self.assertIn("quest_test_test_auth.py", qids)

    def test_quest_verification_proof(self):
        """Test verifying active quest validation proofs successfully."""
        compiler = QuestCompiler()

        # Create a TODO quest
        quest = Quest(
            qid="quest_todo_main.py",
            source="TODOs",
            title="Resolve warnings in main.py",
            description="Clear comments",
            target_paths=["main.py"],
            objective="Clear comments",
            completion_evidence="Zero comments"
        )

        class MockGitCLI:
            def get_uncommitted_files(self): return []

        # 1. Verification fails when TODO is still present
        class MockDiagnosticsStillHasTODO:
            def scan_todos(self):
                return [{"file": "main.py", "line_number": 5, "content": "TODO: fix", "severity": "Medium"}]

        self.assertFalse(compiler.verify_quest_completion(
            quest, MockGitCLI(), MockDiagnosticsStillHasTODO(), None
        ))

        # 2. Verification passes when TODO is cleared (scan returns empty)
        class MockDiagnosticsCleared:
            def scan_todos(self):
                return []

        self.assertTrue(compiler.verify_quest_completion(
            quest, MockGitCLI(), MockDiagnosticsCleared(), None
        ))

if __name__ == "__main__":
    unittest.main()
