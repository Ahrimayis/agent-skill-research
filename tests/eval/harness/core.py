#!/usr/bin/env python3
"""Portable, evidence-clean Greybeard evaluation orchestrator."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import signal
import shlex
import shutil
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tests.eval.archive_evidence import EvidenceError, assert_home_credentials_removed

ROOT = Path(__file__).resolve().parents[3]
EVAL_ROOT = ROOT / "tests" / "eval"
VALID_MODES = {"none", "natural", "forced", "retained"}


class ContractError(ValueError):
    pass


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_hash(root: Path) -> str:
    """Hash names, modes and bytes; ignore Git and generated Python litter."""
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*"), key=lambda p: p.as_posix()):
        rel = path.relative_to(root)
        if ".git" in rel.parts or "__pycache__" in rel.parts or path.suffix == ".pyc":
            continue
        kind = "d" if path.is_dir() else "f"
        mode = path.stat().st_mode & 0o777
        digest.update(f"{kind} {mode:o} {rel.as_posix()}\0".encode())
        if path.is_file():
            digest.update(path.read_bytes())
    return digest.hexdigest()


def _require(obj: dict[str, Any], key: str, kind: type) -> Any:
    value = obj.get(key)
    if not isinstance(value, kind):
        raise ContractError(f"{key} must be {kind.__name__}")
    return value


def validate_suite(data: dict[str, Any], source: Path | None = None) -> None:
    if data.get("schema_version") != 1:
        raise ContractError("schema_version must be 1")
    if data.get("kind") not in {"fast", "integration"}:
        raise ContractError("kind must be fast or integration")
    _require(data, "id", str)
    if not isinstance(data.get("network_access", False), bool):
        raise ContractError("network_access must be bool")
    arms = _require(data, "arms", list)
    cases = _require(data, "cases", list)
    if not arms or not cases:
        raise ContractError("arms and cases must not be empty")
    arm_ids: set[str] = set()
    for arm in arms:
        arm_id = _require(arm, "id", str)
        if arm_id in arm_ids:
            raise ContractError(f"duplicate arm: {arm_id}")
        arm_ids.add(arm_id)
        mode = arm.get("delivery_mode")
        if mode not in VALID_MODES:
            raise ContractError(f"arm {arm_id}: invalid delivery_mode")
        if mode == "retained":
            raise ContractError(f"arm {arm_id}: retained delivery is continuation-only")
        target = _require(arm, "delivery_target", str)
        body = arm.get("body")
        if mode == "forced" and (target == "none" or not isinstance(body, str)):
            raise ContractError(f"arm {arm_id}: forced delivery needs body and target")
        if mode == "none" and target != "none":
            raise ContractError(f"arm {arm_id}: none delivery must target none")
        if source and isinstance(body, str) and not (source.parent / body).resolve().is_file():
            raise ContractError(f"arm {arm_id}: body not found: {body}")
        initial_body = arm.get("initial_body")
        initial_target = arm.get("initial_target")
        if (initial_body is None) != (initial_target is None):
            raise ContractError(f"arm {arm_id}: initial_body and initial_target must appear together")
        if initial_body is not None:
            if mode != "forced" or not isinstance(initial_body, str) or not isinstance(initial_target, str):
                raise ContractError(f"arm {arm_id}: initial delivery must be forced with string fields")
            if source and not (source.parent / initial_body).resolve().is_file():
                raise ContractError(f"arm {arm_id}: initial body not found: {initial_body}")
        continuation = arm.get("continuation_delivery_mode")
        if continuation is not None and (continuation != "retained" or mode != "forced"):
            raise ContractError(f"arm {arm_id}: continuation mode must retain an initially forced body")
    case_ids: set[str] = set()
    for case in cases:
        case_id = _require(case, "id", str)
        if case_id in case_ids:
            raise ContractError(f"duplicate case: {case_id}")
        case_ids.add(case_id)
        steps = _require(case, "steps", list)
        if not steps or any(not isinstance(s.get("prompt"), str) for s in steps):
            raise ContractError(f"case {case_id}: every step needs a prompt")
        if data["kind"] == "fast" and len(steps) != 1:
            raise ContractError(f"fast case {case_id}: expected exactly one step")
        expected = case.get("expected_trigger")
        if expected not in {True, False, None}:
            raise ContractError(f"case {case_id}: expected_trigger must be boolean or null")
        selected_arms = case.get("arms")
        if selected_arms is not None:
            if not isinstance(selected_arms, list) or not selected_arms or not set(selected_arms) <= arm_ids:
                raise ContractError(f"case {case_id}: arms must name suite arms")
        if source:
            fixture = (source.parent / _require(case, "fixture", str)).resolve()
            oracle = (source.parent / _require(case, "oracle", str)).resolve()
            if not fixture.is_dir() or not oracle.is_file():
                raise ContractError(f"case {case_id}: fixture or oracle not found")
            for step in steps:
                mutation = step.get("mutation")
                if mutation is not None and not (source.parent / mutation).resolve().is_file():
                    raise ContractError(f"case {case_id}: mutation not found: {mutation}")


def load_suite(path: Path) -> dict[str, Any]:
    data = read_json(path)
    if not isinstance(data, dict):
        raise ContractError("suite root must be an object")
    validate_suite(data, path)
    return data


def build_schedule(suite: dict[str, Any], seed: int, reps: int | None = None) -> list[dict[str, Any]]:
    count = reps if reps is not None else int(suite.get("repetitions", 1))
    if count < 1:
        raise ContractError("repetitions must be positive")
    cells = [
        {"case_id": case["id"], "arm_id": arm["id"], "rep": rep}
        for rep in range(1, count + 1)
        for case in suite["cases"]
        for arm in suite["arms"]
        if not case.get("arms") or arm["id"] in case["arms"]
    ]
    random.Random(seed).shuffle(cells)
    for index, cell in enumerate(cells, 1):
        cell["order"] = index
    return cells


def select_schedule(cells: list[dict[str, Any]], cases: list[str] | None, arms: list[str] | None) -> list[dict[str, Any]]:
    selected = [
        cell for cell in cells
        if (not cases or cell["case_id"] in cases)
        and (not arms or cell["arm_id"] in arms)
    ]
    if not selected:
        raise ContractError("schedule selection matched no cells")
    for index, cell in enumerate(selected, 1):
        cell["order"] = index
    return selected


def parse_events(text: str) -> list[dict[str, Any]]:
    events = []
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ContractError(f"adapter stdout line {number} is not JSON: {exc}") from exc
        if not isinstance(event, dict) or not isinstance(event.get("type"), str):
            raise ContractError(f"adapter stdout line {number} lacks event type")
        events.append(event)
    return events


def one_event(events: list[dict[str, Any]], kind: str) -> dict[str, Any]:
    found = [event for event in events if event.get("type") == kind]
    if len(found) != 1:
        raise ContractError(f"expected exactly one {kind} event, got {len(found)}")
    return found[0]


def verify_step(
    events: list[dict[str, Any]], arm: dict[str, Any], requested_model: str,
    body_hash: str, session_id: str | None = None,
    network_access: bool | None = None,
) -> dict[str, Any]:
    run_info = one_event(events, "run_info")
    delivery = one_event(events, "delivery")
    result = one_event(events, "result")
    discoveries = [event for event in events if event.get("type") == "discovery"]
    if len(discoveries) > 1:
        raise ContractError(f"expected at most one discovery event, got {len(discoveries)}")
    discovery = discoveries[0] if discoveries else None
    if run_info.get("actual_model") != requested_model:
        raise ContractError(f"actual model {run_info.get('actual_model')!r} != requested {requested_model!r}")
    if not isinstance(run_info.get("adapter_version"), str):
        raise ContractError("run_info.adapter_version missing")
    isolation = run_info.get("isolation")
    if not isinstance(isolation, dict) or isolation.get("workspace_only") is not True or isolation.get("fresh_home") is not True:
        raise ContractError("adapter did not attest workspace-only and fresh-home isolation")
    if network_access is not None and isolation.get("network_access") is not network_access:
        raise ContractError("adapter network-access attestation mismatch")
    if session_id is not None and run_info.get("session_id") != session_id:
        raise ContractError("adapter session_id mismatch")
    if result.get("complete") is not True or not isinstance(result.get("text"), str):
        raise ContractError("result is incomplete")
    assistant_text = result.get("assistant_text")
    if (
        not isinstance(assistant_text, list)
        or not assistant_text
        or any(not isinstance(message, str) for message in assistant_text)
    ):
        raise ContractError("result.assistant_text must contain every assistant message")
    if result.get("assistant_messages") != len(assistant_text):
        raise ContractError("result.assistant_messages does not match assistant_text")
    if assistant_text[-1] != result["text"]:
        raise ContractError("result.text is not the final assistant message")
    usage = result.get("usage")
    if not isinstance(usage, dict):
        raise ContractError("result.usage missing")
    for key in ("input_tokens", "output_tokens"):
        if not isinstance(usage.get(key), (int, float)):
            raise ContractError(f"result.usage.{key} missing")
    if usage.get("cost_usd") is not None and not isinstance(usage.get("cost_usd"), (int, float)):
        raise ContractError("result.usage.cost_usd must be numeric or null")
    mode = arm["delivery_mode"]
    if delivery.get("mode") != mode:
        raise ContractError(f"delivery mode mismatch: {delivery.get('mode')} != {mode}")
    if mode in {"none", "forced", "retained"}:
        if delivery.get("target") != arm["delivery_target"]:
            raise ContractError("delivery target mismatch")
        if (delivery.get("body_sha256") or "") != body_hash:
            raise ContractError("delivery body hash mismatch")
    elif mode == "natural":
        target = delivery.get("target")
        if target not in {"none", arm["delivery_target"]}:
            raise ContractError(f"natural routing loaded wrong target: {target}")
        if target == arm["delivery_target"] and delivery.get("body_sha256") != body_hash:
            raise ContractError("natural routing loaded wrong body")
        if target == "none" and (delivery.get("body_sha256") or ""):
            raise ContractError("natural no-delivery carried a body hash")
        if discovery is not None:
            if discovery.get("target") != arm["delivery_target"]:
                raise ContractError("discovery target mismatch")
            if not isinstance(discovery.get("model_visible"), bool):
                raise ContractError("discovery model_visible missing")
            if not isinstance(discovery.get("description_exact"), bool):
                raise ContractError("discovery description_exact missing")
            source_hash = discovery.get("source_description_sha256")
            if not isinstance(source_hash, str) or len(source_hash) != 64:
                raise ContractError("discovery source description hash missing")
            visible_hash = discovery.get("model_visible_description_sha256")
            if discovery["model_visible"] and (not isinstance(visible_hash, str) or len(visible_hash) != 64):
                raise ContractError("discovery model-visible description hash missing")
            if not discovery["model_visible"] and visible_hash is not None:
                raise ContractError("unexposed discovery carried a model-visible hash")
    verified = {"run_info": run_info, "delivery": delivery, "result": result}
    if discovery is not None:
        verified["discovery"] = discovery
    return verified


@dataclass
class CellOutcome:
    status: str
    reason: str | None
    record: dict[str, Any]
    interrupted: bool = False


class AdapterInterrupted(RuntimeError):
    def __init__(self, stdout: str, stderr: str, returncode: int = 130):
        super().__init__("adapter interrupted")
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


def _signal_adapter_tree(proc: subprocess.Popen[str], action: str) -> None:
    if proc.poll() is not None:
        return
    try:
        if os.name == "posix":
            sig = {
                "interrupt": signal.SIGINT,
                "terminate": signal.SIGTERM,
                "kill": signal.SIGKILL,
            }[action]
            os.killpg(proc.pid, sig)
        elif action == "interrupt" and hasattr(signal, "CTRL_BREAK_EVENT"):
            proc.send_signal(signal.CTRL_BREAK_EVENT)
        elif action == "kill":
            proc.kill()
        else:
            proc.terminate()
    except ProcessLookupError:
        pass


def _stop_adapter_tree(proc: subprocess.Popen[str]) -> tuple[str, str, int]:
    for action, timeout in (("interrupt", 5), ("terminate", 2)):
        _signal_adapter_tree(proc, action)
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
            return stdout or "", stderr or "", proc.returncode or 130
        except subprocess.TimeoutExpired:
            continue
    _signal_adapter_tree(proc, "kill")
    stdout, stderr = proc.communicate()
    return stdout or "", stderr or "", proc.returncode or 130


def _run_adapter_process(
    adapter: list[str], prompt: str, workspace: Path, env: dict[str, str]
) -> subprocess.CompletedProcess[str]:
    kwargs: dict[str, Any] = {}
    if os.name == "posix":
        kwargs["start_new_session"] = True
    elif hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP"):
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    proc = subprocess.Popen(
        adapter,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=workspace,
        env=env,
        **kwargs,
    )
    try:
        stdout, stderr = proc.communicate(input=prompt)
    except KeyboardInterrupt as exc:
        stdout, stderr, returncode = _stop_adapter_tree(proc)
        raise AdapterInterrupted(stdout, stderr, returncode) from exc
    return subprocess.CompletedProcess(adapter, proc.returncode, stdout, stderr)


def _remove_interrupted_credentials(fresh_home: Path) -> None:
    for relative in (Path("codex-home/auth.json"), Path("claude-config/.credentials.json")):
        credential = fresh_home / relative
        credential.unlink(missing_ok=True)


def _resolved(base: Path, relative: str) -> Path:
    return (base / relative).resolve()


def run_cell(
    suite_path: Path,
    suite: dict[str, Any],
    spec: dict[str, Any],
    run_dir: Path,
    adapter: list[str],
    requested_model: str,
) -> CellOutcome:
    cell_before = time.monotonic()
    case = next(item for item in suite["cases"] if item["id"] == spec["case_id"])
    arm = next(item for item in suite["arms"] if item["id"] == spec["arm_id"])
    cell_id = f"{spec['order']:04d}-{case['id']}-{arm['id']}-r{spec['rep']}"
    cell_dir = run_dir / "cells" / cell_id
    if cell_dir.exists():
        raise ContractError(f"refusing to overwrite cell: {cell_dir}")
    cell_dir.mkdir(parents=True)
    workspace = cell_dir / "workspace"
    fresh_home = cell_dir / "home"
    fixture = _resolved(suite_path.parent, case["fixture"])
    shutil.copytree(fixture, workspace)
    fresh_home.mkdir()
    session_id = str(uuid.uuid4())
    body_path = _resolved(suite_path.parent, arm["body"]) if arm.get("body") else None
    body_hash = sha256_file(body_path) if body_path else ""
    initial_body_path = _resolved(suite_path.parent, arm["initial_body"]) if arm.get("initial_body") else None
    initial_body_hash = sha256_file(initial_body_path) if initial_body_path else ""
    started = datetime.now(timezone.utc).isoformat()
    initial_hash = tree_hash(workspace)
    steps: list[dict[str, Any]] = []
    invalid_reason: str | None = None
    interrupted = False
    for index, step in enumerate(case["steps"], 1):
        step_id = str(step.get("id") or f"step-{index}")
        if step.get("mutation"):
            mutation_path = _resolved(suite_path.parent, step["mutation"])
            mutation_proc = subprocess.run(
                [sys.executable, str(mutation_path), step_id, str(workspace)],
                text=True, capture_output=True, cwd=ROOT,
            )
            (cell_dir / f"{index:02d}-{step_id}.mutation.stdout.txt").write_text(mutation_proc.stdout, encoding="utf-8", newline="\n")
            (cell_dir / f"{index:02d}-{step_id}.mutation.stderr.txt").write_text(mutation_proc.stderr, encoding="utf-8", newline="\n")
            if mutation_proc.returncode != 0:
                invalid_reason = f"{step_id}: mutation exit {mutation_proc.returncode}"
                steps.append({"id": step_id, "mutation_exit_code": mutation_proc.returncode})
                break
        step_body_path = initial_body_path if index == 1 and initial_body_path else body_path
        step_body_hash = initial_body_hash if index == 1 and initial_body_path else body_hash
        step_target = arm.get("initial_target") if index == 1 and initial_body_path else arm["delivery_target"]
        step_mode = (
            arm.get("continuation_delivery_mode", arm["delivery_mode"])
            if index > 1 else arm["delivery_mode"]
        )
        env = os.environ.copy()
        env.update({
            "GB_EVAL_CELL_ID": cell_id,
            "GB_EVAL_SESSION_ID": session_id,
            "GB_EVAL_STEP_ID": step_id,
            "GB_EVAL_WORKSPACE": str(workspace),
            "GB_EVAL_ARM": arm["id"],
            "GB_EVAL_DELIVERY_MODE": step_mode,
            "GB_EVAL_DELIVERY_TARGET": step_target,
            "GB_EVAL_DELIVERY_BODY": str(step_body_path or ""),
            "GB_EVAL_REQUESTED_MODEL": requested_model,
            "GB_EVAL_NETWORK_ACCESS": "true" if suite.get("network_access", False) else "false",
            "GB_EVAL_HOME": str(fresh_home),
            "HOME": str(fresh_home),
            "USERPROFILE": str(fresh_home),
            "XDG_CONFIG_HOME": str(fresh_home / ".config"),
            "XDG_CACHE_HOME": str(fresh_home / ".cache"),
        })
        before = time.monotonic()
        try:
            proc = _run_adapter_process(adapter, step["prompt"], workspace, env)
        except AdapterInterrupted as exc:
            elapsed = time.monotonic() - before
            (cell_dir / f"{index:02d}-{step_id}.stdout.jsonl").write_text(
                exc.stdout, encoding="utf-8", newline="\n"
            )
            (cell_dir / f"{index:02d}-{step_id}.stderr.txt").write_text(
                exc.stderr, encoding="utf-8", newline="\n"
            )
            _remove_interrupted_credentials(fresh_home)
            try:
                assert_home_credentials_removed(fresh_home, env)
                invalid_reason = f"{step_id}: interrupted"
            except EvidenceError as cleanup_exc:
                invalid_reason = f"{step_id}: interrupted; {cleanup_exc}"
            steps.append({
                "id": step_id,
                "exit_code": exc.returncode,
                "seconds": elapsed,
                "interrupted": True,
            })
            interrupted = True
            break
        elapsed = time.monotonic() - before
        (cell_dir / f"{index:02d}-{step_id}.stdout.jsonl").write_text(proc.stdout, encoding="utf-8", newline="\n")
        (cell_dir / f"{index:02d}-{step_id}.stderr.txt").write_text(proc.stderr, encoding="utf-8", newline="\n")
        step_record: dict[str, Any] = {"id": step_id, "exit_code": proc.returncode, "seconds": elapsed}
        try:
            assert_home_credentials_removed(fresh_home, env)
            if proc.returncode != 0:
                raise ContractError(f"adapter exit {proc.returncode}")
            expected_arm = {**arm, "delivery_target": step_target, "delivery_mode": step_mode}
            verified = verify_step(
                parse_events(proc.stdout), expected_arm, requested_model,
                step_body_hash, session_id, bool(suite.get("network_access", False)),
            )
            step_record.update(verified)
        except (ContractError, EvidenceError) as exc:
            invalid_reason = f"{step_id}: {exc}"
        steps.append(step_record)
        if invalid_reason:
            break
    oracle_record: dict[str, Any] = {}
    if not invalid_reason:
        oracle_path = _resolved(suite_path.parent, case["oracle"])
        oracle_env = os.environ.copy()
        oracle_env.update({
            "GB_EVAL_ORACLE_ARM": arm["id"],
            "GB_EVAL_ORACLE_CASE": case["id"],
            "GB_EVAL_ORACLE_REP": str(spec["rep"]),
        })
        oracle_proc = subprocess.run(
            [sys.executable, str(oracle_path), str(workspace), str(cell_dir)],
            text=True, capture_output=True, cwd=ROOT, env=oracle_env,
        )
        (cell_dir / "oracle.stdout.json").write_text(oracle_proc.stdout, encoding="utf-8", newline="\n")
        (cell_dir / "oracle.stderr.txt").write_text(oracle_proc.stderr, encoding="utf-8", newline="\n")
        try:
            if oracle_proc.returncode != 0:
                raise ContractError(f"oracle exit {oracle_proc.returncode}")
            oracle_record = json.loads(oracle_proc.stdout)
            if not isinstance(oracle_record, dict) or not isinstance(oracle_record.get("pass"), bool):
                raise ContractError("oracle must return one JSON object with boolean pass")
        except (ContractError, json.JSONDecodeError) as exc:
            invalid_reason = f"oracle: {exc}"
    status = "INVALID" if invalid_reason else ("PASS" if oracle_record["pass"] else "FAIL")
    completed = datetime.now(timezone.utc).isoformat()
    record = {
        "schema_version": 1,
        "cell_id": cell_id,
        "suite_id": suite["id"],
        "suite_kind": suite["kind"],
        "case_id": case["id"],
        "arm_id": arm["id"],
        "rep": spec["rep"],
        "order": spec["order"],
        "session_id": session_id,
        "started_utc": started,
        "completed_utc": completed,
        "seconds": time.monotonic() - cell_before,
        "requested_model": requested_model,
        "skill_body_sha256": body_hash,
        "initial_skill_body_sha256": initial_body_hash,
        "initial_tree_sha256": initial_hash,
        "final_tree_sha256": tree_hash(workspace),
        "status": status,
        "invalid_reason": invalid_reason,
        "expected_trigger": case.get("expected_trigger"),
        "steps": steps,
        "oracle": oracle_record,
    }
    write_json(cell_dir / "cell.json", record)
    return CellOutcome(status, invalid_reason, record, interrupted)


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    valid = [r for r in records if r["status"] != "INVALID"]
    invalid = [r for r in records if r["status"] == "INVALID"]
    by_arm: dict[str, dict[str, int | float]] = {}
    for record in records:
        counts = by_arm.setdefault(record["arm_id"], {
            "pass": 0, "fail": 0, "invalid": 0,
            "cells": 0, "cell_seconds": 0.0, "adapter_seconds": 0.0,
            "input_tokens": 0.0, "output_tokens": 0.0,
            "total_tokens": 0.0, "cost_usd": 0.0,
            "cost_observed_steps": 0, "cost_missing_steps": 0,
        })
        counts[record["status"].lower()] += 1
        counts["cells"] += 1
        counts["cell_seconds"] += float(record.get("seconds", 0))
        for step in record.get("steps", []):
            counts["adapter_seconds"] += float(step.get("seconds", 0))
            usage = step.get("result", {}).get("usage")
            if not isinstance(usage, dict):
                continue
            step_input = float(usage.get("input_tokens", 0))
            step_output = float(usage.get("output_tokens", 0))
            counts["input_tokens"] += step_input
            counts["output_tokens"] += step_output
            counts["total_tokens"] += step_input + step_output
            if isinstance(usage.get("cost_usd"), (int, float)):
                counts["cost_usd"] += float(usage["cost_usd"])
                counts["cost_observed_steps"] += 1
            else:
                counts["cost_missing_steps"] += 1
    routed = [
        r for r in valid
        if r["expected_trigger"] is not None
        and r["steps"]
        and r["steps"][0].get("delivery", {}).get("mode") == "natural"
    ]
    tp = fp = tn = fn = 0
    for record in routed:
        target = record["steps"][0]["delivery"].get("target")
        # verify_step already restricts a valid natural event to either the
        # arm's requested target or "none". Keep the summary target-agnostic so
        # routing experiments can use a neutral installed skill name.
        triggered = isinstance(target, str) and bool(target) and target != "none"
        expected = record["expected_trigger"]
        tp += int(expected and triggered)
        fp += int(not expected and triggered)
        tn += int(not expected and not triggered)
        fn += int(expected and not triggered)
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    all_steps = [step for record in records for step in record.get("steps", [])]
    usages = [
        step["result"]["usage"]
        for record in records for step in record.get("steps", [])
        if isinstance(step.get("result", {}).get("usage"), dict)
    ]
    input_tokens = sum(float(u.get("input_tokens", 0)) for u in usages)
    output_tokens = sum(float(u.get("output_tokens", 0)) for u in usages)
    cell_seconds = [float(record.get("seconds", 0)) for record in records]
    adapter_seconds = [float(step.get("seconds", 0)) for step in all_steps]
    started = [record.get("started_utc") for record in records if record.get("started_utc")]
    completed = [record.get("completed_utc") for record in records if record.get("completed_utc")]
    wall_seconds = None
    if started and completed:
        wall_seconds = (
            datetime.fromisoformat(max(completed)) - datetime.fromisoformat(min(started))
        ).total_seconds()
    models = sorted({step["run_info"]["actual_model"] for record in valid for step in record["steps"] if step.get("run_info")})
    adapters = sorted({step["run_info"]["adapter_version"] for record in valid for step in record["steps"] if step.get("run_info")})
    return {
        "cells": len(records), "valid": len(valid), "invalid": len(invalid),
        "passes": sum(r["status"] == "PASS" for r in valid),
        "fails": sum(r["status"] == "FAIL" for r in valid),
        "by_arm": by_arm,
        "routing": {"tp": tp, "fp": fp, "tn": tn, "fn": fn, "precision": precision, "recall": recall},
        "actual_models": models,
        "adapter_versions": adapters,
        "usage": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "cost_usd": sum(float(u["cost_usd"]) for u in usages if isinstance(u.get("cost_usd"), (int, float))),
            "cost_observed_steps": sum(isinstance(u.get("cost_usd"), (int, float)) for u in usages),
            "cost_missing_steps": sum(u.get("cost_usd") is None for u in usages),
            "observed_steps": len(usages),
            "missing_steps": len(all_steps) - len(usages),
        },
        "timing": {
            "wall_seconds": wall_seconds,
            "cell_seconds": sum(cell_seconds),
            "adapter_seconds": sum(adapter_seconds),
            "mean_cell_seconds": sum(cell_seconds) / len(cell_seconds) if cell_seconds else None,
            "min_cell_seconds": min(cell_seconds) if cell_seconds else None,
            "max_cell_seconds": max(cell_seconds) if cell_seconds else None,
        },
    }


def command_validate(args: argparse.Namespace) -> int:
    suite = load_suite(args.suite.resolve())
    print(f"valid: {suite['id']} ({suite['kind']}, {len(suite['cases'])} cases, {len(suite['arms'])} arms)")
    return 0


def command_schedule(args: argparse.Namespace) -> int:
    suite = load_suite(args.suite.resolve())
    cells = select_schedule(build_schedule(suite, args.seed, args.reps), args.case, args.arm)
    print(json.dumps(cells, indent=2))
    return 0


def command_run(args: argparse.Namespace) -> int:
    suite_path = args.suite.resolve()
    suite = load_suite(suite_path)
    schedule = select_schedule(build_schedule(suite, args.seed, args.reps), args.case, args.arm)
    run_id = args.run_id or f"{suite['id']}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{args.seed}"
    run_dir = (args.output.resolve() if args.output else EVAL_ROOT / "runs" / run_id)
    if run_dir.exists():
        raise ContractError(f"refusing to overwrite run: {run_dir}")
    run_dir.mkdir(parents=True)
    write_json(run_dir / "run.json", {
        "schema_version": 1, "run_id": run_id, "suite": str(suite_path),
        "suite_sha256": sha256_file(suite_path), "seed": args.seed,
        "requested_model": args.requested_model, "adapter": args.adapter,
        "network_access": bool(suite.get("network_access", False)),
        "fail_fast": bool(args.fail_fast),
        "created_utc": datetime.now(timezone.utc).isoformat(),
    })
    write_json(run_dir / "schedule.json", schedule)
    adapter = shlex.split(args.adapter, posix=os.name != "nt")
    records = []
    interrupted = False
    for spec in schedule:
        outcome = run_cell(suite_path, suite, spec, run_dir, adapter, args.requested_model)
        records.append(outcome.record)
        print(
            f"{outcome.record['cell_id']}: {outcome.status}"
            + (f" ({outcome.reason})" if outcome.reason else ""),
            flush=True,
        )
        if outcome.interrupted:
            interrupted = True
            break
        if args.fail_fast and outcome.status == "INVALID":
            break
    summary = summarize(records)
    write_json(run_dir / "summary.json", summary)
    print(json.dumps(summary, indent=2))
    if interrupted:
        return 130
    return 2 if summary["invalid"] else 0


def command_report(args: argparse.Namespace) -> int:
    cells = [read_json(path) for path in sorted((args.run_dir / "cells").glob("*/cell.json"))]
    if not cells:
        raise ContractError("no cell records found")
    summary = summarize(cells)
    print(json.dumps(summary, indent=2))
    return 2 if summary["invalid"] else 0


def parser() -> argparse.ArgumentParser:
    out = argparse.ArgumentParser(description=__doc__)
    sub = out.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("suite", type=Path)
    validate.set_defaults(func=command_validate)
    schedule = sub.add_parser("schedule")
    schedule.add_argument("suite", type=Path)
    schedule.add_argument("--seed", type=int, required=True)
    schedule.add_argument("--reps", type=int)
    schedule.add_argument("--case", action="append")
    schedule.add_argument("--arm", action="append")
    schedule.set_defaults(func=command_schedule)
    run = sub.add_parser("run")
    run.add_argument("suite", type=Path)
    run.add_argument("--seed", type=int, required=True)
    run.add_argument("--reps", type=int)
    run.add_argument("--case", action="append")
    run.add_argument("--arm", action="append")
    run.add_argument("--adapter", required=True)
    run.add_argument("--requested-model", required=True)
    run.add_argument("--run-id")
    run.add_argument("--output", type=Path)
    run.add_argument("--fail-fast", action="store_true")
    run.set_defaults(func=command_run)
    report = sub.add_parser("report")
    report.add_argument("run_dir", type=Path)
    report.set_defaults(func=command_report)
    return out


def main(argv: list[str] | None = None) -> int:
    try:
        args = parser().parse_args(argv)
        return args.func(args)
    except (ContractError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
