# Skill description channel study

## Reading order

1. [Article](ARTICLE.md) — publication-facing synthesis.
2. [Claims and limits](CLAIMS-AND-LIMITS.md) — compact evidence boundary.
3. [`evidence/`](evidence/) — preregistrations and result reports.
4. [`results/`](results/) — released aggregate machine-readable results.
5. [`../../tests/eval/bodies/`](../../tests/eval/bodies/) — frozen benign
   description and routing fixtures.
6. [`../../tests/eval/suites/`](../../tests/eval/suites/) — frozen suite
   definitions.

## Evidence map

| Article section | Primary released evidence |
| --- | --- |
| ZANQURIL routing and retrieval | `ZANQURIL-ROUTING-RETRIEVAL-LUNA-MED-R2-{PREREG,RESULT}-2026-08-24.md` |
| Codex hidden-description canary | `HIDDEN-DESCRIPTION-CANARY-{LUNA-MED-PREREG,CODEX-RESULT}-2026-08-24.md` |
| Claude Code routing and canary | `HOB-CLAUDE-SONNET-HAIKU-ZANQURIL-CANARY-RESULTS-2026-08-24.md`, `results/canary-*.json`, `results/zanquril-haiku45.json` |
| Plain-text content types | `DESCRIPTION-CHANNEL-INTERVIEW-{CODEX-R2-PREREG,LUNA-MED-RESULT}-2026-08-24.md` |
| Forced full-body follow-up | `GREYBEARD-FULL-BODY-VESSARINE-LUNA-MED-{PREREG,RESULT}-2026-08-24.md` |
| SkillSieve comparison | `SKILLSIEVE-DESCRIPTION-GAP-RESULT-2026-08-24.md`, `results/skillsieve-description-gap-current-main-2026-08-25.json` |

Paths in the table are relative to [`evidence/`](evidence/) unless they begin
with `results/`.

## Raw-evidence status

The initial public packet does not include provider homes or full native
traces. In particular, the roughly 156 MB Haiku routing package retains an
operator username in absolute paths and is withheld pending redaction. The
Sonnet routing/retrieval numbers remain report-level until their matching raw
package is available.

The aggregate JSON files are useful for inspecting the published tables but do
not independently prove every provider-boundary claim. This is an explicit
release limitation, not an assertion that aggregate evidence is equivalent to
native traces.

## Reproducing the SkillSieve comparison

The recorded public SkillSieve implementation is commit
`643e220284bf1b0c5404d69b57d8f5d3687e2506`. The arXiv manuscript is v3, while
the public scanner repository still resolves to that v2-release code commit.

From the repository root, after creating an isolated environment containing
SkillSieve's Layer 1 dependencies:

```text
python tests/eval/analyze_skillsieve_description_gap.py \
  --skillsieve-root /path/to/clean/skillsieve-checkout \
  --expected-skillsieve-commit 643e220284bf1b0c5404d69b57d8f5d3687e2506 \
  --output /tmp/skillsieve-description-gap.json
```

The runner refuses a dirty or mismatched SkillSieve checkout. It imports no
provider credentials, executes no skill scripts, and records the dependency,
source, runner, and parsed-description hashes.
