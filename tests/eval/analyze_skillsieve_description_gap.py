#!/usr/bin/env python3
"""Compare SkillSieve Layer 1 and desclint on the frozen description canary.

This runner deliberately exercises only SkillSieve's local Layer 1 classifier.
It does not import the remote-LLM pipeline, execute skill scripts, or make network
calls. Each frozen canary body is copied byte-for-byte into a temporary skill
directory because SkillSieve's public parser accepts directories containing a
``SKILL.md`` file.

The ``description_probe`` result is a diagnostic counterfactual: it places the
already-parsed description in the SKILL.md body field before applying
SkillSieve's public PatternMatcher. It is not a result produced by SkillSieve's
normal scan path and is recorded separately for that reason.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BODIES = REPO_ROOT / "tests" / "eval" / "bodies"
ARMS = tuple(f"a{index}" for index in range(10))
LAYER1_DISTRIBUTIONS = (
    "pydantic",
    "PyYAML",
    "Levenshtein",
    "numpy",
    "tree-sitter",
    "tree-sitter-python",
    "tree-sitter-javascript",
    "tree-sitter-bash",
)


def _git(root: Path, *args: str) -> str:
    command = [
        "git",
        "-c",
        f"safe.directory={root}",
        "-C",
        str(root),
        *args,
    ]
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise SystemExit(f"git check failed ({' '.join(args)}): {detail}")
    return completed.stdout.strip()


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _format_controls(value: str) -> dict[str, int]:
    return dict(sorted(Counter(
        f"U+{ord(character):04X}"
        for character in value
        if unicodedata.category(character) == "Cf"
    ).items()))


def _category_counts(matches: list[Any]) -> dict[str, int]:
    return dict(sorted(Counter(match.category for match in matches).items()))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--skillsieve-root",
        required=True,
        type=Path,
        help="clean SkillSieve checkout to import",
    )
    parser.add_argument(
        "--expected-skillsieve-commit",
        required=True,
        help="full commit hash required before importing SkillSieve",
    )
    parser.add_argument(
        "--bodies-dir",
        default=DEFAULT_BODIES,
        type=Path,
        help="directory containing reference-a0.md through reference-a9.md",
    )
    parser.add_argument("--output", type=Path, help="optional JSON output path")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    skillsieve_root = args.skillsieve_root.resolve()
    bodies_dir = args.bodies_dir.resolve()

    actual_commit = _git(skillsieve_root, "rev-parse", "HEAD")
    if actual_commit != args.expected_skillsieve_commit:
        raise SystemExit(
            "SkillSieve revision mismatch: "
            f"expected {args.expected_skillsieve_commit}, observed {actual_commit}"
        )
    dirty = _git(skillsieve_root, "status", "--porcelain")
    if dirty:
        raise SystemExit("SkillSieve checkout is dirty; refusing an ambiguous scan")

    # Import only after the external checkout is pinned and clean.
    sys.path.insert(0, str(skillsieve_root))
    sys.path.insert(0, str(REPO_ROOT))
    from skillsieve.core.layer1.classifier import Layer1Classifier
    from skillsieve.core.layer1.pattern_matcher import PatternMatcher
    from skillsieve.parser import parse_skill_package
    from tests.eval.description_canary_admission import EXPECTED
    import yaml
    from tools.desclint import NEGATIVE as DESCLINT_NEGATIVE
    from tools.desclint import lint as desclint

    sources = {arm: bodies_dir / f"reference-{arm}.md" for arm in ARMS}
    missing = [str(path) for path in sources.values() if not path.is_file()]
    if missing:
        raise SystemExit(f"missing frozen canary bodies: {missing}")

    classifier = Layer1Classifier()
    matcher = PatternMatcher()
    records: list[dict[str, Any]] = []
    control_records: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory(prefix="skillsieve-description-gap-") as temp:
        staging_root = Path(temp)
        for arm, source in sources.items():
            staged = staging_root / arm
            staged.mkdir()
            shutil.copyfile(source, staged / "SKILL.md")

            pkg = parse_skill_package(staged)
            expected = EXPECTED[arm]
            description_exact = pkg.frontmatter.description == expected
            if not description_exact:
                raise SystemExit(f"{arm}: SkillSieve parsed a different description")

            normal_matches = matcher.scan(pkg)
            layer1 = classifier.classify(pkg)

            # Diagnostic only: ask what SkillSieve's existing patterns would see
            # if its normal scan path included the parsed description.
            description_pkg = pkg.model_copy(update={
                "skill_md_content": pkg.frontmatter.description,
                "script_files": {},
            })
            description_matches = matcher.scan(description_pkg)
            hob_findings = desclint(pkg.frontmatter.description)

            source_bytes = source.read_bytes()
            description_bytes = pkg.frontmatter.description.encode("utf-8")
            records.append({
                "arm": arm,
                "source": str(source.relative_to(REPO_ROOT)).replace("\\", "/"),
                "source_sha256": _sha256(source_bytes),
                "description_sha256": _sha256(description_bytes),
                "description_utf8_bytes": len(description_bytes),
                "description_format_controls": _format_controls(pkg.frontmatter.description),
                "description_exact": description_exact,
                "skillsieve_layer1": {
                    "verdict": layer1.verdict.value,
                    "confidence": layer1.confidence,
                    "model_used": layer1.details.get("model_used"),
                    "pattern_match_count": len(normal_matches),
                    "pattern_categories": _category_counts(normal_matches),
                    "would_escalate": layer1.verdict.value != "safe",
                },
                "skillsieve_description_probe": {
                    "diagnostic_only": True,
                    "pattern_match_count": len(description_matches),
                    "pattern_categories": _category_counts(description_matches),
                },
                "desclint": {
                    "finding_count": len(hob_findings),
                    "rules": sorted({finding["rule"] for finding in hob_findings}),
                    "severities": sorted({finding["severity"] for finding in hob_findings}),
                },
            })

        for index, description in enumerate(DESCLINT_NEGATIVE):
            control_id = f"routing-negative-{index + 1}"
            staged = staging_root / control_id
            staged.mkdir()
            frontmatter = yaml.safe_dump(
                {"name": control_id, "description": description},
                allow_unicode=True,
                sort_keys=False,
            )
            (staged / "SKILL.md").write_text(
                f"---\n{frontmatter}---\n\n# Benign routing control\n",
                encoding="utf-8",
            )

            pkg = parse_skill_package(staged)
            if pkg.frontmatter.description != description:
                raise SystemExit(f"{control_id}: SkillSieve parsed a different description")
            normal_matches = matcher.scan(pkg)
            layer1 = classifier.classify(pkg)
            description_pkg = pkg.model_copy(update={
                "skill_md_content": pkg.frontmatter.description,
                "script_files": {},
            })
            description_matches = matcher.scan(description_pkg)
            hob_findings = desclint(pkg.frontmatter.description)
            control_records.append({
                "control": control_id,
                "description_sha256": _sha256(description.encode("utf-8")),
                "description_utf8_bytes": len(description.encode("utf-8")),
                "description_exact": True,
                "skillsieve_layer1": {
                    "verdict": layer1.verdict.value,
                    "confidence": layer1.confidence,
                    "model_used": layer1.details.get("model_used"),
                    "pattern_match_count": len(normal_matches),
                    "pattern_categories": _category_counts(normal_matches),
                    "would_escalate": layer1.verdict.value != "safe",
                },
                "skillsieve_description_probe": {
                    "diagnostic_only": True,
                    "pattern_match_count": len(description_matches),
                    "pattern_categories": _category_counts(description_matches),
                },
                "desclint": {
                    "finding_count": len(hob_findings),
                    "rules": sorted({finding["rule"] for finding in hob_findings}),
                    "severities": sorted({finding["severity"] for finding in hob_findings}),
                },
            })

    result = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "greybeard_commit": _git(REPO_ROOT, "rev-parse", "HEAD"),
        "runner_sha256": _sha256(Path(__file__).read_bytes()),
        "desclint_sha256": _sha256((REPO_ROOT / "tools" / "desclint.py").read_bytes()),
        "runtime": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "dependencies": {
                distribution: importlib.metadata.version(distribution)
                for distribution in LAYER1_DISTRIBUTIONS
            },
        },
        "skillsieve": {
            "repository": "https://github.com/xiaohou521/skillsieve",
            "commit": actual_commit,
            "checkout_clean": True,
            "mode": "local-layer1-default-heuristic",
            "network_calls": 0,
            "skill_scripts_executed": 0,
        },
        "arms_expected": len(ARMS),
        "arms_scanned": len(records),
        "records": records,
        "routing_controls_expected": len(DESCLINT_NEGATIVE),
        "routing_controls_scanned": len(control_records),
        "routing_control_records": control_records,
        "summary": {
            "canary_skillsieve_layer1_escalated": sum(
                record["skillsieve_layer1"]["would_escalate"] for record in records
            ),
            "canary_desclint_flagged": sum(
                record["desclint"]["finding_count"] > 0 for record in records
            ),
            "canary_description_probe_flagged_arms": [
                record["arm"]
                for record in records
                if record["skillsieve_description_probe"]["pattern_match_count"] > 0
            ],
            "routing_control_skillsieve_layer1_escalated": sum(
                record["skillsieve_layer1"]["would_escalate"]
                for record in control_records
            ),
            "routing_control_desclint_flagged": sum(
                record["desclint"]["finding_count"] > 0
                for record in control_records
            ),
            "routing_control_description_probe_flagged": sum(
                record["skillsieve_description_probe"]["pattern_match_count"] > 0
                for record in control_records
            ),
        },
    }
    rendered = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
