# Codex prompt — Milestone 1 hardening

Work in the current `nielsos_research` repository.

## Goal

Turn the initial scaffold into a tested, runnable Milestone 1 without changing the architecture:

- PostgreSQL is the source of truth.
- Workers never block on human input.
- Jobs use `FOR UPDATE SKIP LOCKED`, leases, retries, and checkpoints.
- TradingView computation is offloaded to Pine; Gateway performs orchestration only.
- One dedicated Linux Chrome profile and one `NRL_MASTER` layout are used initially.

## Tasks

1. Run `ruff` and `pytest`; fix all issues.
2. Add unit tests for queue state transitions using an isolated PostgreSQL test database.
3. Add structured logging with `structlog`.
4. Add a safe schema installer that can run the multi-statement `database/schema.sql` reliably.
5. Ensure UUIDs and JSON values serialize cleanly in the worker.
6. Add graceful SIGTERM/SIGINT handling.
7. Add a worker-level timeout around every TradingView action.
8. Add a systemd service and Xvfb service template, but do not enable them automatically.
9. Add `scripts/doctor.py` checking PostgreSQL, Chrome, profile directory, display, disk, RAM, and TradingView URL reachability.
10. Update docs with exact commands and report any assumption that still requires Niels to decide.

Do not add a dashboard, credibility engine, or broad indicator implementation yet. Keep the repository runnable after every commit.
