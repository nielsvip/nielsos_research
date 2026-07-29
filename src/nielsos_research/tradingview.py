from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from playwright.async_api import BrowserContext, Page, Playwright, async_playwright

from .config import settings


class TradingViewError(RuntimeError):
    pass


class HumanInterventionRequired(TradingViewError):
    def __init__(self, kind: str, message: str, context: dict[str, Any] | None = None):
        super().__init__(message)
        self.kind = kind
        self.context = context or {}


@dataclass
class TradingViewSession:
    playwright: Playwright
    context: BrowserContext
    page: Page

    @classmethod
    async def open(cls) -> "TradingViewSession":
        playwright = await async_playwright().start()
        context = await playwright.chromium.launch_persistent_context(
            user_data_dir=str(settings.chrome_user_data_dir),
            channel="chrome",
            headless=settings.headless,
            args=[f"--profile-directory={settings.chrome_profile_directory}", "--disable-dev-shm-usage"],
            viewport={"width": 1600, "height": 1000},
        )
        page = context.pages[0] if context.pages else await context.new_page()
        return cls(playwright, context, page)

    async def close(self) -> None:
        await self.context.close()
        await self.playwright.stop()

    async def connect(self) -> None:
        await self.page.goto(settings.tradingview_url, wait_until="domcontentloaded", timeout=120_000)
        await self.page.wait_for_timeout(5_000)
        await self.assert_ready()

    async def assert_ready(self) -> None:
        url = self.page.url.lower()
        if "signin" in url or "accounts" in url:
            raise HumanInterventionRequired("login", "TradingView login is required", {"url": self.page.url})
        if not await self.page.locator("body").count():
            raise TradingViewError("TradingView page body did not load")

    async def capture(self, name: str) -> str:
        settings.screenshot_dir.mkdir(parents=True, exist_ok=True)
        path = settings.screenshot_dir / f"{name}.png"
        await self.page.screenshot(path=str(path), full_page=True)
        return str(path)

    async def set_symbol(self, symbol: str) -> None:
        # TradingView keyboard symbol search is more stable than DOM class names.
        await self.page.keyboard.press("Control+K")
        await self.page.wait_for_timeout(500)
        await self.page.keyboard.type(symbol)
        await self.page.wait_for_timeout(1_500)
        await self.page.keyboard.press("Enter")
        await self.page.wait_for_timeout(3_000)

    async def set_timeframe(self, timeframe: str) -> None:
        # Numeric shortcuts work for minutes; higher timeframes require future selector calibration.
        normalized = timeframe.strip().upper()
        if normalized.endswith("M") and normalized[:-1].isdigit():
            await self.page.keyboard.type(normalized[:-1])
            await self.page.keyboard.press("Enter")
        else:
            raise HumanInterventionRequired(
                "selector_calibration",
                f"Timeframe selector needs calibration for {timeframe}",
                {"timeframe": timeframe},
            )
        await self.page.wait_for_timeout(3_000)

    async def run_smoke_test(self, symbol: str = "BINANCE:BTCUSDT", timeframe: str = "15m") -> dict[str, Any]:
        await self.connect()
        await self.set_symbol(symbol)
        await self.set_timeframe(timeframe)
        screenshot = await self.capture("tradingview_smoke_test")
        return {"symbol": symbol, "timeframe": timeframe, "url": self.page.url, "screenshot": screenshot}


async def smoke_test() -> dict[str, Any]:
    session = await TradingViewSession.open()
    try:
        return await session.run_smoke_test()
    finally:
        await session.close()


if __name__ == "__main__":
    print(asyncio.run(smoke_test()))
