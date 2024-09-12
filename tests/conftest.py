import pytest
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import os
from utils.browser_setup import setup_browser

load_dotenv()

@pytest.fixture(scope="session")
def driver():
    """Fixture to initialize the browser and clean up the temporary download directory after use."""
    download_dir = os.path.join(os.path.abspath("."), "downloads")
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    driver = setup_browser(download_dir)
    
    yield driver
    
    if os.path.exists(download_dir):
        shutil.rmtree(download_dir)

    driver.quit()