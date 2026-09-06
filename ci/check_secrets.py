"""Fail closed on scanner errors and suspected secrets; never print values."""
import json
import subprocess
import sys

scan = subprocess.run(
    ["detect-secrets", "scan", "--all-files", "--exclude-files", r"(^|/)(\.git|\.venv|\.mypy_cache|\.ruff_cache|__pycache__|dist|build)/"],
    check=True, capture_output=True, text=True,
)
results = json.loads(scan.stdout)["results"]
count = sum(len(items) for items in results.values())
print(f"Secret scan: {count} potential findings across {len(results)} files")
sys.exit(1 if count else 0)
