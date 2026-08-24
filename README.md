# Agent Skill Research

Controlled evaluations of how agent skill discovery, routing, delivery, and
execution interact.

The first study examines a boundary that is easy to overlook: skill
descriptions can enter an agent's prompt during discovery, before the agent
decides whether to load the skill body. The description is therefore both
routing metadata and model input.

## Current study

**[The skill description was already inside the prompt](studies/skill-description-channel/ARTICLE.md)**

The study separates six events that are often collapsed into “the skill ran”:

1. description exposure;
2. selection or declination;
3. body delivery;
4. definition or source retrieval;
5. run completion; and
6. mechanically enacted, oracle-valid behavior.

It includes controlled results from Codex and Claude Code, a ten-arm benign
description-carrier corpus, a plain-text content study, a forced-full-body
follow-up, and a comparison with the public SkillSieve scanner and our own
explainable description linter.

Start with the study's [evidence guide](studies/skill-description-channel/README.md)
and [claims and limits](studies/skill-description-channel/CLAIMS-AND-LIMITS.md).

## Release boundary

This repository is a clean-history research release. It does **not** inherit
the private Greybeard development repository's Git history.

The initial release contains frozen fixtures, suite definitions, aggregate
results, preregistrations, result reports, and the scanner-comparison runner.
It deliberately excludes provider credential/configuration trees, raw cell
homes, and the large Claude routing archive. Those artifacts require separate
redaction and provenance review before any later release.

The absence of raw provider traces lowers the independent-verification ceiling
for some results. Reports say explicitly which findings are backed by released
aggregates and which remain report-level.

See [PROVENANCE.md](PROVENANCE.md) and the mechanically verifiable
[`MANIFEST.sha256`](MANIFEST.sha256) for the exact first-release boundary.

## Safety

The description-carrier corpus uses fictional, benign canaries. It contains no
credential-access, persistence, exfiltration, mutation, or spending objective.
See [SECURITY.md](SECURITY.md) before running external scanners or extending the
corpus.

## Licence

MIT. See [LICENSE](LICENSE).
