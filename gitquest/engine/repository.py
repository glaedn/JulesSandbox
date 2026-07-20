import subprocess

def run_git(args):
    """Safely executes a git command in list format, returning stdout or empty string."""
    try:
        res = subprocess.run(
            ["git"] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return res.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""

class RepositoryScanner:
    def __init__(self, limit=30):
        self.limit = limit

    def get_uncommitted_files(self):
        """Returns a list of uncommitted/unstaged file statuses using git status --porcelain."""
        output = run_git(["status", "--porcelain"])
        if not output:
            return []
        files = []
        for line in output.split("\n"):
            line = line.strip()
            if line:
                parts = line.split(None, 1)
                if len(parts) == 2:
                    status, filepath = parts
                    files.append({"path": filepath, "status": status})
                else:
                    files.append({"path": line, "status": "??"})
        return files

    def get_current_branch(self):
        """Returns current branch name."""
        branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"])
        return branch if branch else "detached-HEAD"

    def scan_repository(self):
        """Parses git commit logs to build our game levels database.
        Limits the history to prevent huge startup hangs on large repositories.
        """
        # Format: hash|parents|author|timestamp|subject
        log_format = "%H|%P|%an|%at|%s"
        output = run_git(["log", f"-n", str(self.limit), "--all", f"--pretty=format:{log_format}"])
        if not output:
            output = run_git(["log", f"-n", str(self.limit), f"--pretty=format:{log_format}"])
            if not output:
                return []

        # Efficiently gather modified files per commit in a single pass
        files_per_commit = {}
        files_output = run_git(["log", f"-n", str(self.limit), "--all", "--name-only", "--pretty=format:COMMIT:%H"])
        if not files_output:
            files_output = run_git(["log", f"-n", str(self.limit), "--name-only", "--pretty=format:COMMIT:%H"])

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

        # Resolve branch decorations/names
        ref_decorations = {}
        decorations_output = run_git(["log", f"-n", str(self.limit), "--all", "--pretty=format:%H|%D"])
        if not decorations_output:
            decorations_output = run_git(["log", f"-n", str(self.limit), "--pretty=format:%H|%D"])

        if decorations_output:
            for line in decorations_output.split("\n"):
                line = line.strip()
                if not line or "|" not in line:
                    continue
                chash, dec = line.split("|", 1)
                if dec:
                    parts = [p.strip() for p in dec.split(",") if p.strip()]
                    branches = []
                    for p in parts:
                        if p.startswith("HEAD -> "):
                            branches.append(p.replace("HEAD -> ", ""))
                        elif p.startswith("tag: "):
                            continue
                        elif "/" in p:
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
            modified_files = files_per_commit.get(commit_hash, [])
            branches = ref_decorations.get(commit_hash, [])

            # Deduce commit type
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
