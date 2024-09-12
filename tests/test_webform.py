import pytest
import shutil
import os
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.login_page import LoginPage
from pages.webform_page import WebformPage

@pytest.mark.login
def test_login_success(driver):
    """Test successful login on Unity."""
    login_page = LoginPage(driver)
    login_URL = os.getenv("FRAMAFORMS_LOGIN_URL")
    email = os.getenv("FRAMAFORMS_EMAIL")
    password = os.getenv("FRAMAFORMS_PASSWORD")
    
    login_page.load(login_URL)
    login_page.login(email, password)

    assert login_page.is_logged_in(), "Login failed."

@pytest.mark.export
def test_correct_options_selected(driver):
    """Test that correct options are selected for export."""
    webform_page = WebformPage(driver)
    webform_URL = os.getenv("FRAMAFORMS_WEBFORM_URL")

    webform_page.load(webform_URL)
    webform_page.select_options()

    # Verify that the correct delimiter is selected
    delimiter = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'edit-delimiter'))
    )
    assert delimiter.get_attribute('value') == ';', "Incorrect delimiter selected."

    # Verify that the compact format is selected
    compact_option = driver.find_element(By.ID, 'edit-select-format-compact')
    assert compact_option.is_selected(), "Compact format option not selected."

    # Verify that specific components are deselected
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
        option = driver.find_element(By.ID, option_id)
        assert not option.is_selected(), f"{option_id} should be deselected."

@pytest.mark.export
def test_export_csv(driver):
    """Test exporting CSV with correct options selected."""
    webform_page = WebformPage(driver)
    webform_URL = os.getenv("FRAMAFORMS_WEBFORM_URL")
    webform_page.load(webform_URL)

    download_path = os.path.join(os.path.abspath("."), "downloads")
    webform_page.export_csv(download_path)

    files = os.listdir(download_path)
    webform_file = next((f for f in files if f.endswith(".csv")), None)
    assert webform_file is not None, "CSV file was not downloaded."

@pytest.mark.parametrize("download_path", [
    pytest.param("./test_download1", id="path1"),
    pytest.param("./test_download2", id="path2")
])
@pytest.mark.export
def test_export_with_custom_path(driver, download_path):
    """Test exporting CSV to a custom download path."""
    driver.execute_cdp_cmd('Browser.setDownloadBehavior', {
        'behavior': 'allow',
        'downloadPath': download_path
    })

    # Create the temporary download directory manually.
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    driver.refresh()
    webform_page = WebformPage(driver)
    webform_page.export_csv(download_path)

    files = os.listdir(download_path)
    webform_file = next((f for f in files if f.endswith(".csv")), None)
    assert webform_file is not None, f"CSV file was not downloaded in {download_path}."

    # Delete the temporary download directory manually.
    if os.path.exists(download_path):
        shutil.rmtree(download_path)
