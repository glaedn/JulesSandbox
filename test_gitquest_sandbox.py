import unittest
from gitquest.scenarios.definitions import load_scenario, SCENARIOS
from gitquest.scenarios.tutorials import load_tutorial, TUTORIALS
from gitquest.engine.encounters import GameEngine, DungeonRoom
from gitquest.interfaces.terminal import TerminalInterface

class TestGitQuestSandbox(unittest.TestCase):

    def test_scenarios_exist_and_load(self):
        """Verify all scenario definitions exist and load correct DAG structures."""
        self.assertGreater(len(SCENARIOS), 0)
        for sid in SCENARIOS:
            commits = load_scenario(sid)
            self.assertIsInstance(commits, list)
            self.assertGreater(len(commits), 0)
            # Check basic structure of a commit
            c = commits[0]
            self.assertIn("hash", c)
            self.assertIn("short_hash", c)
            self.assertIn("parents", c)
            self.assertIn("subject", c)
            self.assertIn("type", c)

    def test_tutorials_exist_and_load(self):
        """Verify all tutorial definitions exist and load correct structures."""
        self.assertGreater(len(TUTORIALS), 0)
        for tid in TUTORIALS:
            commits = load_tutorial(tid)
            self.assertIsInstance(commits, list)
            self.assertGreater(len(commits), 0)
            c = commits[0]
            self.assertIn("hash", c)
            self.assertIn("short_hash", c)
            self.assertIn("parents", c)
            self.assertIn("subject", c)
            self.assertIn("type", c)

    def test_engine_initialization_with_simulated_commits(self):
        """Verify GameEngine initializes correctly with custom simulated DAGs."""
        scenario_commits = load_scenario("2") # Junior's Rebase Catastrophe
        engine = GameEngine(commits=scenario_commits)
        self.assertEqual(len(engine.commits), len(scenario_commits))
        # Player should spawn correctly in the first room (oldest commit)
        self.assertEqual(engine.current_hash, scenario_commits[-1]["hash"])
        room = engine.get_current_room()
        self.assertIsInstance(room, DungeonRoom)
        self.assertEqual(room.commit["hash"], engine.current_hash)

    def test_simulated_stash_tutorial_quest(self):
        """Verify the Stash Tutorial Quest compiles and validates on player stash."""
        # Load stash tutorial (Lesson 1)
        commits = load_tutorial("1")
        game = TerminalInterface(campaign_choice="5", custom_commits=commits)

        self.assertIsNotNone(game.active_quest)
        self.assertEqual(game.active_quest.id, "tutorial_stash")
        self.assertEqual(game.active_quest.status, "Active")

        # Simulate player stashing (pressing S)
        game.play_turn("S")
        self.assertIsNotNone(game.state.stash_snapshot)

        # Confirm quest completes
        self.assertEqual(game.active_quest.status, "Completed")
        self.assertIn("tutorial_stash", game.state.completed_quest_ids)

    def test_simulated_amend_tutorial_quest(self):
        """Verify the Amend Tutorial Quest compiles and validates on commit amend."""
        # Load amend tutorial (Lesson 2)
        commits = load_tutorial("2")
        game = TerminalInterface(campaign_choice="5", custom_commits=commits)

        self.assertEqual(game.active_quest.id, "tutorial_amend")
        self.assertEqual(game.active_quest.status, "Active")

        # Give player the '--amend' item
        player = game.engine.player
        player.inventory.append("git commit --amend")
        player.last_chest_loot = {
            "name": "Normal PR",
            "type": "weapon",
            "value": 1,
            "gold": 5
        }

        # Play C to amend
        game.play_turn("C")
        self.assertIn("Amended", player.weapon["name"])

        # Confirm quest completes
        self.assertEqual(game.active_quest.status, "Completed")

    def test_simulated_checkout_tutorial_quest(self):
        """Verify the Checkout Tutorial Quest compiles and validates on role checkout."""
        # Load checkout tutorial (Lesson 3)
        commits = load_tutorial("3")
        game = TerminalInterface(campaign_choice="5", custom_commits=commits)

        self.assertEqual(game.active_quest.id, "tutorial_checkout")
        self.assertEqual(game.active_quest.status, "Active")

        # Swap branch role (press B)
        game.play_turn("B")
        self.assertEqual(game.engine.player.role, "Frontend Dev")

        # Confirm quest completes
        self.assertEqual(game.active_quest.status, "Completed")

    def test_simulated_merge_tutorial_quest(self):
        """Verify the Merge Tutorial Quest compiles and validates when conflict pillars are destroyed."""
        # Load merge tutorial (Lesson 4)
        commits = load_tutorial("4")
        game = TerminalInterface(campaign_choice="5", custom_commits=commits)

        self.assertEqual(game.active_quest.id, "tutorial_merge")
        self.assertEqual(game.active_quest.status, "Active")

        # Find the merge conflict room (commit 1 is merge)
        # Note: In Lesson 4, commit 0 is "feat", commit 1 is "merge".
        # We start at commit 0 (oldest). Let's portal forward to the merge room.
        game.engine.current_hash = commits[0]["hash"] # force merge room
        # Wait, let's just force current_hash to the merge commit (index 1)
        game.engine.current_hash = commits[1]["hash"]
        room = game.engine.get_current_room()

        # Confirm pillars exist
        has_pillars = any(e.name in ["HEAD Pillar", "Incoming Pillar"] for e in room.enemies)
        self.assertTrue(has_pillars)

        # Clear pillars
        room.enemies = [e for e in room.enemies if e.name not in ["HEAD Pillar", "Incoming Pillar"]]

        # Run validation check
        game.check_active_quest_validation()
        self.assertEqual(game.active_quest.status, "Completed")

if __name__ == "__main__":
    unittest.main()
