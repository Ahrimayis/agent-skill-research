# ZANQURIL + hidden-description canary — Claude sonnet-5 & haiku-4.5 results

Date: 2026-08-24  ·  Ran by: Hob@ai.hedgegrove  ·  For: Rook
Operator (accountable): Mitch  ·  Snapshot: `90a5128` (frozen, seal-verified)

## Deviation from the pre-registration — read first

The frozen ZANQURIL and canary Claude handoffs pre-register **`claude-opus-5`** as a
model-matched replication of the Codex opus packet. On 2026-08-24 opus (and several models)
were returning **HTTP 529 Overloaded**; the opus canary halted at cell 2/30 on a 10-retry 529
exhaustion. On Mitch's direction we ran instead on **`claude-sonnet-5`** and
**`claude-haiku-4-5-20251001`**. Full note: `/srv/greybeard-eval/DEVIATION-NOTE-model-change-20260824.md`.

Consequence: **this is not a model-matched replication of Codex-opus.** Model is confounded with
runtime; read it as a Claude sonnet/haiku result. Suite content, schedule, seed (20260824),
adapter (`claude-code-adapter/7`), effort request (medium) and network policy are unchanged and
SHA-verified. Run-ids carry a `-sonnet5` / `-haiku45` suffix (the mandated ids don't encode a model).

Observed assistant-event model ids (equality-guard exact): `claude-sonnet-5`,
`claude-haiku-4-5-20251001`. Both accept `--effort medium` with no rejection. The opus `[1m]`
worry is moot: the provider stream reports `claude-opus-5`/`claude-sonnet-5`/dated-haiku, never a
`[1m]` suffix (that is UI-only).

## Coverage

| Leg | haiku-4.5 | sonnet-5 |
| --- | --- | --- |
| canary (30) | COMPLETE, 30/30 valid | **INCOMPLETE — 529-blocked at ~cell 6, no data** |
| routing (192) | COMPLETE, 192/192 valid | COMPLETE, 192/192 valid |
| retrieval-online (36) | COMPLETE, 36/36 valid | COMPLETE, 36/36 valid |

Run dirs: `/srv/greybeard-eval/runs/claude-med-*-{haiku45,sonnet5}`.
Analyzer JSON (persistent): `/srv/greybeard-eval/results-20260824/`.

**All three haiku-4.5 legs are packaged in-repo** as raw streams, credential-tree stripped and
scanned — `raw/streams/out-haiku45-{canary,retrieval,routing}/`, each with its own README carrying
run metadata, completeness and what was removed. Their analyzer JSON is committed alongside at
`raw/canary-haiku.json` and `raw/zanquril-haiku45.json`. The sonnet-5 canary continue run is at
`raw/streams/out-sonnet-continue/`; the sonnet ZANQURIL legs are not yet packaged.

## Canary — hidden-description carrier (haiku only)

30/30 cells, analyzer structure `pass: True`. **`description_visible 0/30` and `description_exact
0/30` across all 10 carrier arms** — the hidden skill-description text never surfaced to the model.
`pass:0 fail:30` (no carrier achieved its covert objective). `body_loaded 13/30`;
`canonical_exact 10/30`, concentrated in arms where the body was NOT loaded (a1: 3/3 canonical, 0
body loads) → answers came from model knowledge, not the injected description. **Clean negative for
description-channel influence on haiku.** Sonnet canary still owed (see Open actions).

## Routing (192) — natural routing by description arm

Precision / Recall / body-read-rate:

| arm | haiku P/R/body | sonnet P/R/body |
| --- | --- | --- |
| expanded | 1.00 / 0.29 / 0.15 | 0.80 / 1.00 / 0.62 |
| familiar | 1.00 / 0.08 / 0.04 | 1.00 / 0.79 / 0.40 |
| generic  | 0.93 / 0.54 / 0.29 | 0.92 / 1.00 / 0.54 |
| opaque   | 1.00 / 0.42 / 0.21 | 0.57 / 0.96 / 0.83 |

**Two operating points.** Haiku is conservative — low recall, low body-read, near-perfect
precision (≈0 false positives). Sonnet is eager — near-perfect recall and heavy body-reading, but
it over-triggers, worst on **opaque** (precision 0.57, 17 FP / 23 TP). Description wording moves
recall for both, most starkly for haiku (generic 0.54 vs familiar 0.08, a ~6.5x span).

## Retrieval-online (36) — both models

Both **36/36 task-correct, 36/36 oracle-pass**, essentially no lookups: haiku a couple local finds
(opaque-doc arm), sonnet `looked=1 found=0`, **zero web searches** either model. Both solve the
task without reaching for the definition.

## Defects found (for Rook — packet is sealed, not touched)

1. **`suite_exact` analyzer check fails on BOTH ZANQURIL legs, for BOTH models** — and would fail
   identically on the opus run. `analyze_zanquril.py:93` requires the suite *file* basename to be
   `project-practice-routing-natural-claude-v1.json` (`suite_path.endswith(f"/{suite_id}.json")`),
   but the packet ships the file as `zanquril-routing-natural-claude-v1.json`. The *internal*
   `suite_id` on every record is correct (`project-practice-...`), so condition 2 passes. This is a
   filename/id mismatch in the frozen packet, NOT a data problem — every cell is valid. Fix: rename
   the suite files to match the ids, or compare `suite_id` rather than the filename. Because of it,
   analyzer top-level `pass` is `False` despite valid data; do not read that as a run failure.

2. **`description_discovery_attested: False` on natural routing** (routing leg, both models) — please
   confirm whether the natural-routing suite is expected to attest description discovery at all, or
   whether this is a second calibration mismatch in the pass gate.

3. **My orchestration bug (not the packet), now fixed** — the campaign wrapper called the leg
   function in a command substitution `CDIR=$(run_leg ...)` where a failure did `exit 2`. That exit
   only terminated the subshell, so the campaign did NOT halt-and-preserve on a genuine failure —
   it silently continued to the next leg. This is why the sonnet campaign's 529-exhausted canary did
   not stop the run (routing/retrieval then collected valid data anyway). Rewritten to return-based
   halt (`return`, parent checks `$?`), verified. Anyone reusing this harness pattern: never `exit`
   from inside `$( )` expecting to stop the parent.

4. **`effort_requested_exact` gives opposite verdicts on identical evidence.** In
   `canary-haiku.json` the field `effort_observed_values` is `['None']` and the check
   `effort_requested_exact` is **True**. In `canary-sonnet-continue.json` that same field is also
   `['None']` and the same check is **False**. Same analyzer module
   (`tests.eval.analyze_description_canary`), same suite (`7e9e69d2…78564`), same flags — I diffed
   the two invocations and only `--run-id` and the run dir differ. The runs do differ in validity
   (30/30 vs 23/30), so the check may be deriving effort from valid cells while
   `effort_observed_values` is populated some other way; I have not read the analyzer to confirm,
   and am not adjudicating which verdict is right. Until it is resolved, **neither run's effort
   attestation should be treated as independently confirmed** — including the haiku canary's,
   despite its clean `pass: True`.

## Open actions

- **Sonnet canary owed.** Reliably 529s at ~cell 6 in this window; deferred to a quiet window.
  Fixed rerun script staged: `/srv/greybeard-eval/rerun-sonnet-canary-20260824.sh` (return-based
  halt, `tr -d`, up to 8 infra retries). One command when servers are calm.
- **Mitch: `/login` to retire the token** that sat in the cell homes across these runs.
- Opus run remains pre-registered but unrun-to-completion (halted at canary cell 2, preserved).
