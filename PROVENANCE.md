# Release provenance

## Publication boundary

This repository was assembled as a new clean-history publication tree on
2026-08-25. It does not share Git objects or commit history with the private
Greybeard development repository.

The source checkout was `Ahrimayis/greybeard-dev`, branch
`review/rook-hob-description-review`, at base commit
`ff04c833050b046df2c38fde5dba802ae4881b9b`. Several publication artifacts were
new working-tree files at assembly time, so that private commit alone is not a
content attestation. `MANIFEST.sha256` is the authoritative hash inventory for
this released tree.

## External implementation pin

The SkillSieve comparison used the public repository
`https://github.com/xiaohou521/skillsieve` at commit
`643e220284bf1b0c5404d69b57d8f5d3687e2506`. On 2026-08-25, both a fresh fetch
and an independent `git ls-remote --heads --tags` query resolved the public
`main` branch to that commit and found no other public branch or tag.

The current paper is arXiv v3. The public scanner repository still labels the
checked-in manuscript `paper/main_v2.pdf`, identifies its package as `0.1.0`,
and uses the `v2 release` commit above. The study therefore distinguishes paper
version from runnable public-code version.

## Scanner reproduction

The current-public-code rerun:

- parsed all ten descriptions exactly;
- classified all ten `SAFE` at confidence `0.0`;
- escalated zero descriptions;
- stopped the actual default `Pipeline(max_layer=3)` at Layer 1 in all ten
  cases; and
- made no remote model calls or skill-script executions.

The prior and current analyzer outputs were identical after removing only the
generation timestamp and source Greybeard commit. The released current result
is `studies/skill-description-channel/results/skillsieve-description-gap-current-main-2026-08-25.json`.

## Release checks

Before the first commit, the candidate tree passed:

- the description linter's five positive and six negative self-tests;
- Python bytecode compilation for released Python files;
- the calibrated evidence scanner's synthetic positive arm, known-credential
  positive arm, and negative arm;
- a full release-tree scan with zero known-credential and zero generic-pattern
  findings; and
- an explicit absolute-path, operator-identifier, and credential-shape review.

The evidence scanner loaded two known provider credential values into memory
for comparison and printed neither value. A clean scan is still fail-open and
must not be read as universal proof of absence.
