from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="NRL_", env_file=".env", extra="ignore")

    database_url: str = "postgresql://nrl:nrl@localhost:5432/nrl"
    log_level: str = "INFO"
    worker_id: str = "gateway-tv-1"
    tradingview_url: str = "https://www.tradingview.com/chart/"
    tradingview_layout: str = "NRL_MASTER"
    chrome_user_data_dir: Path = Path("/home/niels/.config/google-chrome")
    chrome_profile_directory: str = "Default"
    screenshot_dir: Path = Path("runtime/screenshots")
    headless: bool = False
    job_lease_seconds: int = Field(default=900, ge=60)
    heartbeat_seconds: int = Field(default=30, ge=5)
    max_attempts: int = Field(default=3, ge=1)
    autonomous_start_utc: str = "02:00"
    autonomous_end_utc: str = "14:00"


settings = Settings()
