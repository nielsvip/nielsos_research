# NielsOS Research Lab — Codex Execution Chronogram

## Mission

Build a 24/7 autonomous TradingView research platform that tests NielsOS indicators, parameter ranges, symbols, timeframes, market regimes, and long/short hypotheses; stores all runs in PostgreSQL; survives browser or server failures; never blocks on human input; and produces credibility scores that can later influence production trading.

The system must be able to run unattended from **02:00–14:00 UTC** and continue operating 24/7 outside that window. Any unresolved browser state, TradingView prompt, login issue, Pine compile error, or ambiguous condition must be checkpointed into SQL as an intervention and the worker must continue with another runnable job whenever possible.

## Current infrastructure and constraints

- GitHub repository: `nielsvip/nielsos_research`
- Mac development folder: `~/Documents/nielsos_research`
- Gateway deployment folder: `/home/niels/nielsos_research`
- Gateway: `157.90.18.35`, Ubuntu x86, 2 vCPU, 4 GB RAM, 40 GB local disk
- TradingView plan: Premium
- Dedicated Chrome profile: `Flasherz` (`flasherzcolombia@gmail.com`)
- One TradingView account only
- One dedicated TradingView layout: `NRL_MASTER`
- Existing production systems must remain isolated from research
- Gateway already pulls prices/klines and rsyncs to S1 and MacBook
- PostgreSQL is required; do not use SQLite as the primary database
- Browser automation should use Playwright unless a hard blocker is proven
- Do not require a second TradingView account
- Do not assume unlimited TradingView concurrency
- Avoid resource-heavy local backtesting because S1 and MacBook already encounter OOM pressure

## Source-of-truth universes

### Stocks

Use the existing `SECTOR_MAP` and `SECTOR_GROUPS` from `config_tradier.py` as the stock universe source. The research system must import or generate normalized universe records from that configuration rather than duplicate the list manually.

Required initial stock universe groups:

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

Required sector-group rollups:

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

### Crypto

Initial crypto universe is the existing `symbols.json` production list. The system must support dynamic universes from `ez_rankings.py`, including:

- Long-term winners
- Long-term losers
- Short-term winners
- Short-term losers
- Personal tradeable universe
- FLZ short shortlist

Initial FLZ shortlist:

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

The importer must tolerate USDT/USDC naming differences and store canonical exchange-qualified TradingView symbols separately from internal production symbols.

## Research principles

1. TradingView performs the expensive historical indicator calculations.
2. Playwright orchestrates symbols, timeframes, parameters, layouts, screenshots, and result capture.
3. PostgreSQL is the durable queue, state store, knowledge base, and audit trail.
4. Excel is a reporting layer, not the system of record.
5. Every experiment is reproducible and immutable after creation.
6. A rerun with changed code, Pine version, layout, date range, parameters, or universe creates a new run/version.
7. No worker may block indefinitely waiting for a person.
8. Failed or ambiguous work must be checkpointed and requeued or moved to intervention status.
9. All research results must distinguish crypto from stocks.
10. Crypto is the older and more evolved implementation; crypto-only features should be marked as stock migration candidates where applicable.
11. Timeframe performance must be measured rather than assumed.
12. Parameter robustness matters more than a single best setting.
13. Results must be separated by long, short, regime, asset class, timeframe, and horizon.
14. MFI is primarily a long-side feature.
15. For shorts, use RSI for price weakness and relative volume/volume participation as a separate confirmation; do not treat low MFI as automatically favorable for shorts.

## Initial feature set

The first end-to-end vertical slice must test:

1. WaveTrend velocity
2. Donchian position
3. Relative volume
4. RSI
5. MFI

Initial production timeframes:

- 1m
- 3m
- 15m
- 1h
- 4h
- 1D

Secondary timeframes may be enabled later:

- 2m
- 5m
- 30m
- 2h
- 12h
- 1W

Do not run every possible timeframe initially. Start with the six production timeframes and let measured credibility determine later expansion.

## Required repository structure

```text
nielsos_research/
├── README.md
├── CODEX_CHRONOGRAM.md
├── ARCHITECTURE.md
├── ROADMAP.md
├── pyproject.toml
├── requirements.txt
├── .env.example
├── .gitignore
├── docker-compose.yml
├── config/
│   ├── settings.py
│   ├── logging.yaml
│   ├── universes.yaml
│   └── feature_registry.yaml
├── database/
│   ├── schema.sql
│   ├── migrations/
│   ├── models.py
│   └── repository.py
├── scheduler/
│   ├── scheduler.py
│   ├── queue_manager.py
│   ├── leasing.py
│   └── recovery.py
├── workers/
│   ├── worker_base.py
│   ├── tv_worker.py
│   └── maintenance_worker.py
├── browser/
│   ├── playwright_manager.py
│   ├── tradingview_page.py
│   ├── selectors.py
│   ├── screenshots.py
│   └── recovery.py
├── pine/
│   ├── nrl_research_framework.pine
│   ├── feature_modules/
│   └── README.md
├── experiments/
│   ├── manifests/
│   ├── loader.py
│   ├── expander.py
│   └── validator.py
├── ingestion/
│   ├── parser.py
│   ├── normalizer.py
│   └── importer.py
├── credibility/
│   ├── scoring.py
│   ├── stability.py
│   ├── regimes.py
│   └── correlations.py
├── dashboard/
│   ├── app.py
│   ├── templates/
│   └── static/
├── universes/
│   ├── stock_importer.py
│   ├── crypto_importer.py
│   └── symbol_normalizer.py
├── scripts/
│   ├── install_gateway.sh
│   ├── bootstrap_db.sh
│   ├── run_worker.sh
│   ├── run_scheduler.sh
│   └── smoke_test.sh
├── systemd/
│   ├── nrl-scheduler.service
│   ├── nrl-worker@.service
│   └── nrl-dashboard.service
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
└── docs/
    ├── operations.md
    ├── tradingview_setup.md
    ├── experiment_spec.md
    ├── credibility_method.md
    └── agent_handoff.md
```

## Database minimum schema

Codex agents must implement migrations for at least these tables:

- `features`
- `feature_versions`
- `universes`
- `universe_symbols`
- `experiments`
- `experiment_runs`
- `run_symbols`
- `parameter_sets`
- `workers`
- `worker_heartbeats`
- `job_leases`
- `checkpoints`
- `results`
- `statistics`
- `screenshots`
- `interventions`
- `pine_versions`
- `layout_versions`
- `credibility_scores`
- `feature_correlations`
- `research_notes`
- `audit_events`

Required states:

- queued
- leased
- running
- checkpointed
- completed
- retryable_failed
- blocked_intervention
- permanently_failed
- cancelled

Lease behavior:

- Jobs are claimed with an expiring lease.
- Heartbeats renew the lease.
- Expired leases are recoverable.
- A worker crash must not permanently strand a job.
- Retry count and last error are durable.
- Jobs that need human help move to `blocked_intervention`; the worker continues with another job.

## Pine research harness requirements

The universal Pine framework must support configurable:

- Feature under test
- Feature parameters
- Long hypothesis threshold
- Short hypothesis threshold
- Forward horizons
- Regime labels
- Date range
- Session filters for stocks
- Multiple timeframes
- Long and short statistics separately
- Sample count
- Win rate
- Average and median forward return
- MFE
- MAE
- Profit factor where applicable
- Drawdown where applicable
- Stability by segment

Initial features must be modular and selectable from one script rather than five unrelated scripts.

Pine must not attempt to write local files directly. The browser worker must capture values from supported TradingView UI surfaces, exported data, Pine tables, Strategy Tester output, alerts/webhooks, or another tested machine-readable route. OCR is a last resort only.

## Browser automation requirements

- Use the dedicated Chrome profile `Flasherz`.
- Open or restore the `NRL_MASTER` TradingView layout.
- Maintain one primary automated TradingView session.
- Do not interfere with the user's separate stock-monitoring screens.
- Prefer a dedicated browser instance launched with its own user-data directory copy or persistent context.
- Detect login expiration, popups, Pine compile errors, missing layout, missing symbol, rate limiting, stale UI, and timeout.
- Capture screenshots on failure and at major checkpoints.
- Store screenshot paths and metadata in PostgreSQL.
- Never wait indefinitely for a prompt.
- On unresolved UI state, write an intervention, preserve state, and continue another job if possible.
- Browser selectors must be centralized and versioned.
- Include a dry-run mode that does not submit or alter irreversible account state.

## Credibility requirements

Every feature must eventually receive separate credibility scores for:

- Crypto overall
- Stocks overall
- Long
- Short
- Bull
- Bear
- Range
- High volatility
- Low volatility
- Compression
- Expansion
- Each tested timeframe
- Each tested forward horizon
- Cross-symbol robustness
- Cross-sector robustness
- Parameter stability
- Sample-size adequacy
- Recency stability

Credibility must never be only win rate. The scoring design must combine at least:

- Effect size
- Sample size
- Statistical confidence
- Stability across symbols
- Stability across timeframes
- Stability across regimes
- Parameter sensitivity
- Outlier dependence
- Redundancy/correlation with existing features

Store raw components and final score separately so the score remains explainable.

## Multi-agent work allocation

Codex should spawn agents in parallel using the following ownership boundaries.

### Agent A — Architecture and contracts

Deliverables:

- `ARCHITECTURE.md`
- package boundaries
- shared data contracts
- experiment manifest schema
- state-machine definitions
- error taxonomy

Must finish first-pass contracts before other agents finalize interfaces.

### Agent B — PostgreSQL and migrations

Deliverables:

- `database/schema.sql`
- migration framework
- queue/lease SQL
- repository layer
- integration tests using disposable PostgreSQL

### Agent C — Scheduler and worker lifecycle

Deliverables:

- job claiming
- lease renewal
- heartbeats
- retry policy
- stale-worker recovery
- intervention routing
- graceful shutdown

### Agent D — Playwright and TradingView driver

Deliverables:

- persistent Chrome profile handling
- TradingView login/session restoration
- layout restore
- symbol/timeframe/input control
- screenshots
- selector abstraction
- UI timeout/recovery behavior

### Agent E — Pine framework

Deliverables:

- universal research harness
- initial five features
- forward-return and MFE/MAE statistics
- long/short asymmetry
- regime labels
- visible result table suitable for automated extraction

### Agent F — Universe ingestion

Deliverables:

- stock sector-map importer
- crypto symbols importer
- ranking-universe importer interface
- symbol normalization
- TradingView exchange-qualified mapping

### Agent G — Results ingestion and credibility

Deliverables:

- result parser
- normalized result records
- credibility component calculations
- first scoring formula
- parameter stability and correlation interfaces

### Agent H — Dashboard and interventions

Deliverables:

- queue overview
- worker heartbeat view
- current job view
- failure/intervention inbox
- experiment status
- initial credibility table

### Agent I — Deployment and operations

Deliverables:

- Gateway install script
- Docker/PostgreSQL setup
- Playwright browser dependencies
- systemd units
- log rotation
- backup/restore
- resource limits for 4 GB RAM
- smoke-test script

### Agent J — Testing and integration

Deliverables:

- unit test plan
- integration fixtures
- fake TradingView page for deterministic tests
- end-to-end smoke test
- acceptance checklist

## Chronogram

This chronogram is dependency-based. Agents should work in parallel where possible. Calendar estimates are planning targets, not guarantees.

### Phase 0 — Repository bootstrap (Day 0)

Owners: A, I

Tasks:

- Create repository skeleton.
- Add `pyproject.toml`, `.env.example`, `.gitignore`, formatting, linting, and test configuration.
- Add architecture and contributor handoff documents.
- Establish branch/PR conventions.

Exit criteria:

- Clean install in a fresh Python environment.
- `pytest` runs.
- `ruff` or equivalent runs.
- Repository documents the entire planned system.

### Phase 1 — Contracts and SQL core (Days 1–2)

Owners: A, B, C

Parallel tasks:

- Finalize experiment manifest schema.
- Implement PostgreSQL schema and migrations.
- Implement job states, leases, heartbeats, retries, and interventions.
- Implement repository methods and transaction boundaries.

Exit criteria:

- Multiple simulated workers can claim jobs without duplicates.
- Expired leases are reclaimed.
- Blocked jobs do not stop runnable jobs.
- Database can be rebuilt from migrations.

### Phase 2 — Universe ingestion and manifests (Days 1–3)

Owners: F, A

Parallel tasks:

- Import `SECTOR_MAP` and `SECTOR_GROUPS` from `config_tradier.py`.
- Import `symbols.json`.
- Add interface for `ez_rankings.py` winner/loser lists.
- Normalize internal symbols to TradingView symbols.
- Create initial manifests for the five features and six production timeframes.

Exit criteria:

- SQL contains stock and crypto universes.
- Each symbol has asset class, sector/group where known, internal symbol, TradingView symbol, and active status.
- Manifest expansion creates deterministic jobs.

### Phase 3 — Browser proof of control (Days 2–5)

Owner: D

Tasks:

- Launch persistent Chromium/Chrome context using the Flasherz profile strategy.
- Open TradingView.
- Restore `NRL_MASTER`.
- Change one symbol.
- Change one timeframe.
- capture a screenshot.
- Persist browser session metadata and checkpoint.

Exit criteria:

- A smoke test runs BTCUSDC on one timeframe and captures a screenshot.
- Browser restart restores the session.
- Login expiry creates an intervention instead of blocking.

### Phase 4 — Pine vertical slice (Days 3–7)

Owner: E

Tasks:

- Implement the universal Pine harness.
- Add WaveTrend velocity first.
- Add one parameter grid.
- Add long and short hypotheses.
- Add 1, 3, 5, 10, and 20-bar forward horizons.
- Display machine-readable or consistently parseable results.

Exit criteria:

- Pine compiles on TradingView.
- Results can be captured for one symbol and timeframe.
- Long and short outputs are distinct.
- Results include sample count, average return, MFE, and MAE.

### Phase 5 — End-to-end first experiment (Days 5–9)

Owners: B, C, D, E, G, J

Tasks:

- Queue one WT-velocity experiment.
- Worker claims it.
- Browser configures TradingView.
- Pine computes the result.
- Parser stores results.
- Worker marks the run complete.
- Dashboard displays it.

Exit criteria:

- A full run is reproducible from SQL.
- Failure at each step is recoverable.
- No manual database editing is required.

### Phase 6 — Initial five-feature pack (Days 7–14)

Owners: E, G, J

Tasks:

- Add Donchian position.
- Add relative volume.
- Add RSI.
- Add MFI.
- Encode MFI long preference and RSI plus volume short logic.
- Run across BTC, ETH, SOL and one stock sample set.
- Run across 1m, 3m, 15m, 1h, 4h, and 1D.

Exit criteria:

- All five features run through the same harness.
- Results are separated by asset class, side, timeframe, regime, and horizon.
- Parameter grids are configurable without controller code changes.

### Phase 7 — Autonomous operation (Days 10–18)

Owners: C, D, H, I, J

Tasks:

- Install scheduler, worker, PostgreSQL, and dashboard on Gateway.
- Configure 24/7 operation.
- Ensure no-human window from 02:00–14:00 UTC.
- Add worker heartbeat monitoring.
- Add automated restart.
- Add intervention inbox.
- Add retry and stale-job recovery.
- Add disk and memory safeguards.

Exit criteria:

- System runs at least 12 unattended hours.
- Simulated browser crash resumes safely.
- Simulated login expiry creates an intervention and queue continues where possible.
- Gateway stays within safe memory limits.

### Phase 8 — Credibility v1 (Days 12–21)

Owner: G

Tasks:

- Aggregate raw results.
- Compute side/timeframe/regime-specific credibility components.
- Add sample-size and stability penalties.
- Add parameter sensitivity.
- Add cross-symbol robustness.
- Publish explainable credibility records.

Exit criteria:

- Each tested feature has a reproducible credibility score.
- Raw components are inspectable.
- Scores distinguish crypto from stocks and long from short.

### Phase 9 — Dashboard and operational handoff (Days 14–24)

Owners: H, I, J

Tasks:

- Worker/queue dashboard.
- Current experiment view.
- Intervention inbox.
- Failure screenshots.
- Credibility table.
- Operations manual.
- Backup and restore test.

Exit criteria:

- User can see what is running and what needs attention.
- Another agent can deploy and operate the system from repository documentation alone.

### Phase 10 — Production research expansion (Day 21 onward)

Tasks:

- Import the full metric dictionary.
- Add crypto-only versus stock-only flags.
- Add migration-candidate workflow.
- Add feature correlation and redundancy analysis.
- Add adaptive scheduling based on missing confidence and information gain.
- Add weekly research summaries.
- Add workbook export.
- Add validated-weight export for the production trading engine.

This phase must not be allowed to delay the initial working five-feature system.

## Critical path

The shortest path to a usable system is:

1. Repository bootstrap
2. Database queue and leases
3. Browser proof of control
4. Pine WT-velocity vertical slice
5. Result parser
6. End-to-end test
7. Gateway deployment
8. Twelve-hour unattended run
9. Add remaining four initial features
10. Credibility v1

Agents must prioritize the critical path over optional dashboards, AI helpers, or advanced optimization.

## Codex spawning instructions

Codex should:

1. Create one parent tracking issue for each phase.
2. Create one branch per agent/workstream.
3. Require each agent to read this file and `ARCHITECTURE.md` before coding.
4. Require interface proposals in PR descriptions when shared contracts change.
5. Avoid multiple agents editing the same file concurrently.
6. Merge contracts and migrations before dependent modules.
7. Keep PRs small enough to review and test independently.
8. Add tests with each feature, not at the end.
9. Record unresolved assumptions in `docs/agent_handoff.md`.
10. Never leave required work only in chat or issue comments; commit it to the repository.

Recommended first agent launch set:

- Agent A: architecture/contracts
- Agent B: database/migrations
- Agent C: scheduler/worker lifecycle
- Agent D: Playwright proof of control
- Agent F: universe importers
- Agent I: Gateway bootstrap

Launch Agent E after Agent A publishes the experiment contract. Launch G and H once the first result schema is stable. Agent J should start immediately with fixtures and acceptance tests and continue throughout.

## Acceptance test suite

The system is not considered ready until all of these pass:

1. Two workers cannot claim the same job.
2. Killing a worker causes its expired job to be reclaimed.
3. A blocked intervention does not stop unrelated jobs.
4. Browser restart restores the dedicated session.
5. Missing TradingView login creates an intervention.
6. Missing symbol creates a durable error and moves on.
7. Pine compile failure stores the error and screenshot.
8. A complete WT-velocity run is stored with reproducibility metadata.
9. A run can be repeated from its experiment ID.
10. Results distinguish crypto/stocks and long/short.
11. Results distinguish all six initial timeframes.
12. MFI and RSI/volume asymmetry is represented in manifests and scoring.
13. Gateway survives a 12-hour unattended test.
14. Restarting PostgreSQL, scheduler, or worker does not corrupt queue state.
15. Disk usage, screenshot retention, and logs are bounded.
16. Another agent can deploy the system using only repository documentation.

## Resource safeguards for Gateway

Because Gateway has 4 GB RAM:

- Start with one TradingView browser worker only.
- Limit Chromium processes where practical.
- Configure PostgreSQL conservatively.
- Use log rotation.
- Compress or expire old screenshots.
- Do not run heavy local historical backtests.
- Do not load the full crypto history into memory.
- Add memory and disk health checks.
- Defer multiple browser workers until measured safe.

## Definition of the first usable release

`v0.1.0` is reached when:

- PostgreSQL queue is durable.
- One Playwright TradingView worker runs on Gateway.
- `NRL_MASTER` is controllable.
- WT velocity can be tested on at least BTCUSDC, ETHUSDC, and SOLUSDC.
- At least 1m, 3m, 15m, 1h, 4h, and 1D are supported.
- Results are stored in SQL.
- Failures and interventions do not block the queue.
- The system completes a 12-hour unattended run.

`v0.2.0` adds Donchian position, relative volume, RSI, and MFI.

`v0.3.0` adds credibility scoring, dashboard completeness, stock-sector universes, and dynamic ranking universes.

## Immediate human setup checklist

- Create or confirm TradingView layout named `NRL_MASTER`.
- Confirm TradingView is logged in under Chrome profile `Flasherz`.
- Keep the existing monitoring layouts separate.
- Ensure Gateway has the repository cloned at `/home/niels/nielsos_research`.
- Ensure Codex agents have repository access.
- Provide `config_tradier.py`, `symbols.json`, and any ranking-output file paths to the repository through safe configuration or documented mounts; do not commit secrets.
- Do not commit TradingView passwords, Gmail credentials, SSH private keys, API keys, or browser cookies.

## Non-goals for the first release

- Multiple TradingView accounts
- Multiple simultaneous browser workers
- Full 351-metric implementation
- Automatic production trading changes
- Local exhaustive Python backtesting
- OCR-based result extraction unless every better option fails
- Fully autonomous AI experiment invention before the core pipeline is stable

## Final handoff rule

Everything promised, decided, discovered, or required for implementation must be committed into this repository as code, configuration, tests, or Markdown. No critical system knowledge may exist only in a ChatGPT conversation.
