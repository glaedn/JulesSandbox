import os
import subprocess

class TestRunnerAdapter:
    def discover_and_run_tests(self):
        """Discovers python test files and executes them, returning status results."""
        tests = []
        # Find test files
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
                # Run pytest or unittest safely via python3 -m unittest
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

if __name__ == "__main__":
    runner = TestRunnerAdapter()
    print("Test Discovery results:", runner.discover_and_run_tests())
