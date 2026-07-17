import unittest
from gitquest_parser import parse_git_history
from gitquest_engine import GameEngine, DungeonRoom, Enemy, Player

class TestGitQuest(unittest.TestCase):

    def test_git_parser(self):
        commits = parse_git_history()
        self.assertIsInstance(commits, list)
        if commits:
            commit = commits[0]
            self.assertIn("hash", commit)
            self.assertIn("parents", commit)
            self.assertIn("author", commit)
            self.assertIn("timestamp", commit)
            self.assertIn("subject", commit)
            self.assertIn("type", commit)

    def test_player_init(self):
        player = Player("TestDev")
        self.assertEqual(player.name, "TestDev")
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
        # Check that it generated enemies for fix type
        self.assertGreater(len(room.enemies), 0)
        self.assertEqual(room.enemies[0].symbol, "B") # Should contain basic bug enemy

    def test_game_engine_init(self):
        engine = GameEngine()
        self.assertIsNotNone(engine.player)
        self.assertGreater(len(engine.rooms), 0)
        self.assertIn(engine.current_hash, engine.rooms)

    def test_movement_and_combat(self):
        engine = GameEngine()
        room = engine.get_current_room()

        # Manually clear obstacles and enemies to test movement
        room.enemies = []
        for y in range(room.height):
            for x in range(room.width):
                if room.grid[y][x] != "#" and room.grid[y][x] != "<" and room.grid[y][x] != ">":
                    room.grid[y][x] = " "

        engine.player.x = 4
        engine.player.y = 4

        # Test basic move successful
        result = engine.move_player(1, 0)
        self.assertEqual(result, "SUCCESS")
        self.assertEqual(engine.player.x, 5)
        self.assertEqual(engine.player.y, 4)

        # Test walking into wall
        room.grid[4][6] = "#"
        result = engine.move_player(1, 0)
        self.assertEqual(result, "WALL")
        self.assertEqual(engine.player.x, 5)
        self.assertEqual(engine.player.y, 4)

if __name__ == "__main__":
    unittest.main()
