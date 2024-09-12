import os
import re

def find_and_rename_file(download_dir, file_name=None):
    """Find and rename the downloaded CSV file."""
    webform_title = os.getenv("FRAMAFORMS_WEBFORM_TITLE")
    sanitized_title = re.sub(r'\s+', '_', webform_title.strip().lower())

    files = os.listdir(download_dir)
    webform_file = next((f for f in files if re.search(rf"{re.escape(sanitized_title)}.*\.csv$", f)), None)

    if not webform_file:
        raise FileNotFoundError("Webform CSV file not found.")

    final_file_name = file_name if file_name else webform_file
    source_file = os.path.join(download_dir, webform_file)
    destination_file = os.path.join(download_dir, final_file_name)
    os.rename(source_file, destination_file)
    return destination_file
