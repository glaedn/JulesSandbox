import json

class EncounterResponse:
    def __init__(self, encounter_id, title, status, nodes, rewards):
        self.encounter_id = encounter_id
        self.title = title
        self.status = status  # "scanning", "ready", "needs_attention", "validated"
        self.nodes = nodes    # List of node dicts: {"id", "type", "label", "state", "technicalMessage"}
        self.rewards = rewards # Dict of rewards: {"reliability", "clarity", "harmony"}

    def to_json(self):
        return json.dumps({
            "encounterId": self.encounter_id,
            "title": self.title,
            "status": self.status,
            "nodes": self.nodes,
            "rewards": self.rewards
        })

class ActionResponse:
    def __init__(self, result, message, hp, gold, level, current_hash):
        self.result = result  # "SUCCESS", "COMBAT", "PORTAL_FORWARD", "PORTAL_BACK", "VICTORY"
        self.message = message
        self.hp = hp
        self.gold = gold
        self.level = level
        self.current_hash = current_hash

    def to_json(self):
        return json.dumps({
            "result": self.result,
            "message": self.message,
            "hp": self.hp,
            "gold": self.gold,
            "level": self.level,
            "current_hash": self.current_hash
        })
