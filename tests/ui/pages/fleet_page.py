class FleetPage:
    def __init__(self, page):
        self.page = page

    def goto(self, base_url):
        self.page.goto(base_url)

    # Device Registration
    def register_device(self, name, profile, version=""):
        self.page.fill("#device-name", name)
        self.page.fill("#device-profile", profile)
        if version:
            self.page.fill("#device-version", version)
        self.page.click("#device-form button[type='submit']")

    def device_row_count(self):
        return self.page.locator("#device-table-body tr").count()

    def fleet_count_text(self):
        return self.page.locator("#fleet-count").inner_text()

    #Firmware
    def upload_firmware(self, version):
        self.page.fill("#firmware-version", version)
        self.page.click("#firmware-form button[type='submit']")

    def firmware_list_count(self):
        return self.page.locator("#firmware-list li").count()

    #Jobs
    def start_job(self, device_label_substring, build_label_substring):
        device_locator = self.page.locator("#job-device option", has_text=device_label_substring)
        device_locator.wait_for(state="attached", timeout=10000)
        device_value = device_locator.get_attribute("value")
        self.page.select_option("#job-device", value=device_value)

        build_locator = self.page.locator("#job-build option", has_text=build_label_substring)
        build_locator.wait_for(state="attached", timeout=10000)
        build_value = build_locator.get_attribute("value")
        self.page.select_option("#job-build", value=build_value)

        self.page.click("#job-form button[type='submit']")

    def job_status_text(self):
        return self.page.locator("#job-status").inner_text()

    # Dropdown contents
    def job_device_options(self):
        return self.page.locator("#job-device option").all_inner_texts()

    def job_build_options(self):
        return self.page.locator("#job-build option").all_inner_texts()

    #Per-device status lookup

    def device_status(self, name_substring):
        row = self.page.locator("#device-table-body tr", has_text=name_substring)
        return row.locator("td").nth(3).inner_text()