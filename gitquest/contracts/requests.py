import json

class ActionRequest:
    def __init__(self, action):
        self.action = action  # "w", "a", "s", "d", "1", "2", "3", "S", "C", "B"

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        return cls(action=data.get("action"))

class ScanRepositoryRequest:
    def __init__(self, limit=30):
        self.limit = limit

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        return cls(limit=data.get("limit", 30))

class CheckoutRequest:
    def __init__(self, target_branch):
        self.target_branch = target_branch

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        return cls(target_branch=data.get("target_branch"))
