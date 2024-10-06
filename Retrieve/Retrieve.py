import os
import shutil
from datetime import datetime, timedelta
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_first_day_of_month(date):
    return date.replace(day=1)

def get_last_day_of_previous_month(date):
    first_day_of_month = get_first_day_of_month(date)
    return first_day_of_month - timedelta(days=1)

def check_folder_for_pdf(folder, pdf_name):
    pdf_path = os.path.join(folder, pdf_name)
    if os.path.exists(pdf_path):
        return pdf_path
    
    mese_successivo = os.path.join(folder, "Mese successivo")
    if os.path.exists(mese_successivo):
        pdf_path = os.path.join(mese_successivo, pdf_name)
        if os.path.exists(pdf_path):
            return pdf_path
    
    return None

def find_latest_pdf(base_folder, pdf_name):
    today = datetime.now()
    current_month_start = get_first_day_of_month(today)
    
    current_date = today
    while current_date >= current_month_start:
        year_folder = current_date.strftime('%Y')
        date_folder = current_date.strftime('%Y-%m-%d')
        current_folder = os.path.join(base_folder, year_folder, date_folder)
        
        pdf_path = check_folder_for_pdf(current_folder, pdf_name)
        if pdf_path:
            return pdf_path
        
        current_date -= timedelta(days=1)
    
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
    
    current_date = last_day_prev_month
    while current_date >= prev_month_start:
        year_folder = current_date.strftime('%Y')
        date_folder = current_date.strftime('%Y-%m-%d')
        current_folder = os.path.join(base_folder, year_folder, date_folder)
        
        pdf_path = check_folder_for_pdf(current_folder, pdf_name)
        if pdf_path:
            return pdf_path
        
        current_date -= timedelta(days=1)
    
    return None

def check_day_for_complete_files(base_folder, year, month, day):
    today = datetime.now().date()  # Get today's date
    date_str = f"{year}-{month:02d}-{day:02d}"
    date_folder = os.path.join(base_folder, str(year), date_str)

    pdf_names = [f"Nucleo {letter}.pdf" for letter in "ABCDEFGI"]
    all_present = True

    # Check if this is the current day and look into SOURCE_DIR
    current_day = datetime(year, month, day).date()
    if current_day == today:
        source_folder = os.getenv('SOURCE_DIR')  # Get the source folder for the current day from .env

        # Check the main folder in SOURCE_DIR for the current day's files
        for pdf_name in pdf_names:
            if not os.path.exists(os.path.join(source_folder, pdf_name)):
                all_present = False
                break
        
        # Check for "Mese successivo" subfolder in SOURCE_DIR for the current day
        mese_successivo = os.path.join(source_folder, "Mese successivo")
        mese_successivo_status = None
        if os.path.exists(mese_successivo):
            mese_successivo_complete = all(os.path.exists(os.path.join(mese_successivo, pdf_name)) for pdf_name in pdf_names)
            if mese_successivo_complete:
                mese_successivo_status = "complete"
            else:
                mese_successivo_status = "incomplete"

        return {"complete": all_present, "mese_successivo": mese_successivo_status}

    # Skip future dates
    if current_day > today:
        return None

    # For other days, check the archive
    for pdf_name in pdf_names:
        if not check_folder_for_pdf(date_folder, pdf_name):
            all_present = False
            break
    
    # Check "Mese successivo" for other days
    mese_successivo = os.path.join(date_folder, "Mese successivo")
    mese_successivo_status = None
    if os.path.exists(mese_successivo):
        # Check if "Mese successivo" contains the full set of PDFs
        mese_successivo_complete = all(check_folder_for_pdf(mese_successivo, pdf_name) for pdf_name in pdf_names)
        if mese_successivo_complete:
            mese_successivo_status = "complete"
        else:
            mese_successivo_status = "incomplete"
    
    return {"complete": all_present, "mese_successivo": mese_successivo_status}

def check_month_for_files(year, month):
    base_folder = os.getenv('ARCHIVE_DIR')
    
    # Handle the last day of the month correctly (even for December)
    if month == 12:
        days_in_month = 31  # December always has 31 days
    else:
        # Safely get the number of days in the current month
        next_month = datetime(year, month % 12 + 1, 1)  # Wraps around month calculation
        days_in_month = (next_month - timedelta(days=1)).day

    today = datetime.now().date()

    month_files = {}
    for day in range(1, days_in_month + 1):
        current_day = datetime(year, month, day).date()
        if current_day > today:
            continue  # Skip future dates

        day_result = check_day_for_complete_files(base_folder, year, month, day)
        month_files[day] = day_result
    
    return month_files

def copy_file_to_destination(source_path, destination_folder):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    file_name = os.path.basename(source_path)
    destination_path = os.path.join(destination_folder, file_name)
    
    if os.path.exists(destination_path):
        return None
    
    shutil.copy2(source_path, destination_path)
    return destination_path

def check_up_to_date():
    base_folder = os.getenv('ARCHIVE_DIR')
    destination_folder = os.getenv('SOURCE_DIR')
    pdf_names = [f"Nucleo {letter}.pdf" for letter in "ABCDEFGI"]
    
    up_to_date = {}

    for pdf_name in pdf_names:
        latest_pdf = find_latest_pdf(base_folder, pdf_name)
        source_pdf = os.path.join(destination_folder, pdf_name)

        # Check if the source PDF exists
        if os.path.exists(source_pdf):
            # Get the last modified date of the source PDF
            last_modified = datetime.fromtimestamp(os.path.getmtime(source_pdf)).strftime('%Y-%m-%d')
            print(f"{pdf_name} is up-to-date (last modified: {last_modified})")
            up_to_date[pdf_name] = {"up_to_date": True, "latest_date": last_modified}
        else:
            # If the PDF is missing or outdated, retrieve the latest available version from the archive
            if latest_pdf:
                last_modified = datetime.fromtimestamp(os.path.getmtime(latest_pdf)).strftime('%Y-%m-%d')
                print(f"{pdf_name} is outdated or missing (latest available: {last_modified})")
                up_to_date[pdf_name] = {"up_to_date": False, "latest_date": last_modified}
            else:
                # If no version of the PDF is found in the archive
                print(f"{pdf_name} is missing (no available version found)")
                up_to_date[pdf_name] = {"up_to_date": False, "latest_date": "Not Available"}
    
    return up_to_date

def retrieve_terapie():
    base_folder = os.getenv('ARCHIVE_DIR')
    destination_folder = os.getenv('SOURCE_DIR')
    pdf_names = [f"Nucleo {letter}.pdf" for letter in "ABCDEFGI"]
    
    for pdf_name in pdf_names:
        latest_pdf = find_latest_pdf(base_folder, pdf_name)
        if latest_pdf:
            try:
                copy_file_to_destination(latest_pdf, destination_folder)
            except Exception as e:
                print(f"Error processing {pdf_name}: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        result = check_up_to_date()
        print(result)
    elif len(sys.argv) > 1 and sys.argv[1] == "retrieve":
        retrieve_terapie()
