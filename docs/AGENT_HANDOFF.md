# Agent Handoff

This repository is the sole durable handoff for NielsOS Research Lab. Before changing code, agents should read:

1. `docs/CHAT_PROMISES.md`
2. `ARCHITECTURE.md`
3. `ROADMAP.md`
4. `docs/TRADINGVIEW_SETUP.md`
5. `docs/GATEWAY_INSTALL.md`
6. existing manifests and Pine harness

## Current repository state

The repository already contains early commits for:

- Gateway installation guidance;
- TradingView setup contract;
- a Codex Milestone 1 handoff prompt;
- a first WaveTrend experiment manifest;
- Universal Pine Research Harness v0.1.

Do not assume those early artifacts satisfy the full scope. Compare them against `docs/CHAT_PROMISES.md` and create tracked work for gaps.

## Immediate implementation order

1. Audit current tree and document actual versus promised functionality.
2. Complete Milestone 1 with a real PostgreSQL migration, typed configuration, structured logging, job leases, heartbeats, checkpoints, retry policy, stale-worker recovery, and intervention queue.
3. Add tests covering atomic job claims, lease renewal, stale recovery, idempotent result writes, and nonblocking intervention behavior.
4. Implement one conservative Playwright worker using the persistent Flasherz profile and `NRL_MASTER` layout.
5. Validate the existing Pine harness for correctness, especially event alignment and forward-return indexing, before using its statistics as evidence.
6. Implement initial end-to-end campaigns for Donchian Position, WT Velocity, Relative Volume, RSI, and MFI across Tier 1 timeframes.

## Definition of done for any feature

A feature is not complete unless it includes:

- code;
- configuration or manifest;
- database representation;
- tests where applicable;
- operational documentation;
- failure and recovery behavior;
- observability/logging;
- roadmap/status update;
- no undocumented manual step.

## Safety and account constraints

- Only one TradingView Premium account is available.
- Begin with a single active TradingView browser worker.
- Do not create multiple aggressive sessions without explicit evidence that it is safe and compatible with the account.
- Never store account passwords, browser cookies, SSH private keys, or database passwords in Git.
- Persistent browser profile paths are configuration values and must be local secrets/environment settings.
- Never allow a modal, login prompt, unknown popup, or uncertain state to block the queue indefinitely.

## Research correctness

- Separate long and short evidence.
- MFI is not the default short sensor; shorts use RSI plus separate volume confirmation.
- Separate crypto and stocks.
- Segment results by timeframe and regime.
- Record feature/Pine versions and exact parameters for every run.
- Treat the current Pine v0.1 statistics as provisional until reviewed and tested.

## Keeping the repository authoritative

Whenever a user decision changes architecture, universes, timeframes, metrics, deployment, or operational constraints, update the appropriate repository document in the same change. The goal is that another agent can resume work from GitHub alone.
