"""
GitQuest Sandbox Scenario Definitions
Pre-crafted simulated Git DAGs with rich narrative lore, diverse commit structures,
and customized challenges that don't alter the user's real repository.
"""

def generate_legacy_monolith():
    """
    Scenario 1: The Legacy Monolith
    A deep, linear, winding codebase built years ago. It has extensive historical logs,
    spaghetti refactors, and numerous lingering bugs (fix commits) that need squashing.
    """
    return [
        {
            "hash": "init0000000000000000000000000000000001",
            "short_hash": "init001",
            "parents": [],
            "branches": ["main"],
            "author": "The Founder",
            "timestamp": 1100000000,
            "subject": "Initial commit of legacy code",
            "modified_files": ["main.py", "Makefile", "utils.py"],
            "type": "feat"
        },
        {
            "hash": "doc00000000000000000000000000000000001",
            "short_hash": "doc0001",
            "parents": ["init0000000000000000000000000000000001"],
            "branches": [],
            "author": "Unknown Intern",
            "timestamp": 1150000000,
            "subject": "docs: add legacy API manuals",
            "modified_files": ["README.md", "API.md"],
            "type": "docs"
        },
        {
            "hash": "fix00000000000000000000000000000000001",
            "short_hash": "fix0001",
            "parents": ["doc00000000000000000000000000000000001"],
            "branches": [],
            "author": "Desperate Senior",
            "timestamp": 1200000000,
            "subject": "fix: fix severe memory leaks in legacy server loops",
            "modified_files": ["server.py", "utils.py"],
            "type": "fix"
        },
        {
            "hash": "ref00000000000000000000000000000000001",
            "short_hash": "ref0001",
            "parents": ["fix00000000000000000000000000000000001"],
            "branches": [],
            "author": "Architect Al",
            "timestamp": 1250000000,
            "subject": "refactor: restructure spaghetti routing module",
            "modified_files": ["routing.py"],
            "type": "refactor"
        },
        {
            "hash": "fix00000000000000000000000000000000002",
            "short_hash": "fix0002",
            "parents": ["ref00000000000000000000000000000000001"],
            "branches": [],
            "author": "Angry SRE",
            "timestamp": 1300000000,
            "subject": "fix: patch socket connection leaks under high load",
            "modified_files": ["network.py", "routing.py"],
            "type": "fix"
        },
        {
            "hash": "feat00000000000000000000000000000000001",
            "short_hash": "feat001",
            "parents": ["fix00000000000000000000000000000000002"],
            "branches": ["HEAD"],
            "author": "Lead Maintainer",
            "timestamp": 1350000000,
            "subject": "feat: prepare production release candidate v1.0",
            "modified_files": ["release_notes.md", "setup.py"],
            "type": "feat"
        }
    ]

def generate_junior_rebase_catastrophe():
    """
    Scenario 2: The Junior's Rebase Catastrophe
    A chaotic DAG featuring split parallel branches.
    The Junior developer tried to rebase multiple feature branches without coordination,
    leaving a labyrinth of divergent parents/children portals!
    """
    return [
        {
            "hash": "base0000000000000000000000000000000001",
            "short_hash": "base001",
            "parents": [],
            "branches": ["main"],
            "author": "Good Dev",
            "timestamp": 1700000000,
            "subject": "Setup stable base framework",
            "modified_files": ["base.py"],
            "type": "feat"
        },
        # Branch 1: feature-auth (diverging from base001)
        {
            "hash": "auth0000000000000000000000000000000001",
            "short_hash": "auth001",
            "parents": ["base0000000000000000000000000000000001"],
            "branches": ["feature-auth"],
            "author": "Junior Joe",
            "timestamp": 1701000000,
            "subject": "feat: add user login endpoint",
            "modified_files": ["auth.py"],
            "type": "feat"
        },
        # Branch 2: feature-payment (also diverging from base001)
        {
            "hash": "pay00000000000000000000000000000000001",
            "short_hash": "pay0001",
            "parents": ["base0000000000000000000000000000000001"],
            "branches": ["feature-payment"],
            "author": "Junior Jack",
            "timestamp": 1702000000,
            "subject": "feat: integrate external checkout API",
            "modified_files": ["payment.py"],
            "type": "feat"
        },
        # Branch 1 continues
        {
            "hash": "auth0000000000000000000000000000000002",
            "short_hash": "auth002",
            "parents": ["auth0000000000000000000000000000000001"],
            "branches": [],
            "author": "Junior Joe",
            "timestamp": 1703000000,
            "subject": "fix: crash when password is null",
            "modified_files": ["auth.py"],
            "type": "fix"
        },
        # Branch 2 continues
        {
            "hash": "pay00000000000000000000000000000000002",
            "short_hash": "pay0002",
            "parents": ["pay00000000000000000000000000000000001"],
            "branches": [],
            "author": "Junior Jack",
            "timestamp": 1704000000,
            "subject": "docs: document payment webhooks",
            "modified_files": ["payment.md"],
            "type": "docs"
        },
        # Rebase Disaster: A merge of auth002 and pay002 with double parents
        {
            "hash": "merge0000000000000000000000000000000001",
            "short_hash": "mrg0001",
            "parents": ["auth0000000000000000000000000000000002", "pay00000000000000000000000000000000002"],
            "branches": ["HEAD"],
            "author": "Clueless Junior",
            "timestamp": 1705000000,
            "subject": "Merge branch 'feature-auth' and 'feature-payment' into main with force rebase",
            "modified_files": ["auth.py", "payment.py", "base.py"],
            "type": "merge"
        }
    ]

def generate_production_outage_crisis():
    """
    Scenario 3: The Production Outage Crisis
    High-intensity, high-risk scenario. The live application is down.
    The timeline is littered with compiler errors and quick fixes.
    You must find and destroy the bugs quickly before resources drain.
    """
    return [
        {
            "hash": "stable000000000000000000000000000000001",
            "short_hash": "stb0001",
            "parents": [],
            "branches": ["v2.0-tag"],
            "author": "Calm SRE",
            "timestamp": 1800000000,
            "subject": "Stable production release v2.0",
            "modified_files": ["app.py", "database.py"],
            "type": "feat"
        },
        {
            "hash": "fail00000000000000000000000000000000001",
            "short_hash": "fail001",
            "parents": ["stable000000000000000000000000000000001"],
            "branches": [],
            "author": "Midnight Hacker",
            "timestamp": 1801000000,
            "subject": "feat: introduce experimental fast routing",
            "modified_files": ["app.py", "router.py"],
            "type": "feat"
        },
        {
            "hash": "fail00000000000000000000000000000000002",
            "short_hash": "fail002",
            "parents": ["fail00000000000000000000000000000000001"],
            "branches": [],
            "author": "Panic Dev",
            "timestamp": 1802000000,
            "subject": "fix: critical crash in DB transaction pool",
            "modified_files": ["database.py"],
            "type": "fix"
        },
        {
            "hash": "fail00000000000000000000000000000000003",
            "short_hash": "fail003",
            "parents": ["fail00000000000000000000000000000000002"],
            "branches": ["HEAD"],
            "author": "Hero Engineer",
            "timestamp": 1803000000,
            "subject": "fix: disable experimental routing, patch DB retry limits",
            "modified_files": ["app.py", "database.py"],
            "type": "fix"
        }
    ]

def generate_epic_merge_conflict_war():
    """
    Scenario 4: The Epic Merge Conflict War
    A heavy dungeon comprised of multiple merge commits in sequence,
    each with Merge Conflict bosses guarded by HEAD and Incoming branch pillars!
    """
    return [
        {
            "hash": "base_war000000000000000000000000000001",
            "short_hash": "base001",
            "parents": [],
            "branches": ["main"],
            "author": "General Dev",
            "timestamp": 1900000000,
            "subject": "Begin the construction of monolithic fortresses",
            "modified_files": ["castle.py"],
            "type": "feat"
        },
        {
            "hash": "branch_a00000000000000000000000000000001",
            "short_hash": "bra0001",
            "parents": ["base_war000000000000000000000000000001"],
            "branches": ["fortress-alpha"],
            "author": "Knight Alpha",
            "timestamp": 1901000000,
            "subject": "feat: add double-thick defense walls",
            "modified_files": ["castle.py", "alpha_wall.py"],
            "type": "feat"
        },
        {
            "hash": "branch_b00000000000000000000000000000001",
            "short_hash": "brb0001",
            "parents": ["base_war000000000000000000000000000001"],
            "branches": ["fortress-beta"],
            "author": "Knight Beta",
            "timestamp": 1902000000,
            "subject": "feat: add fire-breathing defense turrets",
            "modified_files": ["castle.py", "beta_turret.py"],
            "type": "feat"
        },
        {
            "hash": "merge_war_100000000000000000000000000001",
            "short_hash": "mrg_war",
            "parents": ["branch_a00000000000000000000000000000001", "branch_b00000000000000000000000000000001"],
            "branches": ["HEAD"],
            "author": "Grand Arbitrator",
            "timestamp": 1903000000,
            "subject": "Merge branch 'fortress-alpha' and 'fortress-beta' - Resolve Castle War",
            "modified_files": ["castle.py"],
            "type": "merge"
        }
    ]

SCENARIOS = {
    "1": {
        "name": "The Legacy Monolith (Long, linear, lore-heavy dungeon)",
        "generator": generate_legacy_monolith
    },
    "2": {
        "name": "The Junior's Rebase Catastrophe (Highly branchy maze, parallel portals)",
        "generator": generate_junior_rebase_catastrophe
    },
    "3": {
        "name": "The Production Outage Crisis (High intensity, timers, compile bugs)",
        "generator": generate_production_outage_crisis
    },
    "4": {
        "name": "The Epic Merge Conflict War (Bosses and shield pillars battleground)",
        "generator": generate_epic_merge_conflict_war
    }
}

def load_scenario(choice_id):
    """Loads a simulated Git DAG list for the chosen scenario ID."""
    if choice_id in SCENARIOS:
        return SCENARIOS[choice_id]["generator"]()
    return generate_legacy_monolith()
