import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def find_project_root(current_path: Path, project_name: str = "BackupTerapie") -> Path:
    while current_path.name != project_name:
        if current_path == current_path.parent:
            raise FileNotFoundError(f"Could not find the project root '{project_name}'")
        current_path = current_path.parent
    return current_path

def add_project_root_to_path():
    project_root = find_project_root(Path(__file__).resolve().parent)
    sys.path.insert(0, str(project_root))

def find_and_load_dotenv(start_path: str = None) -> bool:
    if start_path is None:
        start_path = os.getcwd()
    
    current_dir = Path(start_path).resolve()
    
    while current_dir != current_dir.parent:  # Stop at the root directory
        env_file = current_dir / '.env'
        if env_file.is_file():
            load_dotenv(dotenv_path=env_file)
            print(f"Loaded .env file from: {env_file}")
            return True
        current_dir = current_dir.parent
    
    print("No .env file found in the current directory or any parent directories.")
    return False

# Automatically add the project root to the Python path when this module is imported
add_project_root_to_path()
