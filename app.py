import os
import sys
import subprocess
from flask import Flask, jsonify, render_template, request
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from ZUCCscraper.functions.driver_management import get_logs, log
from Retrieve.Retrieve import check_up_to_date, check_month_for_files

# Load environment variables from the .env file
load_dotenv()

# Get the SOURCE_DIR from the .env file
SOURCE_DIR = os.getenv('SOURCE_DIR')

if not SOURCE_DIR:
    raise ValueError("SOURCE_DIR is not defined in the environment variables.")


app = Flask(__name__)

# Set the path to Retrieve.py dynamically based on the current project structure
retrieve_script_path = os.path.join(os.path.dirname(__file__), '..', 'Retrieve', 'Retrieve.py')

def check_mese_successivo():
    today = datetime.today()
    last_day = (datetime(today.year, today.month + 1, 1) - timedelta(days=1)).day
    if today.day >= last_day - 25:  # If today is one of the last three days of the month
        mese_successivo_folder = os.path.join(SOURCE_DIR, 'Mese successivo')
        nucleo_files = [f"Nucleo {x}.pdf" for x in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'I']]
        mese_successivo_files = {file: os.path.exists(os.path.join(mese_successivo_folder, file)) for file in nucleo_files}
        return mese_successivo_files
    return None

# Route to serve the index.html file
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/force_retrieve', methods=['POST'])
def force_retrieve():
    try:
        log("Starting retrieval of PDFs", "INFO")

        # Construct the path to the .bat file dynamically
        bat_file_path = os.path.join(os.path.dirname(__file__), '..', 'ZUCCscraper', 'esegui_backup.bat')
        
        # Execute the .bat file and log each step
        subprocess.run([bat_file_path], check=True, shell=True)
        
        log("Retrieved PDF Nucleo A", "INFO")
        log("Retrieved PDF Nucleo B", "INFO")
        log("Retrieved PDF Nucleo C", "INFO")
        log("Retrieved PDF Nucleo D", "INFO")

        log("PDF retrieval process completed successfully", "INFO")

        # Optional: Call the check_up_to_date() here to ensure the latest data is available after retrieval
        updated_status = check_up_to_date()  # Fetch the latest PDF statuses
        return jsonify({
            "message": "Outdated PDFs retrieved from the web successfully!",
            "updated_status": updated_status
        }), 200
    except subprocess.CalledProcessError as e:
        log(f"Error retrieving PDFs: {str(e)}", "ERROR")
        return jsonify({"message": f"Error retrieving PDFs: {str(e)}"}), 500
    
# Polling route to fetch logs
@app.route('/logs', methods=['GET'])
def stream_logs():
    logs = get_logs()  # Get current logs from the log buffer
    return jsonify(logs), 200

@app.route('/pdf_saved', methods=['POST'])
def pdf_saved():
    try:
        data = request.get_json()
        Nucleo = data.get('Nucleo')
        file_path = data.get('file_path')
        
        # Logic to handle the saved PDF (e.g., update the table or calendar)
        # You can trigger a partial update of the frontend here, or store the info to refresh the calendar
        
        print(f"PDF for Nucleo {Nucleo} saved at {file_path}")
        return jsonify({"message": "PDF save acknowledged"}), 200
    except Exception as e:
        print(f"Error acknowledging PDF save: {e}")
        return jsonify({"message": "Error acknowledging PDF save"}), 500
    
@app.route('/check_month/<int:year>/<int:month>', methods=['GET'])
def check_month_route(year, month):
    try:
        month_files = check_month_for_files(year, month)
        return jsonify(month_files), 200
    except Exception as e:
        print(f"Error checking files for {year}-{month}: {str(e)}")
        return jsonify({"error": "Something went wrong on the server"}), 500


# New debug route
@app.route('/debug_up_to_date', methods=['GET'])
def debug_up_to_date():
    up_to_date = check_up_to_date()
    return jsonify(up_to_date)

# Route to trigger Terapie retrieval by running the retrieve command in Retrieve.py
@app.route('/retrieve_terapie', methods=['POST'])
def retrieve_terapie():
    try:
        # Call the Retrieve.py script to move the files
        subprocess.run(["python", retrieve_script_path, "retrieve"], check=True)
        return jsonify({"message": "Terapie retrieved successfully!"}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"message": "Error retrieving Terapie"}), 500

@app.route('/check_up_to_date', methods=['GET'])
def check_up_to_date_route():
    up_to_date = check_up_to_date()  # Existing function for checking current status
    mese_successivo_status = check_mese_successivo()  # Check Mese successivo PDFs if in the last three days of the month
    
    response = {
        'up_to_date': up_to_date,
        'mese_successivo': mese_successivo_status  # Include this data in the response
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
