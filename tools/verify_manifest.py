#!/usr/bin/env python3
"""Verify every released file against MANIFEST.sha256."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "MANIFEST.sha256"
SKIP_PARTS = {".git", ".pytest_cache", "__pycache__", ".venv", "venv"}


def release_files() -> set[str]:
    found = set()
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        if (
            path.is_file()
            and path != MANIFEST
            and not any(part in SKIP_PARTS for part in relative.parts)
            and path.suffix != ".pyc"
        ):
            found.add(relative.as_posix())
    return found


def main() -> int:
    expected: dict[str, str] = {}
    for number, line in enumerate(MANIFEST.read_text(encoding="utf-8").splitlines(), 1):
        try:
            digest, relative = line.split("  ", 1)
        except ValueError as exc:
            raise SystemExit(f"manifest line {number} is malformed") from exc
        if len(digest) != 64 or relative in expected:
            raise SystemExit(f"manifest line {number} is invalid or duplicated")
        expected[relative] = digest

    actual_paths = release_files()
    missing = sorted(set(expected) - actual_paths)
    unexpected = sorted(actual_paths - set(expected))
    changed = []
    for relative in sorted(set(expected) & actual_paths):
        observed = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        if observed != expected[relative]:
            changed.append(relative)

    if missing or unexpected or changed:
        print(f"missing={missing}")
        print(f"unexpected={unexpected}")
        print(f"changed={changed}")
        return 1
    print(f"MANIFEST_OK files={len(expected)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
