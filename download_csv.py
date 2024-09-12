import os
import sys
import time
import logging
import schedule
from dotenv import load_dotenv
from pages.login_page import LoginPage
from pages.webform_page import WebformPage
from utils.browser_setup import setup_browser
from utils.file_management import find_and_rename_file

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_and_update_csv(destination_path="."):
    """Main function to download and update CSV file."""
    if os.path.isdir(destination_path):
        download_dir = os.path.abspath(destination_path)
        file_name = None
    else:
        download_dir = os.path.dirname(os.path.abspath(destination_path))
        file_name = os.path.basename(destination_path)

    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    logger.info("Browser setup with download directory: %s", download_dir)
    driver = setup_browser(download_dir)

    try:
        login_page = LoginPage(driver)
        login_URL = os.getenv("FRAMAFORMS_LOGIN_URL")
        email = os.getenv("FRAMAFORMS_EMAIL")
        password = os.getenv("FRAMAFORMS_PASSWORD")

        login_page.load(login_URL)
        login_page.login(email, password)

        if login_page.is_logged_in():
            logger.info("Successfully logged in.")
        else:
            logger.error("Failed to log in.")
            sys.exit(1)

        webform_page = WebformPage(driver)
        webform_URL = os.getenv("FRAMAFORMS_WEBFORM_URL")
        
        webform_page.load(webform_URL)
        webform_page.export_csv(download_dir)

        file_path = find_and_rename_file(download_dir, file_name)
        logger.info("File downloaded: %s", file_path)
    finally:
        driver.quit()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: download_csv.py <destination_path>")
        sys.exit(1)
    
    destination = sys.argv[1]
    download_and_update_csv(destination)

    # Schedule the CSV download to run everyday at 6 AM
    schedule.every().day.at("06:00").do(download_and_update_csv, destination_path=destination)
    
    while True:
        schedule.run_pending()
        time.sleep(60)
