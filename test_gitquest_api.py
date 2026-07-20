import unittest
import json
from gitquest.contracts.requests import ActionRequest, ScanRepositoryRequest, CheckoutRequest
from gitquest.contracts.responses import EncounterResponse, ActionResponse
from gitquest.interfaces.api import GitQuestAPI

class TestGitQuestAPI(unittest.TestCase):

    def test_request_deserialization(self):
        """Test structured JSON request deserialization models."""
        # 1. ActionRequest
        json_action = '{"action": "w"}'
        req = ActionRequest.from_json(json_action)
        self.assertEqual(req.action, "w")

        # 2. ScanRepositoryRequest
        json_scan = '{"limit": 45}'
        scan_req = ScanRepositoryRequest.from_json(json_scan)
        self.assertEqual(scan_req.limit, 45)

        # 3. CheckoutRequest
        json_checkout = '{"target_branch": "Frontend Dev"}'
        checkout_req = CheckoutRequest.from_json(json_checkout)
        self.assertEqual(checkout_req.target_branch, "Frontend Dev")

    def test_response_serialization(self):
        """Test class-based structured response serialization to clean JSON."""
        # 1. EncounterResponse
        res = EncounterResponse(
            encounter_id="enc_12345",
            title="Divergent Features",
            status="needs_attention",
            nodes=[{"id": "test_1", "type": "test", "label": "Spec", "state": "failed", "technicalMessage": "failed"}],
            rewards={"reliability": 5, "clarity": 2, "harmony": 1}
        )
        serialized = res.to_json()
        data = json.loads(serialized)
        self.assertEqual(data["encounterId"], "enc_12345")
        self.assertEqual(data["title"], "Divergent Features")
        self.assertEqual(len(data["nodes"]), 1)
        self.assertEqual(data["rewards"]["reliability"], 5)

        # 2. ActionResponse
        act_res = ActionResponse(
            result="SUCCESS",
            message="You moved successfully",
            hp=100,
            gold=15,
            level=3,
            current_hash="abcde123"
        )
        serialized_act = act_res.to_json()
        act_data = json.loads(serialized_act)
        self.assertEqual(act_data["result"], "SUCCESS")
        self.assertEqual(act_data["message"], "You moved successfully")
        self.assertEqual(act_data["hp"], 100)
        self.assertEqual(act_data["current_hash"], "abcde123")

    def test_api_dispatcher(self):
        """Test API wrapper class initialization and action dispatching flows."""
        api = GitQuestAPI()

        # 1. Initialize encounter
        enc_response = api.initialize_encounter(limit=5)
        self.assertEqual(enc_response.title, "The Active Workspace Expedition")
        self.assertIsNotNone(api.engine)

        # 2. Dispatch a simple movement action
        action_json = '{"action": "w"}'
        act_response = api.dispatch_action(action_json)
        self.assertIn(act_response.result, ["SUCCESS", "COMBAT"])
        self.assertIsNotNone(act_response.message)
        self.assertEqual(act_response.level, 1)

if __name__ == "__main__":
    unittest.main()
