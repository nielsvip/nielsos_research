# Gateway setup

Target: Ubuntu Gateway `157.90.18.35`, directory `/home/niels/nielsos_research`.

## 1. Pull the repository

```bash
cd /home/niels/nielsos_research
git pull origin main
```

## 2. Install system packages

```bash
sudo apt update
sudo apt install -y postgresql postgresql-contrib python3.11-venv google-chrome-stable xvfb
```

If `google-chrome-stable` is unavailable, install Google's official Chrome `.deb` first. Chromium can be supported later, but the initial worker expects Chrome because the Flasherz profile is a Chrome profile.

## 3. Create the virtual environment

```bash
cd /home/niels/nielsos_research
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e '.[dev]'
playwright install chrome
```

## 4. Create PostgreSQL database

```bash
sudo -u postgres psql <<'SQL'
CREATE USER nrl WITH PASSWORD 'CHANGE_THIS_PASSWORD';
CREATE DATABASE nrl OWNER nrl;
SQL
```

Copy and edit the environment file:

```bash
cp .env.example .env
chmod 600 .env
nano .env
```

Update `NRL_DATABASE_URL` with the real password.

Initialize:

```bash
source .venv/bin/activate
nrl init-db
```

## 5. Chrome profile on Gateway

The Mac profile itself is not portable. Log into the Flasherz Google/TradingView account once in Chrome on Gateway and keep that Linux profile dedicated to NRL.

For the first interactive login through SSH:

```bash
Xvfb :99 -screen 0 1600x1000x24 >/tmp/nrl-xvfb.log 2>&1 &
export DISPLAY=:99
google-chrome --user-data-dir=/home/niels/.config/google-chrome --profile-directory=Default
```

Use VNC/remote desktop or Chrome remote debugging for the one-time login. Do not put TradingView credentials into `.env`.

## 6. Verify TradingView connection

After login and layout setup:

```bash
export DISPLAY=:99
source .venv/bin/activate
nrl tv-smoke
```

Expected output is JSON with symbol, timeframe, TradingView URL, and a screenshot path.

## 7. Run the worker

```bash
export DISPLAY=:99
source .venv/bin/activate
nrl worker
```

Systemd units will be added after the interactive smoke test passes. Until then, run in a terminal or tmux so selector calibration is observable.

## Safety and resource constraints

- Start with exactly one Chrome worker on the 4 GB Gateway.
- Keep Pine calculations inside TradingView; Gateway performs orchestration only.
- Use expiring SQL leases so a crash requeues work.
- Any login, popup, compile error, or unknown selector creates an intervention and blocks only that job.
