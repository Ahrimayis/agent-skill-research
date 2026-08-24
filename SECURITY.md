# Security and responsible use

## Corpus boundary

The released description-carrier fixtures use fictional facts and inert text.
They are designed to measure transport, prompt exposure, answer influence, and
scanner coverage without asking an agent to access credentials, persist,
exfiltrate data, mutate external systems, spend money, or influence a real
person or election.

Please preserve that benign boundary in public contributions. Proposed tests
that require dangerous payloads, real secrets, third-party targets, or
uncontrolled deployment should not be submitted as ordinary pull requests.

## Running scanners

Scanner integrations execute third-party code. Pin the exact upstream commit,
inspect it before import, use an isolated environment, and do not expose
provider credentials unless a separately reviewed experiment explicitly needs
them. The included SkillSieve comparison intentionally stops on its local
Layer 1 result and records that no skill scripts or remote model calls ran.

## Reporting a problem

Do not open a public issue containing a credential, private provider trace,
operator identifier, or unredacted third-party data. Contact the repository
owner privately through the security-reporting channel configured on GitHub.

Secret scanning is fail-open: a clean result means only that no represented
pattern or known value matched. It is not proof that an artifact contains no
secret.
