"""Next SDK version. While on 0.x a breaking spec change bumps the minor, anything else the patch.
Usage: python3 bump.py <current> <breaking|feature>
"""
import sys

current, kind = sys.argv[1], sys.argv[2]
major, minor, patch = (int(x) for x in current.strip().split("."))
if kind not in ("breaking", "feature"):
    sys.exit(f"bump: unknown kind {kind}")
if major == 0:
    minor, patch = (minor + 1, 0) if kind == "breaking" else (minor, patch + 1)
else:
    major, minor, patch = (major + 1, 0, 0) if kind == "breaking" else (major, minor + 1, 0)
print(f"{major}.{minor}.{patch}")
