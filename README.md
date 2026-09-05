# DeviceOps

A simulated OTA (over-the-air) firmware update system for a device fleet.

This project is modeled on real device-fleet testing work — the idea is to rebuild, in a simplified form, the kind of system that manages firmware updates across a bunch of connected devices: upload firmware, start an update job on a device, watch that job move through its stages, and handle the errors that come with it.

There's no real hardware here. Devices are just rows in a database, and the "update" is simulated by a background task that changes a job's status over time. That's intentional — the point of this project isn't to talk to real firmware, it's to build (and test) a realistic backend and UI around the same problem shape: uploads, jobs, polling, timeouts, and state.

## Status: Phase 1 (Backend), Phase 2 (UI), and Phase 3 (Testing) — complete

This is being built in phases. The backend, a working frontend, and a full test suite covering both now exist. See `ARCHITECTURE.md` for the full plan and the reasoning behind each piece.

## What's built so far

**Backend**
- A FastAPI backend with SQLite storage (no ORM — raw SQL, written by hand)
- Three tables: `devices`, `firmware_builds`, `ota_jobs`, connected with foreign keys
- Endpoints to register a device, list devices, upload a firmware build, list firmware builds, start an update job, and check a job's status
- A background task that simulates a job moving through `pending → in_progress → completed` over time, so there's something real to poll against
- Error handling for the cases that actually matter: starting a job on a device that doesn't exist, starting a job on a device that's already mid-update, and checking the status of a job that was never created

**Frontend**
- A plain HTML/CSS/JS single page, served directly by FastAPI (no separate frontend server, no build step)
- A fleet table showing every device and its live status
- Forms to register devices, upload firmware, and start update jobs
- A live status panel that polls a job's status until it finishes, with no page refresh
- Backend errors (like trying to update a device that's already busy) shown directly in the UI

**Testing**
- 10 Playwright UI test cases, built around a Page Object Model (`FleetPage`), covering device registration, firmware upload, the full job lifecycle, and error handling
- 10 pytest API test cases, hitting the backend directly with `requests` — covering successful flows and the same error cases from the API layer
- A fully isolated test setup: each test run spins up its own FastAPI server on a separate port, pointed at a throwaway SQLite database that's wiped clean before every single test
- Self-contained HTML test reports generated per suite (`reports/ui/`, `reports/api/`)
- Two test cases are intentionally left flaky rather than fixed or deleted — they're documented in the test file as known race conditions, kept on purpose as real failure data for a later phase (an AI agent that investigates why tests fail)
- Along the way, testing surfaced a real bug: the test server's output pipe wasn't being drained, which could silently stall the whole server under load. Found and fixed during this phase, not a hypothetical.

## Endpoints

| Method | Path | What it does |
|---|---|---|
| `POST` | `/devices` | Register a new device in the fleet |
| `GET` | `/devices` | List all devices |
| `POST` | `/firmware/upload` | Upload a new firmware build |
| `GET` | `/firmware` | List all firmware builds |
| `POST` | `/ota/jobs` | Start an update job for a device |
| `GET` | `/ota/jobs/{id}/status` | Check how a job is progressing |

## Tech stack (so far)

- Python, FastAPI
- SQLite (raw SQL, no ORM)
- `asyncio` for the background job simulation
- Plain HTML, CSS, and JavaScript for the frontend (no framework)
- Playwright (UI testing) and pytest + requests (API testing)

## Running it locally

```bash
# from the project root, with your virtual environment active
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open `http://127.0.0.1:8000/` for the UI, or `http://127.0.0.1:8000/docs` for the raw API.

## Running the tests

```bash
playwright install   # one-time, downloads browser binaries

pytest tests/ui/ -v --html=reports/ui/report.html --self-contained-html
pytest tests/api/ -v --html=reports/api/report.html --self-contained-html
```

## What's next

This is a full-stack project, not just a backend exercise. The plan from here:

1. Load testing with k6
2. Visual/OCR validation
3. CI/CD with GitHub Actions
4. An AI agent that looks at failed jobs and helps figure out why they failed

Each of those is a separate phase, and none of them are built yet. This README will get updated as they land.
