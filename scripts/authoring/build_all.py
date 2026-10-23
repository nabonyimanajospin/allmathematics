"""Regenerate every exercises.yaml. Run with the math engine's Python:

    apps/math-engine/.venv/Scripts/python scripts/authoring/build_all.py [module ...]
"""

from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

MODULES = [
    "mvc_m01_u01",
    "mvc_m01_u02",
    "mvc_m01_u03_u04",
    "mvc_m02",
    "mvc_m03",
    "mvc_m04",
    "mvc_m05",
    "mvc_new",
    "mvc_curves",
    "mvc_extrema",
    "mvc_double",
    "geo_m02",
    "geo_m03",
    "geo_m01",
    "geo_polar",
    "geo_conics",
    "geo_quadrics",
    "stat_course",
]


# Modules that add practice sets to lessons (registered before the lessons are written).
MORE = [
    "more_mvc_a",
    "more_mvc_b",
    "more_mvc_c",
    "more_mvc_d",
    "more_geo_a",
]


def main() -> int:
    wanted = sys.argv[1:] or MODULES
    for name in MORE:
        if importlib.util.find_spec(name):
            importlib.import_module(name).register()
    for name in wanted:
        print(f"building {name} ...")
        importlib.import_module(name).build()
    import toolkit

    toolkit.write_orphans()
    print("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
