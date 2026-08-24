#!/usr/bin/env python3
"""Codex CLI adapter for evidence-clean Greybeard evaluations.

The public ``codex exec --json`` stream is preserved, but model, session,
delivery, and isolation attestations are derived from Codex's native rollout
record. Run this adapter only on Linux/WSL2.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ADAPTER_VERSION = "codex-cli-adapter/8"
USAGE_KEYS = ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens")
REASONING_EFFORTS = {"none", "low", "medium", "high", "xhigh", "max"}

# Provider credentials that can reach the adapter through the referee's own
# environment (core.py passes os.environ through). Removed from the child
# environment because Codex has no sandbox-level env deny.
CREDENTIAL_ENV_VARS = (
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_SESSION_TOKEN",
    "GOOGLE_APPLICATION_CREDENTIALS",
    "OPENAI_API_KEY",
)


class AdapterError(RuntimeError):
    pass


def emit(value: dict[str, Any]) -> None:
    print(json.dumps(value, sort_keys=True))


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def adapter_identity(cli_version: str) -> str:
    source_hash = sha256_file(Path(__file__).resolve())
    return f"{ADAPTER_VERSION}+sha256:{source_hash}; codex/{cli_version}"


def parse_jsonl(text: str, label: str) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise AdapterError(f"{label} line {number} is not JSON: {exc}") from exc
        if not isinstance(event, dict) or not isinstance(event.get("type"), str):
            raise AdapterError(f"{label} line {number} is not an event")
        events.append(event)
    if not events:
        raise AdapterError(f"{label} is empty")
    return events


def exactly_one(events: list[dict[str, Any]], predicate, label: str) -> dict[str, Any]:
    found = [event for event in events if predicate(event)]
    if len(found) != 1:
        raise AdapterError(f"expected exactly one {label}, got {len(found)}")
    return found[0]


@dataclass(frozen=True)
class Context:
    session_id: str
    step_id: str
    workspace: Path
    home: Path
    mode: str
    target: str
    body_path: Path | None
    requested_model: str
    reasoning_effort: str = "low"
    network_access: bool = False

    @classmethod
    def from_env(cls, env: dict[str, str]) -> "Context":
        required = [
            "GB_EVAL_SESSION_ID", "GB_EVAL_STEP_ID", "GB_EVAL_WORKSPACE",
            "GB_EVAL_HOME", "GB_EVAL_DELIVERY_MODE", "GB_EVAL_DELIVERY_TARGET",
            "GB_EVAL_REQUESTED_MODEL",
        ]
        missing = [key for key in required if not env.get(key)]
        if missing:
            raise AdapterError("missing environment: " + ", ".join(missing))
        try:
            uuid.UUID(env["GB_EVAL_SESSION_ID"])
        except ValueError as exc:
            raise AdapterError("GB_EVAL_SESSION_ID is not a UUID") from exc
        mode = env["GB_EVAL_DELIVERY_MODE"]
        if mode not in {"none", "natural", "forced", "retained"}:
            raise AdapterError(f"unsupported delivery mode: {mode}")
        raw_body = env.get("GB_EVAL_DELIVERY_BODY", "")
        body_path = Path(raw_body).resolve() if raw_body else None
        if mode != "none" and (body_path is None or not body_path.is_file()):
            raise AdapterError("delivery body is missing")
        reasoning_effort = env.get("GB_CODEX_REASONING_EFFORT", "low")
        if reasoning_effort not in REASONING_EFFORTS:
            raise AdapterError(f"unsupported reasoning effort: {reasoning_effort}")
        raw_network_access = env.get("GB_EVAL_NETWORK_ACCESS", "false")
        if raw_network_access not in {"true", "false"}:
            raise AdapterError("GB_EVAL_NETWORK_ACCESS must be true or false")
        network_access = raw_network_access == "true"
        return cls(
            env["GB_EVAL_SESSION_ID"], env["GB_EVAL_STEP_ID"],
            Path(env["GB_EVAL_WORKSPACE"]).resolve(),
            Path(env["GB_EVAL_HOME"]).resolve(), mode,
            env["GB_EVAL_DELIVERY_TARGET"], body_path,
            env["GB_EVAL_REQUESTED_MODEL"], reasoning_effort, network_access,
        )


def ensure_cell_credential(codex_home: Path, env: dict[str, str]) -> Path:
    """Install a fresh per-invocation auth copy and return its exact path."""
    codex_home.mkdir(parents=True, exist_ok=True)
    auth_target = codex_home / "auth.json"
    if auth_target.exists():
        raise AdapterError("Codex credential copy already existed before invocation")
    auth_source = env.get("GB_CODEX_AUTH_FILE")
    if not auth_source:
        raise AdapterError("fresh Codex home needs GB_CODEX_AUTH_FILE")
    source = Path(auth_source).resolve()
    if not source.is_file():
        raise AdapterError("GB_CODEX_AUTH_FILE does not exist")
    shutil.copyfile(source, auth_target)
    auth_target.chmod(0o600)
    return auth_target


def prepare_home(ctx: Context, env: dict[str, str]) -> tuple[Path, dict[str, str]]:
    if platform.system() != "Linux":
        raise AdapterError("Codex isolation is supported only under Linux/WSL2; native Windows must fail closed")
    import pwd
    codex_bin = env.get("GB_CODEX_BIN", "codex")
    if shutil.which(codex_bin) is None:
        raise AdapterError("Codex CLI not found")
    if shutil.which("bwrap") is None:
        raise AdapterError("Codex outer isolation requires bubblewrap")
    codex_home = ctx.home / "codex-home"
    ensure_cell_credential(codex_home, env)
    if ctx.mode == "natural":
        assert ctx.body_path is not None
        target = codex_home / "skills" / ctx.target / "SKILL.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ctx.body_path, target)
    child_env = env.copy()
    child_env.update({
        "HOME": str(ctx.home),
        "CODEX_HOME": str(codex_home),
        "XDG_CONFIG_HOME": str(ctx.home / ".config"),
        "XDG_CACHE_HOME": str(ctx.home / ".cache"),
    })
    # Codex CLI has no equivalent of Claude Code's sandbox credential-env deny, so
    # the boundary here is the adapter: scrub provider credentials from the child
    # environment outright. Codex authenticates from auth.json in the fresh
    # CODEX_HOME, so nothing below is needed for the run to work.
    for name in CREDENTIAL_ENV_VARS:
        child_env.pop(name, None)
    child_env.pop("GB_CODEX_AUTH_FILE", None)
    run_as = env.get("GB_CODEX_RUN_AS")
    if run_as:
        if os.geteuid() != 0:
            raise AdapterError("GB_CODEX_RUN_AS requires a root referee process")
        try:
            account = pwd.getpwnam(run_as)
        except KeyError as exc:
            raise AdapterError(f"GB_CODEX_RUN_AS account does not exist: {run_as}") from exc
        for root in (ctx.workspace, ctx.home):
            for path in [root, *root.rglob("*")]:
                if path.is_symlink():
                    raise AdapterError("refusing to chown a symlink in a run directory")
                os.chown(path, account.pw_uid, account.pw_gid)
    return codex_home, child_env


def process_command(command: list[str], env: dict[str, str], ctx: Context) -> list[str]:
    cells_root = ctx.workspace.parent.parent
    cell_dir = ctx.workspace.parent
    bwrap = shutil.which("bwrap")
    if bwrap is None:
        raise AdapterError("Codex outer isolation requires bubblewrap")
    wrapped = [
        bwrap, "--unshare-user", "--unshare-pid",
        "--die-with-parent", "--new-session", "--ro-bind", "/", "/",
        "--dev", "/dev", "--proc", "/proc",
        "--tmpfs", "/tmp",
        "--tmpfs", str(cells_root),
        "--dir", str(cell_dir),
        "--dir", str(ctx.workspace),
        "--dir", str(ctx.home),
        "--bind", str(ctx.workspace), str(ctx.workspace),
        "--bind", str(ctx.home), str(ctx.home),
        "--chdir", str(ctx.workspace),
        *command,
    ]
    run_as = env.get("GB_CODEX_RUN_AS")
    if not run_as:
        return wrapped
    runuser = shutil.which("runuser")
    if runuser is None:
        raise AdapterError("runuser is required for GB_CODEX_RUN_AS")
    return [runuser, "-u", run_as, "--", *wrapped]


def _delivery_config(ctx: Context) -> list[str]:
    if ctx.mode != "forced":
        return []
    assert ctx.body_path is not None
    body = ctx.body_path.read_text(encoding="utf-8")
    return ["--config", "developer_instructions=" + json.dumps(body)]


def _config(ctx: Context, include_delivery: bool = True) -> list[str]:
    config = [
        "--ask-for-approval", "never", "--sandbox", "workspace-write",
        "--model", ctx.requested_model,
        "--config", "model_reasoning_effort=" + json.dumps(ctx.reasoning_effort),
        "--config", f"sandbox_workspace_write.network_access={str(ctx.network_access).lower()}",
        "--config", "sandbox_workspace_write.exclude_slash_tmp=true",
        "--config", "sandbox_workspace_write.exclude_tmpdir_env_var=true",
    ]
    if include_delivery:
        config.extend(_delivery_config(ctx))
    return config


def build_command(ctx: Context, codex_bin: str, provider_session: str | None) -> list[str]:
    common = [
        codex_bin, *_config(ctx, include_delivery=provider_session is None),
        "exec", "--json", "--ignore-user-config",
        "--ignore-rules", "--skip-git-repo-check",
    ]
    if provider_session is None:
        return [*common, "--cd", str(ctx.workspace), "-"]
    return [*common, "resume", *_delivery_config(ctx), provider_session, "-"]


def provider_state_path(ctx: Context) -> Path:
    return ctx.home / "codex-provider-session.json"


def load_provider_session(ctx: Context) -> str | None:
    path = provider_state_path(ctx)
    if not path.exists():
        return None
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
        provider_session = state["provider_session_id"]
        logical_session = state["logical_session_id"]
        uuid.UUID(provider_session)
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise AdapterError("stored Codex provider session is invalid") from exc
    if logical_session != ctx.session_id:
        raise AdapterError("stored Codex provider session belongs to another cell")
    return provider_session


def save_provider_session(ctx: Context, provider_session: str) -> None:
    _write_text(provider_state_path(ctx), json.dumps({
        "logical_session_id": ctx.session_id,
        "provider_session_id": provider_session,
    }, sort_keys=True) + "\n")


def usage_state_path(ctx: Context) -> Path:
    return ctx.home / "codex-provider-usage.json"


def incremental_usage(
    ctx: Context, provider_session: str, cumulative: dict[str, Any], resumed: bool,
) -> dict[str, Any]:
    """Convert Codex's cumulative thread counters into this turn's delta."""
    path = usage_state_path(ctx)
    previous = {key: 0 for key in USAGE_KEYS}
    if resumed:
        if not path.is_file():
            raise AdapterError("resumed Codex provider session lacks prior usage state")
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
            if state["logical_session_id"] != ctx.session_id:
                raise AdapterError("stored Codex usage belongs to another cell")
            if state["provider_session_id"] != provider_session:
                raise AdapterError("stored Codex usage belongs to another provider session")
            stored = state["cumulative_usage"]
            if any(not isinstance(stored.get(key), (int, float)) for key in USAGE_KEYS):
                raise TypeError
            previous = {key: stored[key] for key in USAGE_KEYS}
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            raise AdapterError("stored Codex usage state is invalid") from exc
    elif path.exists():
        raise AdapterError("fresh Codex provider session already has usage state")

    delta = {key: cumulative[key] - previous[key] for key in USAGE_KEYS}
    if any(value < 0 for value in delta.values()):
        raise AdapterError("Codex cumulative usage moved backwards")
    _write_text(path, json.dumps({
        "logical_session_id": ctx.session_id,
        "provider_session_id": provider_session,
        "cumulative_usage": {key: cumulative[key] for key in USAGE_KEYS},
    }, sort_keys=True) + "\n")
    return delta


def public_result(
    events: list[dict[str, Any]], expected_session: str | None,
) -> tuple[str, dict[str, Any], str, list[str]]:
    started = exactly_one(events, lambda event: event.get("type") == "thread.started", "thread.started event")
    completed = exactly_one(events, lambda event: event.get("type") == "turn.completed", "turn.completed event")
    messages = [
        event for event in events
        if event.get("type") == "item.completed"
        and isinstance(event.get("item"), dict)
        and event["item"].get("type") == "agent_message"
    ]
    assistant_text = [event["item"].get("text") for event in messages]
    if not assistant_text or any(not isinstance(text, str) for text in assistant_text):
        raise AdapterError("Codex stream has no completed agent message")
    provider_session = started.get("thread_id")
    try:
        uuid.UUID(provider_session)
    except (TypeError, ValueError) as exc:
        raise AdapterError("Codex returned an invalid thread ID") from exc
    if expected_session is not None and provider_session != expected_session:
        raise AdapterError("Codex resumed the wrong provider session")
    usage = completed.get("usage")
    if not isinstance(usage, dict):
        raise AdapterError("Codex turn lacks usage")
    if any(not isinstance(usage.get(key), (int, float)) for key in USAGE_KEYS):
        raise AdapterError("Codex turn has incomplete usage")
    return provider_session, usage, assistant_text[-1], assistant_text


def remove_cell_credential(ctx: Context) -> None:
    """Remove only the adapter-owned credential copy, never its source."""
    credential = ctx.home / "codex-home" / "auth.json"
    credential.unlink(missing_ok=True)
    if credential.exists():
        raise AdapterError("Codex cell credential persisted after cleanup")


def find_rollout(codex_home: Path, provider_session: str) -> Path:
    found = list((codex_home / "sessions").rglob(f"*{provider_session}.jsonl"))
    if len(found) != 1:
        raise AdapterError(f"expected one native rollout for {provider_session}, got {len(found)}")
    return found[0]


def validate_rollout(
    events: list[dict[str, Any]], ctx: Context, provider_session: str, prompt: str,
) -> tuple[str, str, str]:
    meta = exactly_one(events, lambda event: event.get("type") == "session_meta", "session_meta event")
    payload = meta.get("payload") or {}
    if payload.get("id") != provider_session or payload.get("model_provider") != "openai":
        raise AdapterError("native session metadata does not match the returned thread")
    if Path(str(payload.get("cwd", ""))).resolve() != ctx.workspace:
        raise AdapterError("native session metadata has the wrong workspace")
    version = payload.get("cli_version")
    if not isinstance(version, str) or not version:
        raise AdapterError("native session metadata lacks CLI version")
    contexts = [event for event in events if event.get("type") == "turn_context"]
    if not contexts:
        raise AdapterError("native rollout lacks turn context")
    turn = contexts[-1].get("payload") or {}
    if turn.get("model") != ctx.requested_model:
        raise AdapterError(f"actual model {turn.get('model')!r} != requested {ctx.requested_model!r}")
    if turn.get("effort") != ctx.reasoning_effort:
        raise AdapterError(
            f"actual reasoning effort {turn.get('effort')!r} != requested {ctx.reasoning_effort!r}"
        )
    if Path(str(turn.get("cwd", ""))).resolve() != ctx.workspace:
        raise AdapterError("native turn context has the wrong workspace")
    sandbox = turn.get("sandbox_policy") or {}
    if sandbox.get("type") != "workspace-write":
        raise AdapterError("native turn did not use workspace-write isolation")
    if sandbox.get("network_access") is not ctx.network_access:
        raise AdapterError("native turn network access does not match the requested policy")
    if turn.get("approval_policy") != "never":
        raise AdapterError("native turn did not disable approvals")
    user_messages = []
    for event in events:
        if event.get("type") != "response_item":
            continue
        item = event.get("payload") or {}
        if item.get("type") != "message" or item.get("role") != "user":
            continue
        text = "".join(
            str(block.get("text", "")) for block in (item.get("content") or [])
            if isinstance(block, dict) and block.get("type") == "input_text"
        )
        user_messages.append(text)
    if prompt not in user_messages:
        raise AdapterError("native rollout does not contain the exact step prompt")
    for event in events:
        if event.get("type") != "response_item":
            continue
        item = event.get("payload") or {}
        if item.get("type") in {"mcp_tool_call", "mcp_call"} or str(item.get("name", "")).lower().startswith("mcp"):
            raise AdapterError("Codex used MCP in an MCP-free evaluation")
    return ctx.requested_model, version, ctx.reasoning_effort


def _frontmatter_scalar(raw: str) -> str:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise AdapterError(f"invalid double-quoted skill frontmatter scalar: {exc}") from exc
        if not isinstance(parsed, str):
            raise AdapterError("skill frontmatter scalar is not a string")
        return parsed
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    return value


def skill_metadata(path: Path) -> tuple[str, str]:
    """Read the single-line name and description used by Codex discovery."""
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    if not text.startswith("---\n"):
        raise AdapterError("natural skill body lacks opening frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise AdapterError("natural skill body lacks closing frontmatter")
    values: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, raw = line.split(":", 1)
        if key in {"name", "description"}:
            if key in values:
                raise AdapterError(f"natural skill body repeats {key}")
            values[key] = _frontmatter_scalar(raw)
    if not values.get("name") or not values.get("description"):
        raise AdapterError("natural skill body lacks name or description")
    if "\n" in values["name"] or "\n" in values["description"]:
        raise AdapterError("natural skill discovery metadata must be single-line")
    return values["name"], values["description"]


def _description_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def discovery_event(
    events: list[dict[str, Any]], ctx: Context, codex_home: Path, prompt: str,
) -> dict[str, Any]:
    """Attest the exact natural-skill description in the model-visible catalog."""
    if ctx.mode != "natural" or ctx.body_path is None:
        raise AdapterError("discovery attestation requires natural delivery")
    name, source_description = skill_metadata(ctx.body_path)
    skill_path = str((codex_home / "skills" / ctx.target / "SKILL.md").resolve())
    prompt_indices: list[int] = []
    for index, event in enumerate(events):
        if event.get("type") != "response_item":
            continue
        item = event.get("payload") or {}
        if item.get("type") != "message" or item.get("role") != "user":
            continue
        value = "".join(
            str(block.get("text", "")) for block in (item.get("content") or [])
            if isinstance(block, dict) and block.get("type") == "input_text"
        )
        if value == prompt:
            prompt_indices.append(index)
    if not prompt_indices:
        raise AdapterError("native rollout lacks current prompt for discovery attestation")
    current_prompt = prompt_indices[-1]
    prefix = f"- {name}: "
    suffix = f" (file: {skill_path})"
    catalog_events: list[tuple[int, list[str]]] = []
    for index, event in enumerate(events[:current_prompt]):
        if event.get("type") != "response_item":
            continue
        item = event.get("payload") or {}
        if item.get("type") != "message" or item.get("role") != "developer":
            continue
        blocks: list[str] = []
        for block in item.get("content") or []:
            if not isinstance(block, dict) or block.get("type") != "input_text":
                continue
            value = str(block.get("text", ""))
            if "<skills_instructions>" not in value:
                continue
            blocks.append(value)
        if blocks:
            catalog_events.append((index, blocks))
    descriptions: list[str] = []
    if catalog_events:
        # Codex 0.147 writes the automatically injected skill catalog before
        # the turn_context record. Select the closest catalog preceding the
        # exact current prompt; using turn_context as a lower bound silently
        # discarded the current catalog in one-turn native traces.
        for value in catalog_events[-1][1]:
            for line in value.splitlines():
                if line.startswith(prefix) and line.endswith(suffix):
                    descriptions.append(line[len(prefix):-len(suffix)])
    if len(descriptions) > 1:
        raise AdapterError(f"current discovery catalog repeats target skill: {len(descriptions)}")
    exposed = bool(descriptions)
    model_description = descriptions[0] if exposed else None
    return {
        "type": "discovery",
        "target": ctx.target,
        "source_name": name,
        "source_description": source_description,
        "source_description_sha256": _description_sha256(source_description),
        "model_visible": exposed,
        "model_visible_description": model_description,
        "model_visible_description_sha256": (
            _description_sha256(model_description) if model_description is not None else None
        ),
        "description_exact": model_description == source_description,
        "catalog_messages": len(catalog_events),
    }


def delivery_event(
    events: list[dict[str, Any]], ctx: Context, codex_home: Path,
    prompt: str, resumed: bool,
) -> dict[str, Any]:
    if ctx.mode == "none":
        return {"type": "delivery", "mode": "none", "target": "none", "body_sha256": ""}
    assert ctx.body_path is not None
    # Codex canonicalizes developer-instruction newlines. Treat UTF-8 text as
    # exact after universal-newline normalization while retaining the raw file
    # hash below as the source-artifact identity.
    body = ctx.body_path.read_text(encoding="utf-8")
    body_hash = sha256_file(ctx.body_path)
    prompt_indices = []
    for index, event in enumerate(events):
        if event.get("type") != "response_item":
            continue
        item = event.get("payload") or {}
        if item.get("type") != "message" or item.get("role") != "user":
            continue
        text = "".join(
            str(block.get("text", "")) for block in (item.get("content") or [])
            if isinstance(block, dict) and block.get("type") == "input_text"
        )
        if text == prompt:
            prompt_indices.append(index)
    if not prompt_indices:
        raise AdapterError("native rollout lacks the exact current prompt")
    current_prompt = prompt_indices[-1]
    if ctx.mode == "forced":
        lower_bound = 0
        if resumed:
            contexts = [
                index for index, event in enumerate(events[:current_prompt])
                if event.get("type") == "turn_context"
            ]
            if len(contexts) < 2:
                raise AdapterError("resumed rollout lacks a prior turn boundary")
            lower_bound = contexts[-2]
        delivered = []
        for event in events[lower_bound:current_prompt]:
            if event.get("type") != "response_item":
                continue
            item = event.get("payload") or {}
            if item.get("type") != "message" or item.get("role") != "developer":
                continue
            delivered.extend(
                str(block.get("text", "")) for block in (item.get("content") or [])
                if isinstance(block, dict) and block.get("type") == "input_text"
                and block.get("text") == body
            )
        if len(delivered) != 1:
            raise AdapterError(f"expected one exact native forced developer message, got {len(delivered)}")
        return {"type": "delivery", "mode": "forced", "target": ctx.target, "body_sha256": body_hash}

    if ctx.mode == "retained":
        if not resumed:
            raise AdapterError("retained delivery requires a resumed provider session")
        contexts = [
            index for index, event in enumerate(events[:current_prompt])
            if event.get("type") == "turn_context"
        ]
        if len(contexts) < 2:
            raise AdapterError("retained delivery lacks a prior turn boundary")
        retained = []
        for event in events[:contexts[-1]]:
            if event.get("type") != "response_item":
                continue
            item = event.get("payload") or {}
            if item.get("type") != "message" or item.get("role") != "developer":
                continue
            retained.extend(
                str(block.get("text", "")) for block in (item.get("content") or [])
                if isinstance(block, dict) and block.get("type") == "input_text"
                and block.get("text") == body
            )
        if len(retained) != 1:
            raise AdapterError(f"expected one exact retained developer message, got {len(retained)}")
        return {"type": "delivery", "mode": "retained", "target": ctx.target, "body_sha256": body_hash}

    skill_path = str((codex_home / "skills" / ctx.target / "SKILL.md").resolve())
    calls: dict[str, dict[str, Any]] = {}
    outputs: dict[str, Any] = {}
    for event in events[current_prompt:]:
        if event.get("type") != "response_item":
            continue
        item = event.get("payload") or {}
        if item.get("type") == "custom_tool_call" and skill_path in str(item.get("input", "")):
            calls[str(item.get("call_id", ""))] = item
        if item.get("type") == "custom_tool_call_output":
            outputs[str(item.get("call_id", ""))] = item.get("output")
    if not calls:
        return {"type": "delivery", "mode": "natural", "target": "none", "body_sha256": ""}
    def canonical_text(value: str) -> str:
        return value.replace("\r\n", "\n").replace("\r", "\n")

    proven = [
        call_id for call_id in calls
        if any(
            isinstance(block, dict)
            and block.get("type") == "input_text"
            and body in canonical_text(str(block.get("text", "")))
            for block in (outputs.get(call_id) or [])
        )
    ]
    if not proven:
        raise AdapterError("natural skill access had no exact successful native read")
    return {"type": "delivery", "mode": "natural", "target": ctx.target, "body_sha256": body_hash}


def main() -> int:
    try:
        prompt = sys.stdin.read()
        ctx = Context.from_env(dict(os.environ))
        try:
            codex_home, child_env = prepare_home(ctx, dict(os.environ))
            provider_session = load_provider_session(ctx)
            codex_bin = os.environ.get("GB_CODEX_BIN", "codex")
            command = build_command(ctx, codex_bin, provider_session)
            proc = subprocess.run(
                process_command(command, dict(os.environ), ctx), input=prompt, text=True,
                capture_output=True, cwd=ctx.workspace, env=child_env,
            )
            raw_dir = ctx.home / "provider-streams"
            raw_dir.mkdir(parents=True, exist_ok=True)
            _write_text(raw_dir / f"{ctx.step_id}.jsonl", proc.stdout)
            _write_text(raw_dir / f"{ctx.step_id}.stderr.txt", proc.stderr)
            if proc.returncode != 0:
                raise AdapterError(f"Codex CLI exited {proc.returncode}")
            public = parse_jsonl(proc.stdout, "Codex stream")
            returned_session, usage, text, assistant_text = public_result(public, provider_session)
            if provider_session is None:
                save_provider_session(ctx, returned_session)
            rollout_path = find_rollout(codex_home, returned_session)
            rollout_text = rollout_path.read_text(encoding="utf-8")
            rollout = parse_jsonl(rollout_text, "Codex rollout")
            actual_model, cli_version, actual_effort = validate_rollout(
                rollout, ctx, returned_session, prompt,
            )
            shutil.copyfile(rollout_path, raw_dir / f"{ctx.step_id}.native.jsonl")
            delivery = delivery_event(rollout, ctx, codex_home, prompt, provider_session is not None)
            turn_usage = incremental_usage(
                ctx, returned_session, usage, provider_session is not None,
            )
            emit({
                "type": "run_info", "actual_model": actual_model,
                "reasoning_effort": actual_effort,
                "adapter_version": adapter_identity(cli_version),
                "session_id": ctx.session_id, "provider_session_id": returned_session,
                "isolation": {
                    "workspace_only": True, "fresh_home": True,
                    "network_access": ctx.network_access,
                    "mechanism": "outer-bwrap-cell-view+codex-workspace-write+fresh-codex-home",
                },
            })
            if ctx.mode == "natural":
                emit(discovery_event(rollout, ctx, codex_home, prompt))
            emit(delivery)
            emit({
                "type": "result", "complete": True, "text": text,
                "assistant_text": assistant_text,
                "assistant_messages": len(assistant_text),
                "usage": {
                    "input_tokens": turn_usage["input_tokens"],
                    "cached_input_tokens": turn_usage["cached_input_tokens"],
                    "output_tokens": turn_usage["output_tokens"],
                    "reasoning_output_tokens": turn_usage["reasoning_output_tokens"],
                    "cost_usd": None,
                },
            })
            return 0
        finally:
            remove_cell_credential(ctx)
    except (AdapterError, OSError, subprocess.SubprocessError) as exc:
        print(f"codex adapter error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
