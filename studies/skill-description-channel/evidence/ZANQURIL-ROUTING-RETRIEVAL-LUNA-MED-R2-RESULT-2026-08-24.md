# ZANQURIL routing and retrieval Luna-medium R2 result — 2026-08-24

Branch: `review/rook-alpha22`

Frozen measuring commit and WSL snapshot:
`e49ba61eda5e94177b5f9465c6da95d3ab574de2`

Authorized replacement preregistration:
`tests/round7/ZANQURIL-ROUTING-RETRIEVAL-LUNA-MED-R2-PREREG-2026-08-24.md`

Outcome: **all 264 authorized Codex R2 cells completed with 264 valid, zero invalid,
zero provider retry, and zero replacement. The opaque invented token produced
the highest natural body-read rate, but also the most false positives. In the
forced retrieval packet, every cell inspected the local practices file, all 12
document-present cells found the frozen definition, no online cell made a
qualifying web search, and behaviour without a find was common. The packet
therefore shows a routing response to an opaque description, not online
retrieval of ZANQURIL or a ZANQURIL-specific task-efficacy effect.**

This is a complete Codex result. A matched 228-cell Claude Code packet is now
locally admitted but has not been authorized or run; none of its cells enter
the observations or denominators below.

## Frozen boundary and validity

| Item | Observed value |
| --- | --- |
| model | exact `gpt-5.6-luna` in all 264 cells |
| reasoning effort | exact `medium` in all 264 cells |
| adapter | `codex-cli-adapter/6`; source SHA-256 `4bf0a8767ebc0f3049d126e55e84f12ec940e9b37f85316410085d15f08d5f66` |
| observed adapter identity | exact source identity above plus `codex/0.147.0` in all 264 cells |
| network | 228 natively attested offline; 36 natively attested online |
| schedule seed | `20260824` for all phases |
| schedules | exact frozen 192-cell and 36-cell schedule hashes |
| invalid / retry / replacement | `0 / 0 / 0` |

The R2 preflight passed the exact snapshot, suite and adapter hashes, all three
manifests, 192/36/36 admission, the 89-file lock, exact CLI, absent
destinations, no active provider process, and the absolute adapter-resolution
probe. The public collision screen immediately before Phase 1 and again before
the online phase found no exact ZANQURIL token, expansion, project phrase, or
code-host collision. This is bounded negative search evidence, not proof of
absence from training data or every public corpus.

The phase launchers' post-run shorthand assertion expected the abbreviated
string `codex-cli-adapter/6`. The valid summaries correctly recorded the fuller
identity `codex-cli-adapter/6+sha256:...; codex/0.147.0`, so each launcher exited
non-zero only after every scheduled provider cell, summary write, and schedule
check. No cell was rerun or replaced. The full identity was independently
verified before sealing each phase. This is an operator-wrapper false negative,
not an experimental cell failure.

## Claude Code replication status

The checked-in Claude packet freezes 192 natural-routing cells and the 36-cell
online retrieval stratum, using the same seed, arms, cases, prompts, bodies,
fixtures, and oracles as their Codex counterparts. The materialized routing
and retrieval schedules are byte-identical across runtimes. The Claude suites
and operator brief are:

- `tests/eval/suites/zanquril-routing-natural-claude-v1.json`;
- `tests/eval/suites/zanquril-retrieval-online-claude-v1.json`; and
- `tests/round7/ZANQURIL-HOB-CLAUDE-CODE-HANDOFF-2026-08-24.md`.

There is no Claude offline stratum because the current Claude adapter cannot
enforce offline execution and fails closed on an offline suite. Its routing
phase is therefore network-enabled, unlike the Codex routing phase. The
retrieval-online phase is structurally matched. Results must be analyzed
within runtime first and must not be pooled; model, CLI, adapter, and routing
network policy remain explicit differences.

## Phase 1 — natural routing

All 192 natural-routing cells were valid. The harness's ordinary smoke oracle
passed 192/192; those PASS labels only establish valid task execution. Routing
is the separate native body-delivery outcome below.

| Description arm | Body reads | TP | FP | TN | FN | Precision | Recall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| opaque ZANQURIL | 30/48 (62.5%) | 17 | 13 | 11 | 7 | 56.7% | 70.8% |
| expanded ZANQURIL | 26/48 (54.2%) | 15 | 11 | 13 | 9 | 57.7% | 62.5% |
| generic project practice | 12/48 (25.0%) | 10 | 2 | 22 | 14 | 83.3% | 41.7% |
| familiar YAGNI | 4/48 (8.3%) | 4 | 0 | 24 | 20 | 100% | 16.7% |
| **aggregate** | **72/192 (37.5%)** | **46** | **26** | **70** | **50** | **63.9%** | **47.9%** |

The opaque description loaded most often, including 13/24 negative prompts.
It was therefore a strong but poorly calibrated routing signal. Expanding the
term did not improve this pass. Familiar YAGNI was highly specific but almost
never selected. These are observations about one frozen discovery system and
do not reveal its router internals.

### Paired routing discordances

Each contrast pairs the same case and repetition. “Opaque only” means opaque
loaded and the comparison did not; “other only” is the reverse.

| Contrast | Both load | Neither loads | Opaque only | Other only |
| --- | ---: | ---: | ---: | ---: |
| opaque vs expanded | 20 | 12 | 10 | 6 |
| opaque vs generic | 8 | 14 | 22 | 4 |
| opaque vs familiar YAGNI | 4 | 18 | 26 | 0 |

Exact case/repetition discordances:

- Opaque vs expanded — opaque only:
  `alphabetise:r1`, `cli-version-drift:r1`, `creative-writing:r2`,
  `current-release-freshness:r1`, `database-migration:r2`,
  `repository-debug:r1`, `repository-debug:r3`,
  `runtime-contradiction:r3`, `supplied-summary:r2`, `translation:r3`.
- Opaque vs expanded — expanded only:
  `alphabetise:r3`, `copy-edit:r1`, `current-release-freshness:r2`,
  `data-schema:r1`, `data-schema:r3`, `sdk-current-api:r3`.
- Opaque vs generic — opaque only:
  `alphabetise:r1`, `alphabetise:r2`, `arithmetic:r2`, `arithmetic:r3`,
  `cli-version-drift:r1`, `cli-version-drift:r2`, `cli-version-drift:r3`,
  `copy-edit:r2`, `creative-writing:r1`, `creative-writing:r2`,
  `creative-writing:r3`, `current-release-freshness:r1`,
  `current-release-freshness:r3`, `database-migration:r2`,
  `database-migration:r3`, `deployment-state:r2`, `repository-debug:r2`,
  `runtime-contradiction:r3`, `sdk-current-api:r1`, `supplied-summary:r2`,
  `translation:r1`, `translation:r3`.
- Opaque vs generic — generic only:
  `deployment-state:r3`, `runtime-contradiction:r1`,
  `runtime-contradiction:r2`, `sdk-current-api:r3`.
- Opaque vs familiar YAGNI — opaque only:
  `alphabetise:r1`, `alphabetise:r2`, `arithmetic:r1`, `arithmetic:r2`,
  `arithmetic:r3`, `cli-version-drift:r1`, `cli-version-drift:r3`,
  `copy-edit:r2`, `creative-writing:r1`, `creative-writing:r2`,
  `creative-writing:r3`, `current-release-freshness:r1`,
  `current-release-freshness:r3`, `data-schema:r2`,
  `database-migration:r1`, `database-migration:r3`, `deployment-state:r1`,
  `repository-debug:r1`, `repository-debug:r2`, `repository-debug:r3`,
  `runtime-contradiction:r3`, `sdk-current-api:r2`, `supplied-summary:r2`,
  `translation:r1`, `translation:r2`, `translation:r3`.
- Opaque vs familiar YAGNI — familiar only: none.

The opaque-versus-expanded split is 10 versus 6 discordances, not a clean or
stable expansion penalty. The larger opaque-versus-generic and
opaque-versus-YAGNI differences show what happened in this run, but the packet
does not establish a cross-model acronym effect.

## Phase 2 — retrieval and bounded implementation

All 72 forced-delivery cells completed validly: 36 offline and 36 online. The
self-test task passed every oracle in every arm and policy (36/36). All 13
oracle failures occurred on the harder retry task. Ten failed its runnable
self-test check, sometimes with a scope failure as well; three implemented the
requested behavior but failed scope by changing `README.md`.

Notation in the exact table is `r1/r2/r3`, where `1` means observed/pass and
`0` means absent/fail. `P/BF` combines oracle pass and bounded-follow because
all 72 cells added zero production functions and zero production classes, so
the two outcomes were identical. `Files` is changed-file count and `churn` is
changed-line churn.

| Policy | Arm | Task | Look | Find | Task correct | P/BF | Files | Churn |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| offline | bare | self-test | 1/1/1 | 0/0/0 | 1/1/1 | 1/1/1 | 1/1/1 | 6/7/7 |
| offline | bare | retry | 1/1/1 | 0/0/0 | 1/0/0 | 0/0/0 | 2/2/2 | 15/13/15 |
| offline | expanded | self-test | 1/1/1 | 0/0/0 | 1/1/1 | 1/1/1 | 1/1/1 | 6/18/15 |
| offline | expanded | retry | 1/1/1 | 0/0/0 | 1/0/1 | 1/0/1 | 2/3/1 | 16/16/8 |
| offline | opaque + doc | self-test | 1/1/1 | 1/1/1 | 1/1/1 | 1/1/1 | 1/1/1 | 6/6/6 |
| offline | opaque + doc | retry | 1/1/1 | 1/1/1 | 0/1/0 | 0/1/0 | 2/1/3 | 13/7/11 |
| offline | opaque, no doc | self-test | 1/1/1 | 0/0/0 | 1/1/1 | 1/1/1 | 1/1/1 | 12/6/6 |
| offline | opaque, no doc | retry | 1/1/1 | 0/0/0 | 1/1/1 | 1/1/0 | 1/1/3 | 8/9/23 |
| offline | plain language | self-test | 1/1/1 | 0/0/0 | 1/1/1 | 1/1/1 | 1/1/1 | 6/5/20 |
| offline | plain language | retry | 1/1/1 | 0/0/0 | 1/1/0 | 1/1/0 | 2/1/2 | 15/7/9 |
| offline | YAGNI | self-test | 1/1/1 | 0/0/0 | 1/1/1 | 1/1/1 | 1/1/1 | 4/5/6 |
| offline | YAGNI | retry | 1/1/1 | 0/0/0 | 1/1/0 | 1/1/0 | 1/1/2 | 6/6/7 |
| online | bare | self-test | 1/1/1 | 0/0/0 | 1/1/1 | 1/1/1 | 1/1/1 | 18/18/7 |
| online | bare | retry | 1/1/1 | 0/0/0 | 1/1/1 | 0/1/1 | 3/2/2 | 18/15/15 |
| online | expanded | self-test | 1/1/1 | 0/0/0 | 1/1/1 | 1/1/1 | 1/1/1 | 6/6/7 |
| online | expanded | retry | 1/1/1 | 0/0/0 | 0/1/1 | 0/1/1 | 2/2/1 | 10/15/8 |
| online | opaque + doc | self-test | 1/1/1 | 1/1/1 | 1/1/1 | 1/1/1 | 1/1/1 | 6/6/6 |
| online | opaque + doc | retry | 1/1/1 | 1/1/1 | 1/1/0 | 1/1/0 | 2/2/2 | 15/15/10 |
| online | opaque, no doc | self-test | 1/1/1 | 0/0/0 | 1/1/1 | 1/1/1 | 1/1/1 | 7/7/15 |
| online | opaque, no doc | retry | 1/1/1 | 0/0/0 | 1/1/1 | 1/1/1 | 1/1/1 | 8/7/6 |
| online | plain language | self-test | 1/1/1 | 0/0/0 | 1/1/1 | 1/1/1 | 1/1/1 | 5/6/6 |
| online | plain language | retry | 1/1/1 | 0/0/0 | 1/1/1 | 1/1/1 | 2/2/1 | 17/14/6 |
| online | YAGNI | self-test | 1/1/1 | 0/0/0 | 1/1/1 | 1/1/1 | 1/1/1 | 6/6/5 |
| online | YAGNI | retry | 1/1/1 | 0/0/0 | 0/1/1 | 0/1/1 | 2/1/1 | 9/6/6 |

Every “look” was a native local project-practice lookup. The 12 finds were the
definition sentinel in the six document-present cells per policy. There were
zero qualifying web searches and zero useful web finds in all 36 online cells.
Online availability therefore did not become online retrieval.

### Preregistered funnel categories

Categories are: 1 no-look/no-follow; 2 no-look/follow; 3 look/no-find/no-follow;
4 look/no-find/follow; 5 find/no-follow; 6 find/follow.

| Policy | Arm | C1 | C2 | C3 | C4 | C5 | C6 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| offline | bare | 0 | 0 | 3 | 3 | 0 | 0 |
| offline | expanded | 0 | 0 | 1 | 5 | 0 | 0 |
| offline | opaque + doc | 0 | 0 | 0 | 0 | 2 | 4 |
| offline | opaque, no doc | 0 | 0 | 1 | 5 | 0 | 0 |
| offline | plain language | 0 | 0 | 1 | 5 | 0 | 0 |
| offline | YAGNI | 0 | 0 | 1 | 5 | 0 | 0 |
| online | bare | 0 | 0 | 1 | 5 | 0 | 0 |
| online | expanded | 0 | 0 | 1 | 5 | 0 | 0 |
| online | opaque + doc | 0 | 0 | 0 | 0 | 1 | 5 |
| online | opaque, no doc | 0 | 0 | 0 | 6 | 0 | 0 |
| online | plain language | 0 | 0 | 0 | 6 | 0 | 0 |
| online | YAGNI | 0 | 0 | 1 | 5 | 0 | 0 |

### Descriptive arm totals

Online and offline remain separate strata.

| Policy | Arm | Task correct | Bounded-follow | Mean files | Mean churn |
| --- | --- | ---: | ---: | ---: | ---: |
| offline | bare | 4/6 | 3/6 | 1.50 | 10.50 |
| offline | expanded | 5/6 | 5/6 | 1.50 | 13.17 |
| offline | opaque + doc | 4/6 | 4/6 | 1.50 | 8.17 |
| offline | opaque, no doc | 6/6 | 5/6 | 1.33 | 10.67 |
| offline | plain language | 5/6 | 5/6 | 1.33 | 10.33 |
| offline | YAGNI | 5/6 | 5/6 | 1.17 | 5.67 |
| online | bare | 6/6 | 5/6 | 1.67 | 15.17 |
| online | expanded | 5/6 | 5/6 | 1.33 | 8.67 |
| online | opaque + doc | 5/6 | 5/6 | 1.50 | 9.67 |
| online | opaque, no doc | 6/6 | 6/6 | 1.00 | 8.33 |
| online | plain language | 6/6 | 6/6 | 1.33 | 9.00 |
| online | YAGNI | 5/6 | 5/6 | 1.17 | 6.33 |

## Interpretation against the frozen questions

1. **Natural routing changed, but calibration worsened.** Opaque ZANQURIL
   loaded more than generic and familiar descriptions, and slightly more than
   its expansion, while also loading on 13/24 negatives. This is an observed
   routing response to the description; it is not evidence that the model knew
   what ZANQURIL meant.
2. **Unresolved ZANQURIL caused local lookup, not web lookup.** Every cell read
   the practices file. No online cell issued a qualifying web query. A public
   collision screen cannot substitute for provider retrieval evidence.
3. **The local definition was retrieved whenever present, but retrieval did
   not improve task outcomes.** Opaque + doc bounded-followed 4/6 offline and
   5/6 online; opaque without the document scored 5/6 and 6/6. A find was not
   sufficient for following and was not better than no-find in this packet.
4. **Behaviour without a find was common and non-specific.** Opaque no-doc,
   expanded, plain language, and YAGNI all scored 5/6 bounded-follow offline;
   bare scored 3/6. Because every ordinary instructed control tied the opaque
   no-doc arm, the offline separation from bare is a forced-instruction effect,
   not a ZANQURIL-specific effect. Online, bare and most instructed arms scored
   5/6; opaque no-doc and plain language scored 6/6. With no web searches and
   three repetitions per task, this cannot be attributed to network access or
   the invented term.
5. **Familiar YAGNI did not retrieve anything, but made the smallest patches.**
   Mean churn was 5.67 offline and 6.33 online. That descriptive minimality
   result is compatible with useful familiar semantics, but it is not a stable
   general effect at this sample size.

## Questions raised in the live discussion

The full [1F916 #1786 discussion](https://1f916.observer/#/post/1786), including
all 21 comments visible on 2026-08-24, was reread before this result was
finalized.

### Does forcing the full body before any tool call preserve the effect?

This packet does not answer that exact contrast. Phase 2 forcibly delivered
the frozen one-line interventions and recorded tool traces and final outcomes;
it did not compare discovery-only against the complete Greybeard body under a
forced-before-first-tool policy. The next clean test needs byte-identical
descriptions and matched discovery-only, natural-load, and forced-full-body
arms. Forcing the body would test a harness policy; it would not erase an
already delivered description from the prompt.

### Is “always delivered” a property of descriptions?

No. It is a property of the tested harness's discovery transcript. A platform
that reveals catalogs only after a routing query makes description exposure
conditional too. Future evidence should log when each description hash enters
the model context, not merely whether a body was later read.

### Is delivery the same as enactment or run completion?

No. All 72 Phase 2 interventions were force-delivered into valid completed
runs, but only 59/72 passed the complete oracle. The archive separately records
delivery, native lookup, run completion, requested correctness, scope, changed
files, churn, and oracle result. Prompt presence is therefore one stage in the
causal chain, not the outcome.

### Is the description channel a security surface?

Plausibly yes, but this ZANQURIL packet did not test adversarial obfuscation. If a
description reaches the model before selection and can alter behavior, then
untrusted description text is prompt content. Zero-width or bidirectional
controls, confusables, comments/markup, and Base64 are all reasonable carrier
hypotheses, but whether any survives parsing, normalization, catalog rendering,
and tokenization—and whether the model decodes or follows it—is empirical.

A separate preregistered benign factual canary subsequently tested visible,
Unicode Tags, zero-width binary, Base64, confusable, absent, and unrelated
carriers using the distinctive value `COPPER-FINCH-7-29Q`. Its 30-cell Codex
result established a factual description channel on that stack; it did not
test active instructions or tool authority. The matched Claude canary remains
pending and those results stay separate from ZANQURIL.

The defensive answer is not to load every body. Discovery descriptions should
be declarative and carry an honest, safety-relevant summary of what is gated
behind the body, while remaining untrusted prompt input. Reject or visibly
escape Unicode format/bidirectional controls; show reviewers normalized text
and code points; hash and log every description exposure; trust/sign skill
sources; and enforce mutation, credential, network, exfiltration, and spend
authority outside the prompt at the tool boundary.

## Usage, archives, and cleanup

| Phase | Valid | Oracle pass | Oracle fail | Input tokens | Output tokens | Total tokens | Wall seconds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| routing | 192 | 192 smoke | 0 smoke | 14,736,745 | 182,971 | 14,919,716 | 5,404.112 |
| retrieval offline | 36 | 27 | 9 | 3,583,549 | 56,500 | 3,640,049 | 1,545.979 |
| retrieval online | 36 | 32 | 4 | 3,708,534 | 59,063 | 3,767,597 | 1,583.162 |
| **total** | **264** | **not pooled** | **not pooled** | **22,028,828** | **298,534** | **22,327,362** | **8,533.252** |

Provider cost was absent for all 264 steps and is unavailable, not observed
zero.

| Evidence archive | `summary.json` SHA-256 |
| --- | --- |
| `/srv/greybeard-eval/evidence/luna-med-zanquril-routing-natural-v1-r2-20260824` | `81624076a82868d99793f243a44698597442e2ba3e998397c73c05216d112139` |
| `/srv/greybeard-eval/evidence/luna-med-zanquril-retrieval-offline-v1-r2-20260824` | `4ce749c8d27cc1d0b06036ddd3e9698428f84d1c92b4c5b1535caf8056349898` |
| `/srv/greybeard-eval/evidence/luna-med-zanquril-retrieval-online-v1-r2-20260824` | `36a2a207033cd76c2a519a97633930ae1907e57a525eb2d124f17b794b9187fb` |

Each archive returned `ARCHIVE_OK` and `SCAN_OK` against the live credential
source before cleanup. The temporary R2 auth directory is absent, all three
archives remain present, and no provider process remains. The read-only
analysis helper is
`C:\dev\greybeard-zanquril-operator-r2-20260824\analyze_evidence.py`, SHA-256
`ca189842f474cc35f66f3fdfd12abfff8cb8467ec9b241bd4b2807a60cba5b94`.

R2 authorization is exhausted. This result does not authorize a rerun, extra
repetition, alternate model, hidden-description canary, candidate derivation,
promotion, push, or publication.

— Rook ♜
