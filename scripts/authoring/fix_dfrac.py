"""Use the display fraction inside display math ($$...$$) in every hand-written lesson (keeps the notation lint quiet)."""

import glob
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BS = chr(92)
pattern = re.compile(re.escape(BS + "frac") + r"(?![a-z])")
changed = 0
for path in glob.glob(str(ROOT / "content" / "**" / "lesson.yaml"), recursive=True):
    text = Path(path).read_text(encoding="utf8")
    fixed = re.sub(r"\$\$.*?\$\$", lambda m: pattern.sub(lambda _m: BS + "dfrac", m.group(0)), text, flags=re.S)
    if fixed != text:
        Path(path).write_text(fixed, encoding="utf8", newline="\n")
        changed += 1
print("files changed:", changed)
