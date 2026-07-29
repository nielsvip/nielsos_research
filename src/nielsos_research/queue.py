from __future__ import annotations

from datetime import timedelta
from typing import Any

from psycopg.types.json import Jsonb

from .config import settings
from .db import connection


def register_worker(worker_id: str, hostname: str, browser_profile: str) -> None:
    with connection() as conn:
        conn.execute(
            """
            INSERT INTO workers(worker_id, hostname, browser_profile, status, heartbeat_at)
            VALUES (%s,%s,%s,'idle',now())
            ON CONFLICT(worker_id) DO UPDATE SET
              hostname=excluded.hostname,
              browser_profile=excluded.browser_profile,
              status='idle',
              heartbeat_at=now()
            """,
            (worker_id, hostname, browser_profile),
        )


def heartbeat(worker_id: str, status: str, current_job_id: str | None = None) -> None:
    with connection() as conn:
        conn.execute(
            "UPDATE workers SET status=%s,current_job_id=%s,heartbeat_at=now() WHERE worker_id=%s",
            (status, current_job_id, worker_id),
        )


def release_expired_leases() -> int:
    with connection() as conn:
        cur = conn.execute(
            """
            UPDATE jobs SET status='queued',lease_owner=NULL,lease_expires_at=NULL,
              last_error=coalesce(last_error,'') || E'\nLease expired and was requeued.'
            WHERE status IN ('leased','running') AND lease_expires_at < now()
            """
        )
        return cur.rowcount


def claim_job(worker_id: str) -> dict[str, Any] | None:
    lease = timedelta(seconds=settings.job_lease_seconds)
    with connection() as conn:
        row = conn.execute(
            """
            WITH candidate AS (
              SELECT id FROM jobs
              WHERE status='queued' AND attempts < max_attempts
              ORDER BY priority DESC, created_at
              FOR UPDATE SKIP LOCKED LIMIT 1
            )
            UPDATE jobs j SET status='leased',lease_owner=%s,
              lease_expires_at=now()+%s,attempts=attempts+1,started_at=coalesce(started_at,now())
            FROM candidate c WHERE j.id=c.id
            RETURNING j.*
            """,
            (worker_id, lease),
        ).fetchone()
        return dict(row) if row else None


def mark_running(job_id: str, checkpoint: dict[str, Any] | None = None) -> None:
    with connection() as conn:
        conn.execute(
            "UPDATE jobs SET status='running',checkpoint=%s WHERE id=%s",
            (Jsonb(checkpoint or {}), job_id),
        )


def save_checkpoint(job_id: str, checkpoint: dict[str, Any]) -> None:
    with connection() as conn:
        conn.execute(
            "UPDATE jobs SET checkpoint=%s,lease_expires_at=now()+(%s * interval '1 second') WHERE id=%s",
            (Jsonb(checkpoint), settings.job_lease_seconds, job_id),
        )


def complete_job(job_id: str, metrics: dict[str, Any], raw_payload: dict[str, Any], screenshot: str | None) -> None:
    with connection() as conn:
        conn.execute(
            "INSERT INTO results(job_id,metrics,raw_payload,screenshot_path) VALUES (%s,%s,%s,%s)",
            (job_id, Jsonb(metrics), Jsonb(raw_payload), screenshot),
        )
        conn.execute(
            "UPDATE jobs SET status='completed',finished_at=now(),lease_owner=NULL,lease_expires_at=NULL WHERE id=%s",
            (job_id,),
        )


def fail_or_requeue(job_id: str, error: str, blocked: bool = False) -> None:
    with connection() as conn:
        job = conn.execute("SELECT attempts,max_attempts FROM jobs WHERE id=%s FOR UPDATE", (job_id,)).fetchone()
        if not job:
            return
        status = "blocked" if blocked else ("failed" if job["attempts"] >= job["max_attempts"] else "queued")
        conn.execute(
            "UPDATE jobs SET status=%s,last_error=%s,lease_owner=NULL,lease_expires_at=NULL WHERE id=%s",
            (status, error, job_id),
        )


def create_intervention(job_id: str | None, worker_id: str, kind: str, question: str, context: dict[str, Any], screenshot: str | None) -> None:
    with connection() as conn:
        conn.execute(
            "INSERT INTO interventions(job_id,worker_id,kind,question,context,screenshot_path) VALUES (%s,%s,%s,%s,%s,%s)",
            (job_id, worker_id, kind, question, Jsonb(context), screenshot),
        )
