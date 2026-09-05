from playwright.sync_api import expect

def test_fleet_starts_empty(fleet_page):
    expect(fleet_page.page.locator("#device-table-body tr")).to_have_count(0)
    expect(fleet_page.page.locator("#fleet-count")).to_have_text("0 devices")


def test_register_device_adds_to_table(fleet_page):
    fleet_page.register_device("Echo Test Device", "echo-gen4", "1.0.0")

    expect(fleet_page.page.locator("#device-table-body tr")).to_have_count(1)
    row = fleet_page.page.locator("#device-table-body tr").first
    expect(row).to_contain_text("Echo Test Device")
    expect(row).to_contain_text("echo-gen4")
    expect(row).to_contain_text("idle")
    expect(row).to_contain_text("1.0.0")


def test_fleet_count_updates_after_registration(fleet_page):
    fleet_page.register_device("Device A", "profile-a")
    expect(fleet_page.page.locator("#fleet-count")).to_have_text("1 device")

    fleet_page.register_device("Device B", "profile-b")
    expect(fleet_page.page.locator("#fleet-count")).to_have_text("2 devices")


def test_registered_device_appears_in_job_dropdown(fleet_page):
    fleet_page.register_device("Dropdown Device", "profile-x")

    options = fleet_page.job_device_options()
    assert any("Dropdown Device" in option for option in options)


def test_upload_firmware_adds_to_build_list(fleet_page):
    fleet_page.upload_firmware("2.0.0")

    expect(fleet_page.page.locator("#firmware-list li")).to_have_count(1)
    expect(fleet_page.page.locator("#firmware-list li").first).to_have_text("v2.0.0")


def test_uploaded_firmware_appears_in_job_dropdown(fleet_page):
    fleet_page.upload_firmware("3.1.0")

    options = fleet_page.job_build_options()
    assert any("3.1.0" in option for option in options)


def test_start_job_shows_pending_status(fleet_page):
    fleet_page.register_device("Job Device", "profile-job")
    fleet_page.upload_firmware("1.5.0")

    fleet_page.start_job("Job Device", "1.5.0")

    expect(fleet_page.page.locator("#job-status")).to_contain_text("pending")

    # Wait for the job to fully finish before the test ends — otherwise its
    # background task keeps running into the next test and corrupts shared
    # server/database state
    expect(fleet_page.page.locator("#job-status")).to_contain_text(
        "completed", timeout=15000
    )


def test_job_status_reaches_completed(fleet_page):
    fleet_page.register_device("Completion Device", "profile-complete")
    fleet_page.upload_firmware("4.0.0")

    fleet_page.start_job("Completion Device", "4.0.0")

    # background task takes ~10s total (5s + 5s) — allow generous timeout
    expect(fleet_page.page.locator("#job-status")).to_contain_text(
        "completed", timeout=15000
    )


def test_device_status_flips_updating_then_idle(fleet_page):
    fleet_page.register_device("Status Flip Device", "profile-flip")
    fleet_page.upload_firmware("5.0.0")

    fleet_page.start_job("Status Flip Device", "5.0.0")

    # shortly after starting, device should show "updating"
    expect(
        fleet_page.page.locator("#device-table-body tr", has_text="Status Flip Device")
    ).to_contain_text("updating", timeout=5000)

    # after the full job cycle, device should be back to "idle"
    expect(
        fleet_page.page.locator("#device-table-body tr", has_text="Status Flip Device")
    ).to_contain_text("idle", timeout=15000)


def test_second_job_on_busy_device_shows_409_error(fleet_page):
    fleet_page.register_device("Busy Device", "profile-busy")
    fleet_page.upload_firmware("6.0.0")

    fleet_page.start_job("Busy Device", "6.0.0")
    expect(fleet_page.page.locator("#job-status")).to_contain_text("pending")

    # immediately try to start a second job on the same device
    fleet_page.start_job("Busy Device", "6.0.0")

    expect(fleet_page.page.locator("#job-status")).to_contain_text(
        "already mid-update"
    )