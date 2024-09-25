import os
import shutil
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_first_day_of_month(date):
    return date.replace(day=1)

def get_last_day_of_previous_month(date):
    first_day_of_month = get_first_day_of_month(date)
    return first_day_of_month - timedelta(days=1)

def check_folder_for_pdf(folder, pdf_name):
    # Check main folder
    pdf_path = os.path.join(folder, pdf_name)
    if os.path.exists(pdf_path):
        return pdf_path
    
    # Check "Mese successivo" subfolder
    mese_successivo = os.path.join(folder, "Mese successivo")
    if os.path.exists(mese_successivo):
        pdf_path = os.path.join(mese_successivo, pdf_name)
        if os.path.exists(pdf_path):
            return pdf_path
    
    return None

def find_latest_pdf(base_folder, pdf_name):
    today = datetime.now()
    current_month_start = get_first_day_of_month(today)
    
    # Step 1: Check current month up to the first day
    current_date = today
    while current_date >= current_month_start:
        year_folder = current_date.strftime('%Y')
        date_folder = current_date.strftime('%Y-%m-%d')
        current_folder = os.path.join(base_folder, year_folder, date_folder)
        
        pdf_path = check_folder_for_pdf(current_folder, pdf_name)
        if pdf_path:
            return pdf_path
        
        current_date -= timedelta(days=1)
    
    # Step 2: Check "Mese successivo" folders from the previous month
    last_day_prev_month = get_last_day_of_previous_month(today)
    prev_month_start = get_first_day_of_month(last_day_prev_month)
    current_date = last_day_prev_month
    
    while current_date >= prev_month_start:
        year_folder = current_date.strftime('%Y')
        date_folder = current_date.strftime('%Y-%m-%d')
        current_folder = os.path.join(base_folder, year_folder, date_folder, "Mese successivo")
        
        if os.path.exists(current_folder):
            pdf_path = check_folder_for_pdf(current_folder, pdf_name)
            if pdf_path:
                return pdf_path
        
        current_date -= timedelta(days=1)
    
    # Step 3: Check main folders from the previous month
    current_date = last_day_prev_month
    while current_date >= prev_month_start:
        year_folder = current_date.strftime('%Y')
        date_folder = current_date.strftime('%Y-%m-%d')
        current_folder = os.path.join(base_folder, year_folder, date_folder)
        
        pdf_path = check_folder_for_pdf(current_folder, pdf_name)
        if pdf_path:
            return pdf_path
        
        current_date -= timedelta(days=1)
    
    return None  # File not found after all checks

def copy_file_to_destination(source_path, destination_folder):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    file_name = os.path.basename(source_path)
    destination_path = os.path.join(destination_folder, file_name)
    
    if os.path.exists(destination_path):
        return None  # File already exists, don't copy
    
    shutil.copy2(source_path, destination_path)
    return destination_path

def main():
    base_folder = os.getenv('ARCHIVE_DIR')
    destination_folder = os.getenv('SOURCE_DIR')
    pdf_names = [f"Nucleo {letter}.pdf" for letter in "ABCDEFGI"]
    
    for pdf_name in pdf_names:
        latest_pdf = find_latest_pdf(base_folder, pdf_name)
        if latest_pdf:
            try:
                copied_path = copy_file_to_destination(latest_pdf, destination_folder)
                if copied_path:
                    print(f"Latest backup of {pdf_name} found at: {latest_pdf}")
                    print(f"Copied to: {copied_path}")
                else:
                    print(f"File {pdf_name} already exists in the destination folder. Not copied.")
            except Exception as e:
                print(f"Error processing {pdf_name}: {str(e)}")
        else:
            print(f"No backup found for {pdf_name}")

if __name__ == "__main__":
    main()
