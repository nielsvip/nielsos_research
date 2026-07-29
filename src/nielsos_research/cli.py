from __future__ import annotations

import asyncio
import json
from pathlib import Path

import typer

from .config import settings
from .db import connection
from .tradingview import smoke_test
from .worker import run_forever

app = typer.Typer(no_args_is_help=True)


@app.command("init-db")
def init_db(schema: Path = Path("database/schema.sql")) -> None:
    sql = schema.read_text()
    with connection() as conn:
        conn.execute(sql)
    typer.echo("Database initialized")


@app.command("tv-smoke")
def tv_smoke() -> None:
    typer.echo(json.dumps(asyncio.run(smoke_test()), indent=2))


@app.command("worker")
def worker() -> None:
    asyncio.run(run_forever())


@app.command("config")
def show_config() -> None:
    typer.echo(settings.model_dump_json(indent=2))


if __name__ == "__main__":
    app()
