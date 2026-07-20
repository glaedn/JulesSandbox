class Event:
    pass

class DamageApplied(Event):
    def __init__(self, attacker_name, target_name, damage, remaining_hp):
        self.attacker_name = attacker_name
        self.target_name = target_name
        self.damage = damage
        self.remaining_hp = remaining_hp

class EnemyDefeated(Event):
    def __init__(self, enemy_name, xp_gained):
        self.enemy_name = enemy_name
        self.xp_gained = xp_gained

class PillarDestroyed(Event):
    def __init__(self, pillar_name):
        self.pillar_name = pillar_name

class ConflictResolved(Event):
    def __init__(self, commit_hash):
        self.commit_hash = commit_hash

class RoomCleared(Event):
    def __init__(self, commit_hash):
        self.commit_hash = commit_hash

class QuestCompleted(Event):
    def __init__(self, quest_id, title):
        self.quest_id = quest_id
        self.title = title

class EvidenceRecorded(Event):
    def __init__(self, key, description):
        self.key = key
        self.description = description

class EventBus:
    def __init__(self):
        self._listeners = {}

    def subscribe(self, event_class, callback):
        if event_class not in self._listeners:
            self._listeners[event_class] = []
        self._listeners[event_class].append(callback)

    def publish(self, event):
        event_class = type(event)
        if event_class in self._listeners:
            for cb in self._listeners[event_class]:
                cb(event)
