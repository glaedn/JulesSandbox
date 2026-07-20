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

class GitCLIAdapter:
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

    def get_recent_commits(self, limit=30):
        """Returns a structured log representation of recent commits."""
        log_format = "%H|%P|%an|%at|%s"
        output = run_git(["log", f"-n", str(limit), "--all", f"--pretty=format:{log_format}"])
        if not output:
            output = run_git(["log", f"-n", str(limit), f"--pretty=format:{log_format}"])
        if not output:
            return []

        commits = []
        seen = set()
        for line in output.split("\n"):
            line = line.strip()
            if not line or "|" not in line:
                continue
            parts = line.split("|", 4)
            if len(parts) < 5:
                continue
            chash, parents_str, author, timestamp, subject = parts
            if chash in seen:
                continue
            seen.add(chash)
            commits.append({
                "hash": chash,
                "short_hash": chash[:7],
                "parents": parents_str.split() if parents_str else [],
                "author": author,
                "timestamp": int(timestamp) if timestamp.isdigit() else 0,
                "subject": subject
            })
        return commits

if __name__ == "__main__":
    cli = GitCLIAdapter()
    print("Uncommitted files:", cli.get_uncommitted_files())
    print("Current branch:", cli.get_current_branch())
    print("Recent commits:", len(cli.get_recent_commits()))
