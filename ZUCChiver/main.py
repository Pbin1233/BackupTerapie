import os
import shutil
import time
from datetime import datetime, timedelta
import logging
from dotenv import load_dotenv


# Set log level based on environment variable
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()

# Set up basic configuration for logging
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),  # Use the environment variable
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),  # Log to file
        logging.StreamHandler()  # Also log to console
    ]
)

def log(message, level="INFO"):
    logger = logging.getLogger(__name__)
    if level == "INFO":
        logger.info(message)
    elif level == "DEBUG":
        logger.debug(message)
    elif level == "ERROR":
        logger.error(message)
    elif level == "WARNING":
        logger.warning(message)

# Load environment variables from .env file
load_dotenv()

def move_files_to_yesterday_folder(source_folder, destination_base_folder):
    logging.info(f"Starting move_files_to_yesterday_folder")
    logging.info(f"Source folder: {source_folder}")
    logging.info(f"Destination base folder: {destination_base_folder}")

    if not source_folder or not destination_base_folder:
        raise ValueError("Both SOURCE_DIR and ARCHIVE_DIR must be set and non-empty")

    if not os.path.exists(source_folder):
        raise ValueError(f"Source folder does not exist: {source_folder}")

    if not os.path.exists(destination_base_folder):
        raise ValueError(f"Destination base folder does not exist: {destination_base_folder}")

    # Get yesterday's date
    yesterday = datetime.now() - timedelta(days=1)
    year_folder = yesterday.strftime('%Y')
    date_folder = yesterday.strftime('%Y-%m-%d')

    # Construct the full path for the destination folder
    destination_folder = os.path.join(destination_base_folder, year_folder, date_folder)
    logging.info(f"Destination folder: {destination_folder}")

    # Create the destination folders if they don't exist
    os.makedirs(destination_folder, exist_ok=True)

    # Move all files and folders from the source folder to the destination folder
    for item in os.listdir(source_folder):
        source_item = os.path.join(source_folder, item)
        destination_item = os.path.join(destination_folder, item)
        logging.debug(f"Moving {source_item} to {destination_item}")
        if os.path.isdir(source_item):
            shutil.move(source_item, destination_item)
        else:
            shutil.move(source_item, destination_folder)

    logging.info(f"All contents of {source_folder} have been moved to {destination_folder}")

def main():
    logging.info("Script started")
    
    source_folder = os.getenv('SOURCE_DIR')
    destination_base_folder = os.getenv('ARCHIVE_DIR')

    logging.info(f"SOURCE_DIR environment variable: {source_folder}")
    logging.info(f"ARCHIVE_DIR environment variable: {destination_base_folder}")

    if not source_folder or not destination_base_folder:
        logging.error("Error: Environment variables SOURCE_DIR and ARCHIVE_DIR must be set and non-empty.")
        logging.error("Please check your .env file and ensure these variables are correctly set.")
        return

    try:
        move_files_to_yesterday_folder(source_folder, destination_base_folder)
    except Exception as e:
        logging.exception(f"An error occurred: {e}")

    # Wait for a few minutes before closing the shell window
    time.sleep(120)

if __name__ == "__main__":
    main()
