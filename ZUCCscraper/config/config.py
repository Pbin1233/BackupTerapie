import os
import sys
from pathlib import Path

def find_project_root(current_path: Path, project_name: str = "BackupTerapie") -> Path:
    while current_path.name != project_name:
        if current_path == current_path.parent:
            raise FileNotFoundError(f"Could not find the project root '{project_name}'")
        current_path = current_path.parent
    return current_path

# Add the project root to the Python path
project_root = find_project_root(Path(__file__).resolve().parent)
sys.path.insert(0, str(project_root))

# Now we can import env_utils
from env_utils import find_and_load_dotenv

# Load environment variables
find_and_load_dotenv()

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
