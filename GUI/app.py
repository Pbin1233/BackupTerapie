import os
import sys
import subprocess
from flask import Flask, jsonify, render_template

# Add the path to the Retrieve folder dynamically
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Retrieve'))

# Now import the check_up_to_date function
from Retrieve import check_up_to_date, check_month_for_files


app = Flask(__name__)

# Set the path to Retrieve.py dynamically based on the current project structure
retrieve_script_path = os.path.join(os.path.dirname(__file__), '..', 'Retrieve', 'Retrieve.py')

# Route to serve the index.html file
@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/check_month/<int:year>/<int:month>', methods=['GET'])
def check_month_route(year, month):
    try:
        month_files = check_month_for_files(year, month)
        return jsonify(month_files), 200
    except Exception as e:
        print(f"Error checking files for {year}-{month}: {str(e)}")
        return jsonify({"error": "Something went wrong on the server"}), 500


@app.route('/check_up_to_date', methods=['GET'])
def check_up_to_date_route():
    up_to_date = check_up_to_date()  # This should now return a clean dictionary
    return jsonify(up_to_date)  # Return only the clean JSON data

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

if __name__ == '__main__':
    app.run(debug=True)
