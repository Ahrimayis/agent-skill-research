#!/usr/bin/env python3
"""Build the release SHA-256 manifest from the current working tree."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "MANIFEST.sha256"
SKIP_PARTS = {".git", ".pytest_cache", "__pycache__", ".venv", "venv"}


def included(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    return (
        path.is_file()
        and path != OUTPUT
        and not any(part in SKIP_PARTS for part in relative.parts)
        and path.suffix != ".pyc"
    )


def main() -> int:
    rows = []
    for path in sorted(ROOT.rglob("*"), key=lambda item: item.as_posix()):
        if included(path):
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            relative = path.relative_to(ROOT).as_posix()
            rows.append(f"{digest}  {relative}")
    OUTPUT.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {OUTPUT} with {len(rows)} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
