import os
import subprocess

class DiagnosticsScanner:
    def scan_todos(self, root_dir="."):
        """Scans python, javascript, markdown, and text files for raw TODO / FIXME / XXX comments."""
        todos = []
        extensions = (".py", ".js", ".md", ".txt", ".json", ".yml", ".yaml")
        exclude_dirs = {"node_modules", ".git", "__pycache__", "dist", "build", "gitquest"}

        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                if file.endswith(extensions):
                    path = os.path.join(root, file)
                    try:
                        with open(path, "r", encoding="utf-8", errors="ignore") as f:
                            for idx, line in enumerate(f, 1):
                                line_lower = line.lower()
                                if "todo" in line_lower or "fixme" in line_lower or "xxx" in line_lower:
                                    todos.append({
                                        "file": path,
                                        "line_number": idx,
                                        "content": line.strip(),
                                        "severity": "High" if "fixme" in line_lower else "Medium"
                                    })
                    except Exception:
                        pass
        return todos

class TestRunnerScanner:
    def discover_and_run_tests(self):
        """Discovers python test files and executes them, returning status results."""
        tests = []
        for root, dirs, files in os.walk("."):
            if ".git" in root or "node_modules" in root or "gitquest" in root:
                continue
            for file in files:
                if (file.startswith("test_") or file.endswith("_test.py")) and file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    tests.append(filepath)

        results = []
        for test_file in tests:
            try:
                res = subprocess.run(
                    ["python3", "-m", "unittest", test_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=5
                )
                passed = res.returncode == 0
                results.append({
                    "test_file": test_file,
                    "passed": passed,
                    "output": res.stderr if res.stderr else res.stdout
                })
            except subprocess.TimeoutExpired:
                results.append({
                    "test_file": test_file,
                    "passed": False,
                    "output": "Execution timed out!"
                })
            except Exception as e:
                results.append({
                    "test_file": test_file,
                    "passed": False,
                    "output": str(e)
                })
        return results
