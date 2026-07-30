# NielsOS Research Lab — Multi-Agent Delegation Plan

This document defines the path forward and assigns work according to the strengths of Codex, Claude, and Gemini. The repository is the source of truth. Agents must read `docs/AGENT_HANDOFF.md`, `docs/CHAT_PROMISES.md`, and this file before changing code.

## Operating model

- Codex is the primary implementation agent.
- Claude is the architecture, specification, and adversarial-review agent.
- Gemini is the TradingView/Pine, browser-automation reconnaissance, and data-model validation agent.
- No agent should work directly on `main`.
- Every task starts from a GitHub issue and ends in a pull request.
- PRs must include tests, documentation changes, and a clear handoff note.
- Any ambiguity that can block autonomous overnight operation must be converted into an intervention record, not a blocking prompt.

## Immediate sequence

### Phase A — Foundation

1. Claude reviews the current architecture and produces a concrete technical specification for Milestone 1.
2. Codex implements Milestone 1 from that specification.
3. Gemini independently reviews the TradingView/Pine assumptions and browser workflow, then records UI risks, selectors, timing constraints, and export options.
4. Claude reviews Codex's PR for architectural correctness and failure handling.
5. Codex addresses review comments and merges only after tests pass.

### Phase B — TradingView vertical slice

1. Gemini validates the single-account, single-layout workflow and documents the exact UI state contract for `NRL_MASTER` and Chrome profile `Flasherz`.
2. Codex implements one Playwright worker that opens TradingView, selects BTCUSDC, switches timeframe, captures a screenshot, and records the run in PostgreSQL.
3. Claude reviews the worker state machine, retry semantics, intervention handling, and resume logic.
4. Codex fixes issues and prepares Gateway deployment scripts.

### Phase C — Pine research harness

1. Gemini audits the existing Pine harness for look-ahead, indexing, sample alignment, and TradingView limits.
2. Claude defines the statistical contract: sample definition, forward-return alignment, long/short semantics, MFI-vs-RSI asymmetry, regimes, outputs, and minimum credibility thresholds.
3. Codex implements the corrected Pine harness and manifest schema.
4. Gemini validates Pine compilation and output behavior manually in TradingView.
5. Claude performs a research-methodology review before results are accepted.

### Phase D — Autonomous queue

1. Codex implements SQL-backed jobs, leases, heartbeats, checkpoints, retries, interventions, screenshots, and non-blocking worker recovery.
2. Claude reviews concurrency, idempotency, data integrity, and recovery scenarios.
3. Gemini tests real TradingView failure modes: login expiry, popup, stale layout, script compile failure, missing data, symbol mismatch, slow load, and rate limiting.
4. Codex incorporates findings and deploys the 24/7 service on Gateway.

### Phase E — Credibility and reporting

1. Claude defines the credibility model and guards against overfitting, low sample size, regime imbalance, and parameter-selection bias.
2. Gemini evaluates whether TradingView outputs expose sufficient statistics and proposes any extra Pine outputs.
3. Codex implements aggregation, credibility tables, dashboard, workbook export, and research ledger.

## Agent responsibilities

## Codex — implementation owner

Best used for:
- repository scaffolding
- Python services
- PostgreSQL schema and migrations
- Playwright implementation
- workers, scheduler, leases, retries, checkpoints
- dashboard and CLI
- tests, CI, packaging, systemd, Gateway installation
- translating reviewed specifications into production code

Codex should not invent statistical methodology or silently change architectural contracts. It should open a draft PR early and keep it updated.

First Codex assignment:

> Read `docs/AGENT_HANDOFF.md`, `docs/CHAT_PROMISES.md`, and `docs/MULTI_AGENT_PLAN.md`. Implement Milestone 1 only: repository package structure, configuration loading, structured logging, PostgreSQL schema/migrations, SQL job queue with atomic claim/lease, worker heartbeat, checkpoint persistence, intervention records, CLI commands, unit/integration tests, Docker Compose for local PostgreSQL, and systemd-ready entry points. Do not implement TradingView selectors yet. Nothing may block waiting for human input. Open a draft PR with architecture notes, migration instructions, test output, and unresolved risks.

Definition of done:
- clean install on macOS and Ubuntu
- PostgreSQL schema can migrate from zero
- concurrent workers cannot claim the same job
- expired leases requeue safely
- checkpoints survive process restart
- interventions are persisted and do not block queue progress
- tests cover happy path and crash/recovery path
- README has exact commands

## Claude — architect and reviewer

Best used for:
- decomposing broad goals into precise specifications
- reviewing architecture and interfaces
- identifying missing failure modes
- statistical-research design
- threat modelling and reliability review
- simplifying overly complex plans
- reviewing PRs for consistency with promises
- writing acceptance criteria and adversarial test cases

Claude should generally avoid implementing large overlapping code areas while Codex is active. Its output should be specifications, review reports, issue comments, or focused patches.

First Claude assignment:

> Read the full repository documentation and current files. Produce `docs/MILESTONE_1_SPEC.md` with a precise architecture for the first deployable foundation. Define modules, SQL tables, status enums, job lease semantics, heartbeat cadence, stale-worker recovery, checkpoint format, intervention lifecycle, idempotency rules, logging fields, configuration precedence, security boundaries, and acceptance tests. Keep the design realistic for Gateway: Ubuntu x86, 2 vCPU, 4 GB RAM, 40 GB disk. Flag any promises that conflict or are premature. Do not write the full implementation. Submit the specification through a PR or issue for Codex to follow.

Second Claude assignment after Codex opens a PR:

> Review the Milestone 1 PR adversarially. Focus on races, duplicate execution, lost checkpoints, stuck leases, database transaction boundaries, restart behavior, non-blocking interventions, secret handling, disk growth, and Gateway resource limits. Leave actionable inline comments and a final pass/fail checklist.

## Gemini — TradingView/Pine and external-behavior specialist

Best used for:
- investigating TradingView UI behavior and Pine constraints
- checking selector fragility and browser-flow assumptions
- reviewing Pine formulas and indexing
- enumerating symbols/timeframes/parameter grids
- validating watchlist and layout workflows
- identifying what can and cannot be exported from TradingView
- testing real browser failure modes
- cross-checking the Pine implementation against intended metrics

Gemini should not own the SQL scheduler or core Python service architecture. It should produce empirical UI notes, Pine reviews, and test matrices.

First Gemini assignment:

> Read `docs/CHAT_PROMISES.md`, `docs/AGENT_HANDOFF.md`, the TradingView setup docs, manifests, and `pine/NRL_Research_Harness.pine`. Produce two files: `docs/TRADINGVIEW_AUTOMATION_RECON.md` and `docs/PINE_HARNESS_AUDIT.md`. For TradingView, define the exact single-Premium-account workflow using Chrome profile `Flasherz`, layout `NRL_MASTER`, one worker, watchlists/universes, supported timeframes, stable UI anchors, expected load times, popup/login/session failure modes, screenshot checkpoints, and realistic ways to extract machine-readable results without OCR when possible. For Pine, audit look-ahead, signal-to-forward-return alignment, long/short sign handling, MFI/RSI/relative-volume asymmetry, sample counting, parameter sweeps, regime labels, TradingView limits, and table output. Provide a corrected algorithm in pseudocode but do not overwrite the Pine file until the review is accepted.

Second Gemini assignment during the vertical slice:

> Run the TradingView vertical-slice checklist manually using the Flasherz profile and NRL_MASTER layout. Record every click/state transition, timing observation, popup, and selector risk. Confirm whether BTCUSDC, ETHUSDC, SOLUSDC and stock symbols resolve consistently. File issues for anything that could stall unattended operation.

## Shared handoff format

Every agent output must contain:

1. Scope completed
2. Files changed
3. Decisions made
4. Assumptions
5. Tests performed
6. Known limitations
7. Risks and blockers
8. Exact next task for the next agent
9. Git commit/PR/issue references

## Branch and PR conventions

- `claude/spec-*` for architecture/specification work
- `codex/m1-*`, `codex/tv-*`, `codex/pine-*` for implementation
- `gemini/tv-recon-*`, `gemini/pine-audit-*` for research and validation

PR title prefixes:
- `[SPEC]`
- `[CORE]`
- `[TV]`
- `[PINE]`
- `[RESEARCH]`
- `[DOCS]`

## Merge gates

A PR may merge only when:
- scope matches its GitHub issue
- tests pass
- documentation is updated
- no unresolved high-severity review comments remain
- changes preserve non-blocking 24/7 operation
- secrets and browser profiles are not committed
- statistical outputs are not described as credible until methodology review is complete

## User responsibilities

Niels only needs to:
- maintain the TradingView Premium login in the `Flasherz` Chrome profile
- keep `NRL_MASTER` available and avoid changing it without updating the setup contract
- run Gateway installation commands that require SSH/root access
- answer queued interventions when convenient
- approve major changes in research priorities

Agents must not wait for Niels during 02:00–14:00 UTC. They must save state, create an intervention, and continue with another runnable task.

## First delegation order

1. Send the first Claude assignment.
2. In parallel, send the first Gemini assignment.
3. After Claude's Milestone 1 specification is merged or accepted, send the first Codex assignment.
4. When Codex opens the Milestone 1 PR, send Claude the adversarial review assignment.
5. After Milestone 1 merges, begin the TradingView vertical slice with Gemini reconnaissance feeding Codex implementation.
