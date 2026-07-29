# TradingView setup contract

Use the existing TradingView Premium account through the dedicated Flasherz Chrome profile.

## Required layout

Create one chart layout named exactly:

`NRL_MASTER`

Initial layout requirements:

1. One chart only.
2. No drawings required.
3. Standard candles.
4. A clean pane for the NRL Pine research harness.
5. Save the layout after loading `BINANCE:BTCUSDT` on 15 minutes.
6. Keep the layout dedicated to automation; do not use it for the existing 3 × 8 monitoring screens.

## Session rules

- Use one TradingView browser session initially.
- The Flasherz Linux Chrome profile on Gateway is the automation profile.
- A second paid TradingView account is not required.
- Human monitoring may continue on the existing account, but simultaneous-session limits and layout collisions must be tested before both are used heavily at once.
- The worker must never edit or depend on the user's monitoring layouts.

## First calibration

Run `nrl tv-smoke` interactively. The first smoke test proves:

- TradingView login persists.
- `NRL_MASTER` is accessible.
- Symbol switching works.
- 15-minute timeframe switching works.
- Screenshot capture works.

Selectors and keyboard shortcuts can change. Any uncertain interaction must produce an intervention record rather than repeatedly clicking.

## Pine installation

The universal Pine harness will initially be added manually to the Pine Editor and saved as `NRL Research Harness`. Browser automation of Pine source editing is deferred until chart control is stable because editor automation is more fragile than symbol/timeframe/input changes.
