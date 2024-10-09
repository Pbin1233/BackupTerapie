import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()  # This loads the environment variables from a .env file

# Configuration for download directory and Chrome user data directory
download_dir = os.getenv('SOURCE_DIR')
mese_successivo_dir = os.path.join(download_dir, "Mese successivo")
user_data_dir = os.getenv('USER_DATA_DIR')

# URL for the login page
url = os.getenv('URL')

# User credentials
username = os.getenv('APP_USERNAME')
password = os.getenv('PASSWORD')

# Nuclei and their respective wait times
nuclei = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'I']
attesa = [150, 300, 300, 300, 300, 300, 300, 300]
