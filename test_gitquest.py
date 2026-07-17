import unittest
from gitquest_parser import parse_git_history
from gitquest_engine import GameEngine, DungeonRoom, Enemy, Player
from gitquest import TerminalGame

class TestGitQuest(unittest.TestCase):

    def test_git_parser(self):
        commits = parse_git_history()
        self.assertIsInstance(commits, list)
        if commits:
            commit = commits[0]
            self.assertIn("hash", commit)
            self.assertIn("parents", commit)
            self.assertIn("branches", commit)
            self.assertIn("author", commit)
            self.assertIn("timestamp", commit)
            self.assertIn("subject", commit)
            self.assertIn("type", commit)

    def test_player_init(self):
        player = Player("TestDev")
        self.assertEqual(player.name, "TestDev")
        self.assertEqual(player.role, "Backend Dev")
        self.assertEqual(player.hp, player.max_hp)
        self.assertEqual(player.level, 1)
        self.assertEqual(player.xp, 0)
        self.assertEqual(player.gold, 0)

    def test_player_heal(self):
        player = Player()
        player.hp = 10
        player.heal(50)
        self.assertEqual(player.hp, 60)
        player.heal(100)
        self.assertEqual(player.hp, player.max_hp)

    def test_player_level_up(self):
        player = Player()
        initial_attack = player.attack
        leveled = player.gain_xp(100)
        self.assertTrue(leveled)
        self.assertEqual(player.level, 2)
        self.assertGreater(player.attack, initial_attack)

    def test_player_checkout_role(self):
        player = Player()
        self.assertEqual(player.role, "Backend Dev")
        success, msg = player.checkout_role("Frontend Dev")
        self.assertTrue(success)
        self.assertEqual(player.role, "Frontend Dev")
        self.assertEqual(player.max_hp, 80)
        self.assertEqual(player.attack, 22)

        success2, msg2 = player.checkout_role("Frontend Dev")
        self.assertFalse(success2) # Already on branch

    def test_git_stash_mechanic(self):
        engine = GameEngine()
        engine.player.gold = 50
        engine.player.hp = 90

        # Save state
        msg = engine.stash_save()
        self.assertIn("Stashed", msg)
        self.assertIsNotNone(engine.player.stash_data)

        # Modify state
        engine.player.gold = 1000
        engine.player.hp = 10

        # Restore state via pop
        restored = engine.stash_pop()
        self.assertTrue(restored)
        self.assertEqual(engine.player.gold, 50)
        self.assertEqual(engine.player.hp, 90)

    def test_git_commit_amend_mechanic(self):
        engine = GameEngine()
        engine.player.gold = 10
        engine.player.last_chest_loot = {
            "name": "Standard PR",
            "type": "weapon",
            "value": 2,
            "gold": 5
        }

        # Amend without item
        engine.player.inventory = []
        res = engine.amend_chest_loot()
        self.assertIn("No '--amend' item", res)

        # Amend with item
        engine.player.inventory = ["git commit --amend"]
        res = engine.amend_chest_loot()
        self.assertIn("Amended!", res)
        self.assertNotIn("git commit --amend", engine.player.inventory)
        self.assertGreater(engine.player.weapon["bonus"], 2) # Guaranteed improvement!

    def test_merge_conflict_boss_shield(self):
        mock_commit = {
            "hash": "abcdef1234567890abcdef1234567890abcdef12",
            "parents": ["parent1", "parent2"],
            "author": "Tester",
            "timestamp": 123456,
            "subject": "Merge branch main into develop",
            "modified_files": ["main.py"],
            "type": "merge"
        }
        room = DungeonRoom(mock_commit)
        # Check that we generated the Boss, HEAD Pillar, and Incoming Pillar
        has_boss = any(e.name == "Merge Conflict Boss" for e in room.enemies)
        has_head = any(e.name == "HEAD Pillar" for e in room.enemies)
        has_incoming = any(e.name == "Incoming Pillar" for e in room.enemies)

        self.assertTrue(has_boss)
        self.assertTrue(has_head)
        self.assertTrue(has_incoming)

        # Test boss damage shield in engine
        engine = GameEngine()
        engine.rooms[engine.current_hash] = room
        boss = next(e for e in room.enemies if e.name == "Merge Conflict Boss")

        # Attack while pillars exist
        result = engine.attack_enemy(boss)
        self.assertIn("Your attack bounce off!", result)
        self.assertEqual(boss.hp, boss.max_hp) # No damage dealt

        # Destroy HEAD Pillar to simulate resolving conflict
        head_pillar = next(e for e in room.enemies if e.name == "HEAD Pillar")
        res_destroy = engine.attack_enemy(head_pillar)
        self.assertIn("Pillar destroyed!", res_destroy)

        # Confirm both pillars got resolved/removed
        self.assertFalse(any(e.name in ["HEAD Pillar", "Incoming Pillar"] for e in room.enemies))

        # Attack boss now
        res_attack = engine.attack_enemy(boss)
        self.assertNotIn("Your attack bounce off!", res_attack)
        self.assertLess(boss.hp, boss.max_hp) # Damage is dealt successfully!

    def test_terminal_game_turn_flow(self):
        """Verify gameplay actions (movement vs stash/checkout) in terminal game loop."""
        game = TerminalGame()
        # Test movement
        game.engine.player.x = 4
        game.engine.player.y = 4

        # Clear obstacles for movement test
        room = game.engine.get_current_room()
        room.enemies = []
        for y in range(room.height):
            for x in range(room.width):
                if room.grid[y][x] != "#" and room.grid[y][x] != "<" and room.grid[y][x] != ">":
                    room.grid[y][x] = " "

        # 's' should move player DOWN (increase y)
        game.play_turn("s")
        self.assertEqual(game.engine.player.y, 5)
        self.assertIsNone(game.engine.player.stash_data) # S was not stashed

        # 'S' (Shift+s) should stash player state, NOT move
        game.play_turn("S")
        self.assertEqual(game.engine.player.y, 5) # y remains same
        self.assertIsNotNone(game.engine.player.stash_data) # stash data is saved!

        # 'B' (Shift+b) should checkout role/class
        self.assertEqual(game.engine.player.role, "Backend Dev")
        game.play_turn("B")
        self.assertEqual(game.engine.player.role, "Frontend Dev")

    def test_dungeon_room_generation(self):
        mock_commit = {
            "hash": "abcdef1234567890abcdef1234567890abcdef12",
            "parents": [],
            "author": "Tester",
            "timestamp": 123456,
            "subject": "fix the severe memory leak",
            "modified_files": ["main.py", "test.py"],
            "type": "fix"
        }
        room = DungeonRoom(mock_commit)
        self.assertGreater(len(room.enemies), 0)
        self.assertEqual(room.enemies[0].symbol, "B")

    def test_game_engine_init(self):
        engine = GameEngine()
        self.assertIsNotNone(engine.player)
        self.assertGreater(len(engine.rooms), 0)
        self.assertIn(engine.current_hash, engine.rooms)

    def test_movement_and_combat(self):
        engine = GameEngine()
        room = engine.get_current_room()

        room.enemies = []
        for y in range(room.height):
            for x in range(room.width):
                if room.grid[y][x] != "#" and room.grid[y][x] != "<" and room.grid[y][x] != ">":
                    room.grid[y][x] = " "

        engine.player.x = 4
        engine.player.y = 4

        result = engine.move_player(1, 0)
        self.assertEqual(result, "SUCCESS")
        self.assertEqual(engine.player.x, 5)
        self.assertEqual(engine.player.y, 4)

        room.grid[4][6] = "#"
        result = engine.move_player(1, 0)
        self.assertEqual(result, "WALL")
        self.assertEqual(engine.player.x, 5)
        self.assertEqual(engine.player.y, 4)

if __name__ == "__main__":
    unittest.main()
