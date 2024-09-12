from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
import re

class WebformPage:
    """Page Object Model for the webform page."""
    def __init__(self, driver):
        self.driver = driver

    def load(self, webform_URL):
        """Load the webform page."""
        self.driver.get(webform_URL)

    def scroll_to_element(self, element):
        """Scroll to the element."""
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()

    def select_options(self):
        """Select options for the export."""
        # Select the delimiter
        delimiter_select = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.ID, 'edit-delimiter'))
        )
        delimiter_select.click()
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'option[value=";"]'))
        ).click()

        # Expand the fieldset to select "Compact"
        fieldset_legend = WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="edit-select-options"]/legend/span/a'))
        )
        fieldset_legend.click()

        compact_option = WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@id="edit-select-format-compact"]'))
        )
        compact_option.click()

        # Expand the fieldset to deselect specific options
        components_legend = WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="edit-components"]/legend/span/a'))
        )
        components_legend.click()

        # Deselect specific options
        options_to_deselect = [
            'edit-components-webform-serial',
            'edit-components-webform-sid',
            'edit-components-webform-completed-time',
            'edit-components-webform-modified-time',
            'edit-components-webform-draft',
            'edit-components-webform-ip-address',
            'edit-components-webform-uid',
            'edit-components-webform-username'
        ]

        for option_id in options_to_deselect:
            checkbox = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, option_id))
            )
            self.scroll_to_element(checkbox)  # Scroll to the checkbox if it's not visible
            if checkbox.is_selected():
                checkbox.click()

    def wait_for_download_complete(self, download_dir, timeout=60):
        """Wait for the CSV file to be completely downloaded."""
        start_time = time.time()

        webform_title = os.getenv("FRAMAFORMS_WEBFORM_TITLE")
        sanitized_title = re.sub(r'\s+', '_', webform_title.strip().lower())
        
        while True:
            files = os.listdir(download_dir)
            webform_file_downloading = next(
                (
                    f for f in files
                    if re.search(rf"{re.escape(sanitized_title)}", f)
                    and (f.endswith('.crdownload') or f.endswith('.part'))
                ),
                None
            )

            if not webform_file_downloading:
                break
            
            if time.time() - start_time > timeout:
                raise TimeoutError("Download Timeout.")

    def export_csv(self, download_dir):
        """Export the data to a CSV file and wait for it to complete downloading."""
        self.select_options()

        # Click the download button
        download_button = WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.ID, 'edit-submit'))
        )
        download_button.click()

        self.wait_for_download_complete(download_dir)
        
        time.sleep(5)
