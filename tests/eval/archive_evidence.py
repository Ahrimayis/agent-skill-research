#!/usr/bin/env python3
"""Create and validate credential-safe evaluation evidence archives."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


class EvidenceError(RuntimeError):
    pass


CREDENTIAL_SOURCE_ENV = ("GB_CODEX_AUTH_FILE", "GB_CLAUDE_CREDENTIALS_FILE")
FORBIDDEN_CREDENTIAL_FILES = {"auth.json", ".credentials.json"}
FORBIDDEN_ARCHIVE_DIRS = {"codex-home", "claude-config"}
SENSITIVE_KEY = re.compile(r"(?:token|secret|password|credential|api[_-]?key)", re.IGNORECASE)
GENERIC_SECRET_PATTERNS = (
    ("anthropic-key", re.compile(rb"sk-ant-[A-Za-z0-9_-]{16,}")),
    (
        "openai-key",
        re.compile(rb"(?<![A-Za-z0-9_-])sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{20,}"),
    ),
    ("github-token", re.compile(rb"(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})")),
    ("aws-access-key", re.compile(rb"AKIA[0-9A-Z]{16}")),
    ("slack-token", re.compile(rb"xox[baprs]-[A-Za-z0-9-]{10,}")),
    ("jwt", re.compile(rb"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
    ("private-key", re.compile(rb"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----")),
)

RUN_FILES = {"run.json", "schedule.json", "summary.json"}
CELL_FILES = {"cell.json", "oracle.stdout.json", "oracle.stderr.txt"}
CELL_SUFFIXES = (
    ".stdout.jsonl",
    ".stderr.txt",
    ".mutation.stdout.txt",
    ".mutation.stderr.txt",
)


@dataclass(frozen=True)
class Finding:
    path: str
    kind: str


def _sensitive_values(value: object, key: str = "") -> set[bytes]:
    found: set[bytes] = set()
    if isinstance(value, dict):
        for child_key, child in value.items():
            found.update(_sensitive_values(child, str(child_key)))
    elif isinstance(value, list):
        for child in value:
            found.update(_sensitive_values(child, key))
    elif isinstance(value, str) and len(value) >= 12 and SENSITIVE_KEY.search(key):
        found.add(value.encode("utf-8"))
    return found


def configured_secret_values(env: dict[str, str]) -> dict[str, bytes]:
    """Load live canaries without returning or logging their values."""
    values: dict[str, bytes] = {}
    for env_name in CREDENTIAL_SOURCE_ENV:
        raw_path = env.get(env_name)
        if not raw_path:
            continue
        source = Path(raw_path).resolve()
        if not source.is_file():
            continue
        data = source.read_bytes()
        if data:
            values[f"{env_name}:whole-file"] = data
        try:
            parsed = json.loads(data)
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        for index, secret in enumerate(sorted(_sensitive_values(parsed))):
            values[f"{env_name}:sensitive-value-{index + 1}"] = secret
    return values


def _path_findings(relative: Path, *, forbid_provider_dirs: bool) -> list[Finding]:
    findings: list[Finding] = []
    if relative.name.lower() in FORBIDDEN_CREDENTIAL_FILES:
        findings.append(Finding(relative.as_posix(), "credential-file"))
    if forbid_provider_dirs and any(part.lower() in FORBIDDEN_ARCHIVE_DIRS for part in relative.parts):
        findings.append(Finding(relative.as_posix(), "provider-config-tree"))
    return findings


def scan_payloads(
    payloads: Iterable[tuple[Path, bytes]],
    *,
    live_secrets: dict[str, bytes] | None = None,
    generic_patterns: bool = True,
    forbid_provider_dirs: bool = True,
) -> list[Finding]:
    findings: list[Finding] = []
    secrets = live_secrets or {}
    for relative, data in payloads:
        findings.extend(_path_findings(relative, forbid_provider_dirs=forbid_provider_dirs))
        if generic_patterns:
            for kind, pattern in GENERIC_SECRET_PATTERNS:
                if pattern.search(data):
                    findings.append(Finding(relative.as_posix(), kind))
        for label, secret in secrets.items():
            if secret and secret in data:
                findings.append(Finding(relative.as_posix(), f"live-secret:{label}"))
    return sorted(set(findings), key=lambda finding: (finding.path, finding.kind))


def tree_payloads(root: Path) -> Iterable[tuple[Path, bytes]]:
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise EvidenceError(f"evidence tree contains symlink: {path.relative_to(root).as_posix()}")
        if path.is_file():
            yield path.relative_to(root), path.read_bytes()


def scan_tree(
    root: Path,
    env: dict[str, str] | None = None,
    *,
    generic_patterns: bool = True,
    forbid_provider_dirs: bool = True,
) -> list[Finding]:
    root = root.resolve()
    if not root.is_dir():
        raise EvidenceError(f"evidence tree does not exist: {root}")
    return scan_payloads(
        tree_payloads(root),
        live_secrets=configured_secret_values(env or dict(os.environ)),
        generic_patterns=generic_patterns,
        forbid_provider_dirs=forbid_provider_dirs,
    )


def assert_home_credentials_removed(home: Path, env: dict[str, str]) -> None:
    """Fail a cell if adapter-owned credentials remain after its process exits."""
    findings = scan_tree(
        home,
        env,
        generic_patterns=False,
        forbid_provider_dirs=False,
    )
    if findings:
        summary = ", ".join(f"{finding.path} ({finding.kind})" for finding in findings)
        raise EvidenceError(f"credential material persisted in cell home: {summary}")


def _archive_sources(run_dir: Path) -> Iterable[tuple[Path, Path]]:
    for name in sorted(RUN_FILES):
        source = run_dir / name
        if source.is_file():
            yield source, Path(name)
    cells = run_dir / "cells"
    if not cells.is_dir():
        raise EvidenceError("run has no cells directory")
    for cell in sorted(path for path in cells.iterdir() if path.is_dir()):
        prefix = Path("cells") / cell.name
        for source in sorted(path for path in cell.iterdir() if path.is_file()):
            if source.name in CELL_FILES or source.name.endswith(CELL_SUFFIXES):
                yield source, prefix / source.name
        for relative_root in (Path("workspace"), Path("home") / "provider-streams"):
            root = cell / relative_root
            if not root.exists():
                continue
            for source in sorted(root.rglob("*")):
                if source.is_symlink():
                    raise EvidenceError(
                        f"run contains symlink: {(prefix / relative_root / source.relative_to(root)).as_posix()}"
                    )
                if source.is_file():
                    yield source, prefix / relative_root / source.relative_to(root)


def archive_run(run_dir: Path, destination: Path, env: dict[str, str] | None = None) -> None:
    run_dir = run_dir.resolve()
    destination = destination.resolve()
    if not run_dir.is_dir():
        raise EvidenceError(f"run directory does not exist: {run_dir}")
    if destination.exists():
        raise EvidenceError(f"refusing to overwrite archive destination: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{destination.name}-", dir=destination.parent))
    try:
        copied = 0
        for source, relative in _archive_sources(run_dir):
            target = temporary / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            copied += 1
        if copied == 0:
            raise EvidenceError("archive allowlist selected no files")
        findings = scan_tree(temporary, env)
        if findings:
            summary = ", ".join(f"{finding.path} ({finding.kind})" for finding in findings)
            raise EvidenceError(f"archive scan rejected evidence: {summary}")
        temporary.replace(destination)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


def scan_git_index(
    repo: Path,
    prefix: str = "",
    env: dict[str, str] | None = None,
) -> list[Finding]:
    repo = repo.resolve()
    proc = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR"],
        cwd=repo,
        capture_output=True,
        check=True,
    )
    names = [name for name in proc.stdout.decode("utf-8", errors="surrogateescape").split("\0") if name]
    selected = [name for name in names if not prefix or name == prefix or name.startswith(prefix.rstrip("/") + "/")]
    payloads: list[tuple[Path, bytes]] = []
    for name in selected:
        blob = subprocess.run(
            ["git", "show", f":{name}"],
            cwd=repo,
            capture_output=True,
            check=True,
        ).stdout
        payloads.append((Path(name), blob))
    return scan_payloads(
        payloads,
        live_secrets=configured_secret_values(env or dict(os.environ)),
    )


def _raise_findings(label: str, findings: list[Finding]) -> None:
    if not findings:
        return
    summary = ", ".join(f"{finding.path} ({finding.kind})" for finding in findings)
    raise EvidenceError(f"{label} rejected evidence: {summary}")


def parser() -> argparse.ArgumentParser:
    top = argparse.ArgumentParser(description=__doc__)
    commands = top.add_subparsers(dest="command", required=True)
    copy = commands.add_parser("copy")
    copy.add_argument("run_dir", type=Path)
    copy.add_argument("destination", type=Path)
    scan = commands.add_parser("scan-tree")
    scan.add_argument("path", type=Path)
    index = commands.add_parser("scan-index")
    index.add_argument("repo", type=Path)
    index.add_argument("--prefix", default="")
    return top


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "copy":
            archive_run(args.run_dir, args.destination)
            print(f"ARCHIVE_OK {args.destination.resolve()}")
        elif args.command == "scan-tree":
            _raise_findings("tree scan", scan_tree(args.path))
            print(f"SCAN_OK {args.path.resolve()}")
        else:
            _raise_findings("Git index scan", scan_git_index(args.repo, args.prefix))
            print(f"SCAN_OK index {args.repo.resolve()}")
        return 0
    except (EvidenceError, OSError, subprocess.SubprocessError) as exc:
        print(f"evidence archive error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
