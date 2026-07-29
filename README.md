# NielsOS Research Lab

NielsOS Research Lab is a 24/7 research platform that uses TradingView/Pine for computation and PostgreSQL for orchestration, persistence, interventions, and credibility scoring.

## Core goals

- Run continuously on the Gateway server.
- Never block on human input.
- Save state and move on when TradingView needs intervention.
- Test metrics across symbols, parameter ranges, market regimes, and timeframes.
- Distinguish crypto from stocks; crypto is the older, more evolved implementation.
- Treat MFI as primarily useful for long research, while short research prefers RSI plus relative-volume confirmation.
- Produce reproducible, machine-readable evidence for every metric.

## Initial architecture

- PostgreSQL queue and research knowledge base
- Python scheduler and worker framework
- Playwright TradingView controller
- One immutable TradingView layout: `NRL_MASTER`
- One dedicated Chrome profile: `Flasherz`
- Universal Pine research harness
- YAML experiment manifests
- Credibility engine and dashboard

## Current milestone

Milestone 1 establishes the repository, schema, configuration, logging, queue, worker lifecycle, intervention model, and TradingView connection scaffolding.

See `docs/SETUP_GATEWAY.md` and `docs/TRADINGVIEW_SETUP.md`.
