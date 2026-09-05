import os
import subprocess
import sys
import time
import sqlite3
from pathlib import Path
from tests.ui.pages.fleet_page import FleetPage

import pytest
import requests
import threading

TEST_DB_PATH = Path(__file__).parent.parent / "data" / "test_deviceops.db"
BASE_URL = "http://127.0.0.1:8001"


@pytest.fixture(scope="session")
def live_server():
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    env = os.environ.copy()
    env["DEVICEOPS_DB_PATH"] = str(TEST_DB_PATH)

    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8001"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    log_lines = []

    def _drain_output():
        for line in process.stdout:
            log_lines.append(line)

    threading.Thread(target=_drain_output, daemon=True).start()

    for _ in range(30):
        try:
            requests.get(f"{BASE_URL}/devices")
            break
        except requests.ConnectionError:
            time.sleep(0.5)
    else:
        process.terminate()
        raise RuntimeError(f"Test server did not start in time.\n{''.join(log_lines)}")

    yield BASE_URL

    process.terminate()
    process.wait()
    print("\n----- Full server log for this test run -----")
    print("".join(log_lines))


@pytest.fixture(autouse=True)
def reset_db(live_server):
    conn = sqlite3.connect(TEST_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ota_jobs")
    cursor.execute("DELETE FROM firmware_builds")
    cursor.execute("DELETE FROM devices")
    conn.commit()
    conn.close()
    yield

@pytest.fixture
def fleet_page(page, live_server):
    fp = FleetPage(page)
    fp.goto(live_server)
    return fp