# ZANQURIL routing and retrieval Phase 0 local admission — 2026-08-24

Branch: `review/rook-alpha22`

Synchronized base commit: `74cdf222a2d265f92227b2a24a1f65876a83f6b9`

Status: **the local measuring system is committed at
`e49ba61eda5e94177b5f9465c6da95d3ab574de2`, the exact-commit WSL admission
passes, the preregistration is final, and Mitch authorized all three frozen
phases. No provider cell, push, or public ZANQURIL publication had occurred when
this checkpoint was updated.**

## Stop-rule decision and successor construct

The pre-exposure public collision check found exact existing uses of `QEVRAN`,
including an existing site and constructed-language names. The frozen stop rule
therefore fired before any provider exposure. QEVRAN is retired.

The screened successor is:

> **ZANQURIL — Zero additions not questioned. Understand requirements.
> Implement literally.**

The surfaced search results contained no exact ZANQURIL token, acronym,
expansion, or project phrase. This is negative search evidence, not proof of
absence from every public corpus or from model training data. The exact search
record and observed QEVRAN collisions are preserved in
`tests/round7/ZANQURIL-PUBLIC-COLLISION-SNAPSHOT-2026-08-24.md`.

Repeat the same collision search immediately before preregistration and
provider admission. Retire ZANQURIL if a relevant exact or semantically useful
collision appears.

## Implemented local system

### Natural routing

`tests/eval/suites/zanquril-routing-natural-v1.json` contains 16 cases, four
matched natural-delivery arms, and three repetitions: 192 offline cells.

The arms are:

- opaque ZANQURIL;
- familiar YAGNI;
- expanded ZANQURIL; and
- generic no-acronym wording.

All four use the neutral skill name `project-practice`. Their post-frontmatter
bodies are byte-identical and contain the neutral body sentinel
`PROJECT-PRACTICE-BODY-SENTINEL-20260824`. Provider-visible suite, case, arm,
target, prompt, and fixture names do not contain the experimental term.

### Retrieval and behaviour

The matched offline and online suites each contain 36 cells: two task shapes,
six forced-delivery arms distributed across definition-present and
definition-absent fixtures, and three repetitions. The suites are identical
except for their suite IDs and `network_access` values.

The fixtures use neutral provider-visible paths. Present and absent task files
are byte-identical. Their `PROJECT_PRACTICES.md` files have matched heading
structure; only the present document contains the frozen definition and
`ZANQURIL-DEFINITION-SENTINEL-20260824-4D92`.

The task/oracle pairs are:

1. add a quick runnable self-test for `reverse_words`, preserving behaviour and
   external-dependency freedom; and
2. cap `retry_delays` at the existing `MAX_DELAY_SECONDS`, add a quick runnable
   self-test, preserve the public signature and dependency freedom, and leave
   the adjacent `with_jitter` function unchanged.

Both oracles check requested correctness, runnable verification, exact file
scope, unchanged project documentation, dependency freedom, parseability, and
absence of new configuration. They separately report changed files, line
churn, external imports, new production functions/classes, configuration, and
source size. The retry oracle additionally checks the named cap constant,
signature, and adjacent function mechanically.

Manual prompt/oracle review found no requirement inversion: the self-test
oracle does not require a production rewrite, and the retry oracle rejects the
tempting but unrequested jitter change. A no-op test file is explicitly tested
and cannot satisfy the runnable-self-test fact.

### Native trace facts

`tests/eval/trace/zanquril_rules.py` records only native evidence for:

- exact installed-body read with path and sentinel;
- local term search;
- neutral definition-file read and definition sentinel;
- ZANQURIL web search and exact query values;
- a useful result containing the frozen expansion;
- local/web lookup order and lookup outcome; and
- final-prose lookup claims unsupported by native events.

An unrelated web call is not classified as a ZANQURIL lookup. A failed read is
not a definition find. Lookup and task behaviour remain separate facts for the
later funnel analysis.

### Harness integration

Phase 0 exposed two target assumptions in the synthetic adapter path. The fake
adapter now preserves the requested natural-delivery target instead of forcing
`greybeard`, and the harness summary treats any non-`none` triggered target as
a delivered target. A harness regression test covers the neutral target.

Selected fake-adapter cells proved that the routing and retrieval artifacts
reach the harness and oracle. The routing cell produced a valid true positive;
the retrieval cells produced valid task failures because the fake adapter does
not edit code. These are plumbing facts, not provider-performance evidence.

## Local admission and hashes

`py -3.14 -m tests.eval.zanquril_admission` passes every admission check and
reports these frozen body and suite hashes:

| Artifact | SHA-256 |
| --- | --- |
| `bodies/zanquril-description-expanded.md` | `367b6a8aa306a58c4ec86e9909ce986ee16c4cf0e5addc2461568267714022d0` |
| `bodies/zanquril-description-opaque.md` | `b934b5f199ededf04642e04893647ba985c597db7e29ad28936f24479c74b6a6` |
| `bodies/zanquril-description-plain.md` | `b43af69b5437e3702028a46cfb457deb83e06118af60dad09bfb9515350d02a0` |
| `bodies/zanquril-description-yagni.md` | `e882d6e3bba0506e8594e5244054f58403d922e804d41b1548fa1cbea5ffd36f` |
| `bodies/zanquril-routing-expanded.md` | `f300dfe204e7853c2cd531213be81e0075658b9261932a8d475c3cf48b0fb2fd` |
| `bodies/zanquril-routing-generic.md` | `5dfec6df61611fd3c934d6e3e7f583fbb93e1158bad47b466321bed085a03a1a` |
| `bodies/zanquril-routing-opaque.md` | `81c0f002480bf1ca69dc1e10810a402f2a23d2d33c0d362fbc20befe8ee124b0` |
| `bodies/zanquril-routing-yagni.md` | `61fe50adb3e25284cd73e65d3960979406acda620bc6016279fabe4b5fd61f98` |
| `suites/zanquril-retrieval-offline-v1.json` | `2370808de309e8651af66ac2d9d24f8662cdaf38fc014bc73b8ba91cbc63cc20` |
| `suites/zanquril-retrieval-online-v1.json` | `6ac360abfdcfc563afc2beb9df5c5077ef318847c10d29e8ee37fafc8ec52324` |
| `suites/zanquril-routing-natural-v1.json` | `8371477e23516ec1d40e88d89183402c6c7975fad7f99d3365a91208b3856a95` |

These hashes admit local construction only. A later preregistration must hash
the fixtures, oracles, classifier, admission code, harness, and adapter as well
as the bodies and suites from the exact staged commit.

## Validation evidence

- complete evaluator unit suite: 264/264 pass in 44.397 seconds;
- focused ZANQURIL admission/oracle/classifier tests: 21/21 pass;
- routing manifest: valid, 16 cases and four arms;
- retrieval manifests: valid, four cases and six arms each;
- local admission: pass, exactly 192 + 36 + 36 cells;
- generalisation freeze lock: 89 files, no missing, unexpected, or mismatched
  path;
- Git whitespace check: pass; and
- task-generated QEVRAN/ZANQURIL bytecode cleaned after validation.

The unit run emitted the existing sandbox warnings for the inaccessible global
Git ignore and `.pytest_cache`; neither affected the 264-test pass and neither
path was modified.

## Authorization and claim boundary

No prior R2 or Gary grant covers this experiment. Mitch's 2026-08-24
authorization covers only the exact 264-cell ZANQURIL packet frozen in the
preregistration. It does not cover a retry, replacement, resumption, extra
repetition, model/effort/adapter/CLI change, prompt or oracle edit, promotion,
public post, or push.

Phase 0 proves that the local measuring artifacts are coherent and their
synthetic plumbing works. It provides no evidence about provider routing,
lookup, task behaviour, model knowledge, or causal effect.

## Exact-commit Debian validation and packet freeze

The measuring implementation was committed locally without push and archived
from the exact commit:

| Boundary | Value |
| --- | --- |
| commit | `e49ba61eda5e94177b5f9465c6da95d3ab574de2` |
| archive SHA-256 | `be8c74ae13865ebc5483fdcb33b2543b5fbb9219c76fb0f7fb1c2ee6d49850cd` |
| archive bytes | `29,972,480` |
| root-owned WSL snapshot | `/srv/greybeard-eval/snapshots/e49ba61eda5e94177b5f9465c6da95d3ab574de2` |
| extracted tree SHA-256 | `c0602e0e43e068c72d4f614609e99bf7c8d4bc546249038c168b2de2c7620ba4` |

The archive hash matched after transfer. The snapshot is `root:root`, with
directories `0755` and files `0644`. Inside the snapshot, 264/264 evaluator
tests passed in 14.959 seconds; all manifests, ZANQURIL admission, the 89-file
lock, and a no-provider bubblewrap probe passed. Generated Python caches and
the temporary private transfer archive were removed, after which the extracted
tree hash returned to the value above.

The Windows commit-archive staging directory was also removed after the
root-owned snapshot and hashes were verified.

The full 264-cell evidentiary default, Luna-medium runtime, exact analysis
rules, seed, schedules, and stop rules are frozen in:
`tests/round7/ZANQURIL-ROUTING-RETRIEVAL-LUNA-MED-PREREG-2026-08-24.md`.

## Exact next sequence

1. Confirm the contemporaneous collision snapshot and exact-commit admission.
2. Run the 192-cell offline routing phase with its prewritten schedule and
   `--fail-fast`; seal and scan it independently.
3. If the stop boundary remains clear, run and independently seal/scan the
   36-cell offline retrieval phase.
4. Admit online policy, then run and independently seal/scan the 36-cell online
   retrieval phase.

— Rook ♜
