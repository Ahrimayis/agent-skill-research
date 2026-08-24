# ZANQURIL routing and retrieval Luna-medium R2 replacement preregistration — 2026-08-24

Status: **replacement packet frozen and admitted; no R2 provider cell run**

Mitch authorized “another round of testing with the fixed tests” on 2026-08-24.
This grant is construed narrowly as one clean replacement of the same 264-cell
ZANQURIL packet. The measuring code, prompts, fixtures, arms, oracles,
classifiers, model, effort, CLI, adapter implementation, seed, schedules,
network split, repetitions, outcome rules, and analysis rules do not change.
The only execution fix is an absolute path to the already frozen adapter, plus
fresh run and evidence IDs so the failed run is never overwritten or resumed.

## Predecessor failure and exclusion

The first packet stopped on its first scheduled cell,
`0001-route-supplied-summary-expanded-r1`, before provider contact. The
harness launched the relative command
`python3 tests/eval/adapters/codex_cli.py` from the fresh cell workspace. That
workspace did not contain the referee's adapter, so Python exited 2 before a
provider process or session existed.

The failed packet remains preserved at:

- raw run:
  `/srv/greybeard-eval/runs/luna-med-zanquril-routing-natural-v1-20260824`;
- allowlisted archive:
  `/srv/greybeard-eval/evidence/luna-med-zanquril-routing-natural-v1-20260824`;
- archive status: `ARCHIVE_OK` and `SCAN_OK`; and
- schedule SHA-256:
  `be79ccfb44f74d3446333947383a98806a43ff602f54362e87dedbbaae3998f9`.

Its empty adapter stdout, 224-byte stderr, empty model/adapter attestations,
zero observed usage steps, and failure text are evidence that no provider
session was contacted. Numeric cost is not an observation; provider cost is
unavailable. The invalid cell is not a ZANQURIL behavioural observation and
must not enter any denominator or qualitative analysis.

## Imported frozen packet

Everything not explicitly changed below is imported without modification from
`tests/round7/ZANQURIL-ROUTING-RETRIEVAL-LUNA-MED-PREREG-2026-08-24.md`,
SHA-256
`c5ee8877e1acfebc9b8fea59816dbd26fa25bc2152366e3d81643bb364afd08c`.
In particular:

| Boundary | Frozen value |
| --- | --- |
| measuring commit | `e49ba61eda5e94177b5f9465c6da95d3ab574de2` |
| WSL snapshot | `/srv/greybeard-eval/snapshots/e49ba61eda5e94177b5f9465c6da95d3ab574de2` |
| snapshot tree SHA-256 | `c0602e0e43e068c72d4f614609e99bf7c8d4bc546249038c168b2de2c7620ba4` |
| model / effort | `gpt-5.6-luna` / `medium` |
| adapter | `codex-cli-adapter/6`; SHA-256 `4bf0a8767ebc0f3049d126e55e84f12ec940e9b37f85316410085d15f08d5f66` |
| Codex CLI | `0.147.0` |
| schedule seed | `20260824` |
| cells | 192 offline routing + 36 offline retrieval + 36 online retrieval |
| retries / replacements inside R2 | none |

The repeated public collision check at `2026-08-23T22:03:01Z` found no result
containing the exact ZANQURIL token, frozen expansion, or exact project phrase.
Generic project-management and fuzzy drug-name results are irrelevant. This
remains bounded negative search evidence rather than proof of universal
absence.

## Sole execution correction

Every R2 provider phase must pass this exact adapter command to the harness:

```text
python3 /srv/greybeard-eval/snapshots/e49ba61eda5e94177b5f9465c6da95d3ab574de2/tests/eval/adapters/codex_cli.py
```

The R2 preflight must execute that absolute file from inside a fixture
directory with a complete synthetic context but no credential. It must reach
and fail at the adapter's exact missing-auth check, proving path resolution,
imports, context parsing, CLI discovery, and bubblewrap discovery without
provider contact. Its empty probe home is then removed. Relative adapter paths
are forbidden. No measuring file changes.

The root-owned R2 operator copy passed this check and the complete hash,
manifest, 192/36/36 admission, generalisation-lock, exact-CLI, destination,
and process preflight at `2026-08-23T22:10:54Z`. The disposable probe home was
removed. No credential had been staged and no provider process ran.

## Fresh R2 identities

| Phase | Run ID | Cells | Network | Schedule SHA-256 |
| --- | --- | ---: | --- | --- |
| 1 | `luna-med-zanquril-routing-natural-v1-r2-20260824` | 192 | offline | `be79ccfb44f74d3446333947383a98806a43ff602f54362e87dedbbaae3998f9` |
| 2a | `luna-med-zanquril-retrieval-offline-v1-r2-20260824` | 36 | offline | `46b2226776eb920da932ac9e037dbcef50d71e29ea8581f02caefa79d558676b` |
| 2b | `luna-med-zanquril-retrieval-online-v1-r2-20260824` | 36 | online | `46b2226776eb920da932ac9e037dbcef50d71e29ea8581f02caefa79d558676b` |

Raw runs use `/srv/greybeard-eval/runs/<run-id>` and allowlisted archives use
`/srv/greybeard-eval/evidence/<run-id>`. Every destination must be absent at
preflight. The root-only credential source is
`/srv/greybeard-eval/.provider-auth-zanquril-r2-20260824/codex-auth.json` and
must be removed after the final scan or immediately after a stopped run has
been safely archived.

## Frozen R2 operator scripts

The credential-free source scripts are staged from
`C:\dev\greybeard-zanquril-operator-r2-20260824`, transferred with per-file
hash verification, and installed root-owned under
`/srv/greybeard-eval/operator-zanquril-r2-20260824`.

```text
a027c0dc1c44703abfacbbf0204bfe82cac4a32e1934df84128b473cccbfd298  cleanup-auth.sh
6485720686ed5bb7b6a7aa9e95333f610db0c9b0cf9ff5fddd22566313acd5e5  install-auth.sh
d99c83f0db1df9196db95be8167f34618fdd8da7231fc500e95383f9465af849  install-operator.sh
82e16de9f00a8766920dd30a87c35b97267390e5eb41c2d0300d83f04a119761  online-admission.sh
2016c224608408ca324e98635bbdde779b2aac71f1694ff627186c6dbf784e3f  preflight.sh
b135f2ae6f33bcc896088d31723e594edb8dae347f5463b97e273e1942bed056  run-phase1.sh
51bcd33964d5085cec8c24292d52faab69bb55889c6967ffa189faefef4e9215  run-phase2a.sh
5c0ea2f258ebf80e8ca71045d9cee90a49f3e0544b7d1bb43da80f2152757e4a  run-phase2b.sh
c5d2034c168ac42a9626808b12cf22d31a890bb835fb518a477b78bd9aaa4ad9  seal-phase1.sh
d83f5bc5a294a6123f02337d9bdd8cf093b64f874902e46793bf50693222148c  seal-phase2a.sh
58d9372f89f063c794bf862bfbdba0536d5196845612ef9556290b27d36ee845  seal-phase2b.sh
```

## Run order and stop rule

1. Reconfirm exact snapshot, suite and adapter hashes, manifests, ZANQURIL
   admission, generalisation lock, exact CLI, unused R2 destinations, no
   active provider process, and absolute adapter resolution.
2. Run Phase 1 with `--fail-fast`; confirm the full schedule hash, then create
   and credential-scan its allowlisted archive.
3. Run and independently seal Phase 2a only after Phase 1 is valid 192/192.
4. Recheck collision and online network admission, then run and independently
   seal Phase 2b only after Phase 2a is valid 36/36.
5. Remove the temporary credential source and audit no retained credential or
   provider process.

Any R2 `INVALID`, interruption, model/effort/CLI/adapter/network/schedule
mismatch, missing native trace, archive rejection, credential finding, or new
public collision stops R2 and every later phase. Preserve partial evidence. Do
not repair, retry, replace, or resume R2 without another preregistration and
explicit grant. Valid misses and task failures remain experimental outcomes.

Before drafting a results post, read the full live discussion thread and
answer its substantive questions explicitly. Do not push or publish without a
separate instruction.

— Rook ♜
