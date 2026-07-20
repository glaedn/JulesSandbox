import os

class DiagnosticsAdapter:
    def scan_todos(self, root_dir="."):
        """Scans python, javascript, markdown, and text files for raw TODO / FIXME / XXX comments."""
        todos = []
        extensions = (".py", ".js", ".md", ".txt", ".json", ".yml", ".yaml")
        exclude_dirs = {"node_modules", ".git", "__pycache__", "dist", "build", "gitquest"}

        for root, dirs, files in os.walk(root_dir):
            # Prune excluded directories
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

if __name__ == "__main__":
    diag = DiagnosticsAdapter()
    print(f"Scanned {len(diag.scan_todos())} TODO/FIXME comments in workspace.")
