# .github

Community health files and organization profile for the [attest-framework](https://github.com/attest-framework) GitHub organization.

## Contents

- `profile/README.md` — Organization profile displayed at [github.com/attest-framework](https://github.com/attest-framework)
- `scripts/generate-profile.py` — regenerates the layer and adapter tables in the profile from `scripts/capabilities.json` (`attest-engine capabilities --json`); `--check` fails when they are stale
- `SECURITY.md` — Security vulnerability reporting policy (applies to all repos)

## Repositories

| Repository | Description |
|------------|-------------|
| [`attest`](https://github.com/attest-framework/attest) | Core framework — Go engine, Python SDK (`attest-ai`), TypeScript SDK (`@attest-ai/core`, `@attest-ai/vitest`), pytest + Vitest integrations |
| [`attest-examples`](https://github.com/attest-framework/attest-examples) | 27 small, copyable examples — one per feature or framework, in Python and TypeScript |
| [`refund-desk`](https://github.com/attest-framework/refund-desk) | End-to-end demo: two synthetic incidents taken from reproduction to a blocked regression |
| [`attest-bench`](https://github.com/attest-framework/attest-bench) | Benchmarks: engine protocol and codec performance, and a labeled fault corpus that measures how often each way of checking an agent run catches a faulty run |
| [`attest-framework.github.io`](https://github.com/attest-framework/attest-framework.github.io) | Documentation site — [attest-framework.github.io](https://attest-framework.github.io/) |
