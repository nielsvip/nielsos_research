# Chat Commitments and Scope

This document captures the requirements and promises agreed during the architecture discussion so future agents can work without needing the original chat.

## Mission

Build a 24/7 autonomous research platform that uses TradingView/Pine as the main historical computation engine, minimizing load on S1 and the MacBook. The platform must qualify the credibility of every metric across asset class, direction, timeframe, market regime, parameter range, and decision context.

## Infrastructure and access assumptions

- Repository: `nielsvip/nielsos_research`.
- MacBook checkout: `~/Documents/nielsos_research`.
- Gateway checkout: `/home/niels/nielsos_research`.
- Gateway: `157.90.18.35`, Ubuntu x86, CX22, 2 vCPU, 4 GB RAM, 40 GB local disk.
- Gateway already pulls prices and klines and rsyncs them to S1 and the MacBook.
- TradingView plan: Premium.
- Only one Premium TradingView account is available.
- Dedicated Chrome profile: `Flasherz`.
- Chrome/Google identity: `flasherzcolombia@gmail.com`.
- Dedicated TradingView layout: `NRL_MASTER`.
- User normally uses TradingView for three monitoring screens of eight stock tickers; research automation must coexist with this single account and avoid corrupting the monitoring setup.

## Availability requirements

- Run 24/7.
- From 02:00–14:00 UTC, require no human input.
- A task requesting human input must never stall the whole platform.
- On ambiguity, login expiration, popup, Pine error, layout drift, or selector failure:
  1. checkpoint state;
  2. record an intervention with screenshot and structured context;
  3. release or quarantine the affected browser context;
  4. continue with another runnable job, opening a new window/context when appropriate;
  5. allow the user to answer interventions later.
- Recover automatically from Gateway reboot, Chrome crash, worker death, stale heartbeat, and interrupted jobs.

## Research model

Pipeline:

Indicator/sensor → engineered feature → hypothesis → Pine experiment → statistics → credibility score → production recommendation.

TradingView is the research laboratory, not the production trading engine. Python production code remains the implementation used for live trading. Pine should offload large historical sweeps and visual validation.

## Initial metrics

The first complete vertical slice must support:

1. Donchian Position
2. WaveTrend Velocity
3. Relative Volume
4. RSI
5. MFI

### Directional asymmetry rule

- MFI is preferable for longs because volume-backed rising money flow supports accumulation.
- MFI must not be treated as the default short equivalent.
- For shorts, falling RSI indicates price weakness, while separate volume evidence determines whether sellers are participating.
- Short research should therefore test RSI together with relative volume, selling volume, and volume acceleration.
- Credibility must be scored separately for long and short use.

## Crypto versus stocks

- Crypto is the older and more evolved indicator implementation.
- Stocks are a downstream implementation that may receive selected crypto metrics after evidence shows they are useful.
- Every metric record must distinguish:
  - crypto available;
  - stock available;
  - shared;
  - crypto-only;
  - stock-only;
  - migration candidate;
  - migration impossible/not applicable.
- Migration from crypto to stocks must be evidence-driven.

## Timeframe research

Tier 1 (default): `1m`, `3m`, `15m`, `1h`, `4h`, `1D`.

Tier 2 after evidence: `2m`, `5m`, `30m`, `2h`, `12h`, `1W`.

Tier 3 research-only: `10m`, `45m`, `8h`, `3D`.

Do not assume one global best timeframe. Credibility and parameter recommendations must be segmented by timeframe. Indicators may be promoted or excluded from timeframes based on evidence.

## Universes

### Crypto

Initial universe source is the user's existing `symbols.json`, approximately 200 Binance perpetual symbols, including crypto assets and a few tokenized stock symbols. The research system should ingest this file rather than requiring manually duplicated TradingView sector lists.

Dynamic universes from `ez_rankings` should eventually include:

- long-term winners;
- long-term losers;
- short-term winners;
- short-term losers;
- active/tradeable symbols.

Initial short-focused `flz` shortlist:

- BTCUSDC
- BTCDOMUSDT
- ETHUSDC
- BNBUSDC
- SOLUSDC
- XRPUSDC
- HYPEUSDT
- DOGEUSDC
- ZECUSDC
- WLDUSDC

Crypto sector taxonomy can be added later (AI, L1, L2, DeFi, gaming, meme, RWA, perps, etc.).

### Stocks

The authoritative source is `SECTOR_MAP` and `SECTOR_GROUPS` in `config_tradier.py`. Do not manually maintain duplicate stock classifications.

Current sectors include:

- TECH
- TECH_SW
- TECH_CONS
- ENERGY_OIL
- ENERGY_NAT
- NUCLEAR
- MINING_GOLD
- MINING_BASE
- DEFENSE
- CRYPTO
- AGRICULTURE
- SHIPPING
- HEALTH
- CONSUMER
- FINANCIAL
- INDUSTRIAL
- TELECOM
- INDEX
- MEME

Sector groups include:

- GROWTH
- COMMODITIES
- ENERGY_ALT
- DEFENSE
- CRYPTO
- SHIPPING
- DEFENSIVE
- FINANCIAL
- CYCLICAL
- INDEX
- SPECULATIVE

The research system should generate database universes and, where useful, TradingView watchlists from this source.

## Experiment manifests

Experiments are declarative YAML, not one-off controller code. Each manifest can define:

- stable experiment ID;
- feature and feature version;
- hypothesis;
- asset classes;
- universes;
- symbols;
- directions;
- timeframes;
- parameter grid;
- thresholds;
- forward horizons;
- date range;
- regimes;
- priority;
- retry and timeout policy;
- Pine harness version;
- expected output schema.

The generic scheduler expands manifests into reproducible jobs and run units.

## Queue and worker behavior

Use PostgreSQL, not SQLite.

Workers must use leases and heartbeats. A worker claims one runnable unit atomically, records ownership and lease expiry, checkpoints at symbol/timeframe/parameter/output stages, and renews its lease. Stale units are requeued.

The queue should optimize UI transitions and information gained per hour. Prefer batching to minimize expensive Pine/layout/input changes. Queue ordering may consider:

- feature importance;
- missing confidence;
- expected information gain;
- runtime cost;
- insufficient sample count;
- parameter coverage;
- regime coverage;
- cross-asset coverage.

## TradingView automation

Use Playwright with the persistent Flasherz Chrome profile.

Controller responsibilities:

- launch/reconnect browser;
- open `NRL_MASTER`;
- restore known baseline state;
- select symbol;
- select timeframe;
- open indicator settings;
- set Pine inputs;
- wait for deterministic completion marker;
- capture the result table/export;
- save screenshots and diagnostics;
- validate the active symbol, timeframe, feature, parameters, and output version;
- recover or create an intervention rather than block.

Do not depend solely on brittle screen coordinates. Prefer accessible roles, labels, text, testable DOM selectors, and validation after each action. Keep a selector registry and page-state detectors.

One account means conservative concurrency. Start with one active TradingView worker/browser context. Add parallel contexts only if proven safe under the subscription and session behavior.

## Pine research framework

Maintain one universal Pine harness rather than hundreds of unrelated scripts. Feature modules plug into it.

The harness should eventually report:

- samples;
- wins;
- win rate;
- mean/median forward return;
- standard deviation;
- Sharpe-like statistic;
- profit factor where event definitions support it;
- MFE;
- MAE;
- forward returns at configured horizons;
- long/short result separation;
- regime buckets;
- parameter identity;
- feature/version identity;
- output schema version;
- deterministic completion marker.

Pine output must be machine-readable enough for DOM extraction or robust screenshot/table parsing. OCR is a last resort.

## SQL knowledge base

Required conceptual tables include:

- features / metrics;
- feature versions;
- dependencies;
- consumers;
- hypotheses;
- manifests;
- experiments;
- experiment runs;
- run units/jobs;
- symbols;
- universes;
- universe membership history;
- workers;
- worker heartbeats or current leases;
- checkpoints;
- results;
- result statistics;
- screenshots/artifacts;
- interventions;
- intervention answers;
- Pine versions;
- TradingView layouts;
- browser/runtime versions;
- research notes/memory;
- credibility snapshots;
- feature correlations;
- lifecycle transitions.

Use JSONB for flexible parameters and metadata, but preserve strongly typed columns for fields used in scheduling, filtering, aggregation, and constraints.

## Credibility

Every metric must earn separate credibility scores by:

- crypto versus stocks;
- symbol/universe/sector;
- long versus short;
- timeframe;
- bull/bear/range;
- compression/expansion;
- high/low volatility;
- above/below SMA200 or other agreed trend regime;
- entry/add/reduce/exit/position-size use case;
- parameter neighborhood;
- sample size and stability;
- cross-asset robustness;
- out-of-sample stability;
- redundancy/correlation with existing features.

Credibility is evidence, not subjective importance. The system may also store subjective information value and computational cost separately.

Feature lifecycle:

Idea → Implemented → Experimenting → Validated → Production → Core → Deprecated.

## Results and reporting

The platform should provide:

- durable SQL results;
- CSV/JSON/Parquet exports where useful;
- live dashboard of workers, queue, progress, failures, interventions, and credibility;
- Excel workbook/database export integrating the metrics dictionary and research results;
- weekly research summary;
- permanent research ledger and notes;
- correlation/redundancy reports;
- recommended migration from crypto to stocks;
- recommended production weights or deprecation candidates.

## Milestones promised

### Milestone 1

- repository skeleton;
- PostgreSQL schema;
- configuration system;
- logging;
- generic worker framework;
- leases, retries, checkpoints, interventions.

### Milestone 2

- Playwright;
- persistent profile management;
- TradingView controller;
- screenshot capture;
- selectors and state validation;
- crash recovery.

### Milestone 3

- universal Pine framework;
- feature modules;
- YAML manifests;
- experiment queue expansion;
- initial five-feature campaign.

### Milestone 4

- result ingestion;
- credibility engine;
- dashboard;
- workbook/export integration.

## Required documentation for agents

The repository must explain:

- architecture and invariants;
- deployment on Gateway;
- local development;
- TradingView one-time setup;
- database migration and backup;
- how to create a feature module;
- how to create a manifest;
- how to queue, pause, resume, retry, or cancel work;
- how interventions are resolved;
- how credibility is computed;
- how crypto and stock universes are imported;
- what remains unimplemented.

Agents must update documentation and roadmap as implementation changes. Do not leave critical assumptions only in chat messages.
