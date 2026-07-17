import subprocess
import sys

def run_git_command(args):
    """Runs a git command and returns output, or None on failure."""
    try:
        result = subprocess.run(
            ["git"] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def parse_git_history(limit=50):
    """Parses git commit logs to build our game levels database.
    Limits the history to prevent huge startup hangs on large repositories.
    """
    # Format: hash|parents|author|timestamp|subject
    log_format = "%H|%P|%an|%at|%s"
    output = run_git_command(["log", f"-n", str(limit), "--all", f"--pretty=format:{log_format}"])
    if not output:
        # Fallback to no --all if it's a completely fresh repo or has issues
        output = run_git_command(["log", f"-n", str(limit), f"--pretty=format:{log_format}"])
        if not output:
            return []

    # Efficiently gather modified files per commit in a single pass
    files_per_commit = {}
    files_output = run_git_command(["log", f"-n", str(limit), "--all", "--name-only", "--pretty=format:COMMIT:%H"])
    if not files_output:
        files_output = run_git_command(["log", f"-n", str(limit), "--name-only", "--pretty=format:COMMIT:%H"])

    if files_output:
        current_hash = None
        for line in files_output.split("\n"):
            line = line.strip()
            if not line:
                continue
            if line.startswith("COMMIT:"):
                current_hash = line.split(":", 1)[1]
                files_per_commit[current_hash] = []
            elif current_hash:
                files_per_commit[current_hash].append(line)

    # Let's also resolve branch decorations/names using git show-ref or git log --decorate
    ref_decorations = {}
    decorations_output = run_git_command(["log", f"-n", str(limit), "--all", "--pretty=format:%H|%D"])
    if not decorations_output:
        decorations_output = run_git_command(["log", f"-n", str(limit), "--pretty=format:%H|%D"])

    if decorations_output:
        for line in decorations_output.split("\n"):
            line = line.strip()
            if not line or "|" not in line:
                continue
            chash, dec = line.split("|", 1)
            if dec:
                # e.g., "HEAD -> main, tag: v1.0, origin/main"
                parts = [p.strip() for p in dec.split(",") if p.strip()]
                branches = []
                for p in parts:
                    if p.startswith("HEAD -> "):
                        branches.append(p.replace("HEAD -> ", ""))
                    elif p.startswith("tag: "):
                        continue
                    elif "/" in p: # remote
                        branches.append(p)
                    else:
                        branches.append(p)
                if branches:
                    ref_decorations[chash] = branches

    commits = []
    lines = output.split("\n")
    seen_hashes = set()
    for line in lines:
        if not line.strip():
            continue
        parts = line.split("|", 4)
        if len(parts) < 5:
            continue

        commit_hash, parents_str, author, timestamp, subject = parts
        if commit_hash in seen_hashes:
            continue
        seen_hashes.add(commit_hash)
        parents = parents_str.split() if parents_str else []

        # Retrieve modified files from our single-pass dictionary
        modified_files = files_per_commit.get(commit_hash, [])

        # Retrieve branches/refs for this commit
        branches = ref_decorations.get(commit_hash, [])

        # Deduce commit type (feat, fix, docs, refactor, chore, test, merge, other)
        subject_lower = subject.lower()
        if "merge" in subject_lower or len(parents) > 1:
            commit_type = "merge"
        elif subject_lower.startswith("feat") or "feature" in subject_lower:
            commit_type = "feat"
        elif subject_lower.startswith("fix") or "bug" in subject_lower or "error" in subject_lower:
            commit_type = "fix"
        elif subject_lower.startswith("docs") or "doc" in subject_lower or "readme" in subject_lower:
            commit_type = "docs"
        elif subject_lower.startswith("refactor") or "clean" in subject_lower or "style" in subject_lower:
            commit_type = "refactor"
        elif subject_lower.startswith("test") or "spec" in subject_lower:
            commit_type = "test"
        else:
            commit_type = "chore"

        commits.append({
            "hash": commit_hash,
            "short_hash": commit_hash[:7],
            "parents": parents,
            "branches": branches,
            "author": author,
            "timestamp": int(timestamp) if timestamp.isdigit() else 0,
            "subject": subject,
            "modified_files": modified_files,
            "type": commit_type
        })

    return commits

if __name__ == "__main__":
    print("Testing Git Parser...")
    commits = parse_git_history()
    print(f"Parsed {len(commits)} commits.")
    for idx, c in enumerate(commits):
        print(f"[{idx}] {c['short_hash']} by {c['author']} ({c['type']}): {c['subject']}")
        print(f"    Parents: {c['parents']}")
        print(f"    Branches: {c['branches']}")
        print(f"    Files: {c['modified_files']}")
