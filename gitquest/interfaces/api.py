import json
from gitquest.engine.encounters import GameEngine
from gitquest.engine.repository import RepositoryScanner
from gitquest.engine.validation import DiagnosticsScanner, TestRunnerScanner
from gitquest.analysis.quest_compiler import QuestCompiler
from gitquest.contracts.requests import ActionRequest, ScanRepositoryRequest
from gitquest.contracts.responses import EncounterResponse, ActionResponse

class GitQuestAPI:
    def __init__(self):
        self.scanner = RepositoryScanner()
        self.diagnostics = DiagnosticsScanner()
        self.test_runner = TestRunnerScanner()
        self.compiler = QuestCompiler()
        self.engine = None

    def initialize_encounter(self, limit=30):
        """Initializes a new game engine snapshot and compiles active validation quests."""
        commits = self.scanner.scan_repository()
        self.engine = GameEngine(commits=commits)

        quests = self.compiler.compile_quests(self.scanner, self.diagnostics, self.test_runner)

        # Build structured contract nodes
        nodes = []
        for q in quests:
            nodes.append({
                "id": q.id,
                "type": q.source,
                "label": q.title,
                "state": "pending" if q.status == "Active" else "passed",
                "technicalMessage": q.description
            })

        response = EncounterResponse(
            encounter_id="enc_" + (self.engine.current_hash[:6] if self.engine.current_hash else "000000"),
            title="The Active Workspace Expedition",
            status="needs_attention" if any(q.status == "Active" for q in quests) else "validated",
            nodes=nodes,
            rewards={"reliability": 5, "clarity": 3, "harmony": 2}
        )
        return response

    def dispatch_action(self, action_request_json):
        """Dispatches an incoming JSON ActionRequest and returns an ActionResponse JSON."""
        if not self.engine:
            self.initialize_encounter()

        req = ActionRequest.from_json(action_request_json)
        player = self.engine.player

        # Execute turn in engine
        res = self.engine.move_player(0, 0) # Fallback turn action

        # Map WASD movements
        if req.action in ["w", "a", "s", "d"]:
            dx, dy = 0, 0
            if req.action == "w": dy = -1
            elif req.action == "s": dy = 1
            elif req.action == "a": dx = -1
            elif req.action == "d": dx = 1
            res = self.engine.move_player(dx, dy)

        elif req.action == "S":
            res = self.engine.stash_save()
        elif req.action == "C":
            res = self.engine.amend_chest_loot()
        elif req.action == "B":
            target = "Frontend Dev" if player.role == "Backend Dev" else "Backend Dev"
            success, msg = player.checkout_role(target)
            res = msg

        response = ActionResponse(
            result="SUCCESS" if "SUCCESS" in res or "LOOT" in res else "COMBAT",
            message=res,
            hp=player.hp,
            gold=player.gold,
            level=player.level,
            current_hash=self.engine.current_hash
        )
        return response
