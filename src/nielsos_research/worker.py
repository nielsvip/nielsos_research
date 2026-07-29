from __future__ import annotations

import asyncio
import json
import platform
import traceback
from typing import Any

from .config import settings
from .queue import (
    claim_job,
    complete_job,
    create_intervention,
    fail_or_requeue,
    heartbeat,
    mark_running,
    register_worker,
    release_expired_leases,
    save_checkpoint,
)
from .tradingview import HumanInterventionRequired, TradingViewSession


async def execute_job(session: TradingViewSession, job: dict[str, Any]) -> None:
    job_id = str(job["id"])
    heartbeat(settings.worker_id, "running", job_id)
    mark_running(job_id, {"phase": "starting"})
    try:
        await session.connect()
        save_checkpoint(job_id, {"phase": "connected"})
        await session.set_symbol(job["symbol"])
        save_checkpoint(job_id, {"phase": "symbol_set", "symbol": job["symbol"]})
        await session.set_timeframe(job["timeframe"])
        save_checkpoint(job_id, {"phase": "timeframe_set", "timeframe": job["timeframe"]})
        screenshot = await session.capture(f"job_{job_id}")
        metrics = {"status": "smoke_complete"}
        raw = {"job": {k: str(v) if k == "id" else v for k, v in job.items()}}
        complete_job(job_id, metrics, raw, screenshot)
    except HumanInterventionRequired as exc:
        screenshot = None
        try:
            screenshot = await session.capture(f"intervention_{job_id}")
        except Exception:
            pass
        create_intervention(job_id, settings.worker_id, exc.kind, str(exc), exc.context, screenshot)
        fail_or_requeue(job_id, str(exc), blocked=True)
    except Exception as exc:
        fail_or_requeue(job_id, f"{exc}\n{traceback.format_exc()}")
    finally:
        heartbeat(settings.worker_id, "idle", None)


async def run_forever(poll_seconds: float = 5.0) -> None:
    register_worker(settings.worker_id, platform.node(), settings.chrome_profile_directory)
    session = await TradingViewSession.open()
    try:
        while True:
            release_expired_leases()
            job = claim_job(settings.worker_id)
            if job is None:
                heartbeat(settings.worker_id, "idle", None)
                await asyncio.sleep(poll_seconds)
                continue
            await execute_job(session, job)
    finally:
        await session.close()


def main() -> None:
    asyncio.run(run_forever())


if __name__ == "__main__":
    main()
