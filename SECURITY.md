# Security Policy

## Scope and posture

CivicWorkOS (this repository) is a **research reference implementation**
(TRL 1-2; see [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)). It is
not a production system, has not undergone a security audit, and makes no
production-security claims. It has no network-facing service, no database,
and no default credentials — see [docs/architecture.md](docs/architecture.md)
for the actual components.

The one security-relevant boundary the source paper specifies is preserved
exactly: **robot execution is required to sit behind fleet middleware
enforcing ISO 10218-1:2025, independently of the allocation decision**, so
that a policy-level error in this codebase cannot defeat a hardware-level
safety interlock. This repository does not implement that middleware (it is
explicitly out of scope, per the paper); a real deployment must supply it.

## Reporting a vulnerability

If you find a security issue in this repository's code (e.g. unsafe
deserialization, path traversal in config loading, injection in a future
API layer), please report it privately rather than opening a public issue:

1. Open a GitHub Security Advisory ("Report a vulnerability" under the
   repository's Security tab), or
2. If that is unavailable, open an issue with minimal detail asking a
   maintainer to contact you privately.

Please include: affected file(s)/module(s), a minimal reproduction, and the
potential impact. We will acknowledge reports within a reasonable time and
aim to publish a fix or mitigation before public disclosure.

## Known, out-of-scope gaps (documented, not hidden)

These are named explicitly in
[docs/assumptions.md](docs/assumptions.md) and
[IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) rather than treated as
vulnerabilities to "fix" silently, because the source paper itself does not
specify them:

- No authentication/authorization layer exists (the paper describes no API).
- No cross-validation of self-reported agent signals (`Q`, `Tr`) against
  independent outcomes — the paper states this is a requirement it does not
  design (the pre-release audit).
- Governance-artifact configs (`configs/weights/`, `configs/domains/`) are
  plain YAML with no signing/verification in this reference implementation,
  though the schema models them as versioned policy acts (Paper sec:feedback).
  A production deployment should add signature verification before loading.

Do not deploy this repository against real municipal data or real automation
channels without addressing these gaps — see
[docs/deployment.md](docs/deployment.md).
