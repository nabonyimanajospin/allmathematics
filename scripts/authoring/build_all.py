"""Regenerate every exercises.yaml. Run with the math engine's Python:

    apps/math-engine/.venv/Scripts/python scripts/authoring/build_all.py [module ...]
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

MODULES = [
    "mvc_m01_u01",
]


def main() -> int:
    wanted = sys.argv[1:] or MODULES
    for name in wanted:
        print(f"building {name} ...")
        importlib.import_module(name).build()
    print("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
