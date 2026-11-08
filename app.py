from flask import Flask, render_template_string, request, redirect, url_for
import csv
from datetime import datetime
import os

app = Flask(__name__)
CSV_FILE = "attendance.csv"

# Ensure CSV header exists
if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Student_ID", "Status"])

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Smart Attendance System - Web Entry</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f6f9; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        h2 { color: #333; margin-top: 0; }
        .input-group { margin-bottom: 15px; }
        input[type="text"] { width: 70%; padding: 10px; font-size: 16px; border: 1px solid #ccc; border-radius: 4px; }
        button { padding: 10px 18px; font-size: 16px; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        .alert-success { background-color: #d4edda; color: #155724; padding: 12px; border-radius: 4px; margin-bottom: 15px; border: 1px solid #c3e6cb; }
        .alert-warning { background-color: #fff3cd; color: #856404; padding: 12px; border-radius: 4px; margin-bottom: 15px; border: 1px solid #ffeeba; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #343a40; color: white; }
        tr:hover { background-color: #f1f1f1; }
        .status { color: #28a745; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Smart Attendance System</h2>
        
        {% if msg %}
            <div class="{{ msg_class }}">{{ msg }}</div>
        {% endif %}

        <form action="/submit" method="POST" class="input-group">
            <input type="text" name="student_id" placeholder="Enter Roll Number (e.g., 124CS0003)" required autofocus>
            <button type="submit">Submit</button>
        </form>

        <h3>Live Attendance Log</h3>
        <table>
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Student ID</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {% for row in records %}
                <tr>
                    <td>{{ row[0] }}</td>
                    <td>{{ row[1] }}</td>
                    <td class="status">{{ row[2] }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

def is_already_present(student_id, today_date):
    if not os.path.exists(CSV_FILE):
        return False
        
    target_id = str(student_id).strip().upper()
    
    with open(CSV_FILE, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or len(row) < 2:
                continue
            
            raw_timestamp = row[0].strip()
            raw_id = row[1].strip().upper()
            
            if raw_id == "STUDENT_ID":
                continue
                
            row_date = raw_timestamp.split()[0] if " " in raw_timestamp else raw_timestamp
            
            print(f"[CHECK] Target: '{target_id}' vs Row ID: '{raw_id}' | Today: '{today_date}' vs Row Date: '{row_date}'")
            
            if raw_id == target_id and row_date == today_date:
                return True
    return False

@app.route('/')
def index():
    msg = request.args.get('msg', '')
    msg_type = request.args.get('type', '')
    msg_class = 'alert-success' if msg_type == 'success' else 'alert-warning'

    records = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 3 and row[1].strip().upper() != "STUDENT_ID":
                    records.append([row[0].strip(), row[1].strip(), row[2].strip()])
            records = records[::-1]

    return render_template_string(HTML_TEMPLATE, records=records, msg=msg, msg_class=msg_class)

@app.route('/submit', methods=['POST'])
def submit():
    student_id = request.form.get('student_id', '').strip()
    if student_id:
        now = datetime.now()
        today_date = now.strftime("%Y-%m-%d")
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

        if is_already_present(student_id, today_date):
            print(f"[{timestamp}] -> REJECTED DUPLICATE: {student_id}")
            return redirect(url_for('index', msg=f"Roll No. '{student_id}' is ALREADY PRESENT today!", type="warning"))

        with open(CSV_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, student_id, "PRESENT"])
        
        print(f"[{timestamp}] -> SUCCESS LOGGED: {student_id}")
        return redirect(url_for('index', msg=f"Attendance logged successfully for '{student_id}'.", type="success"))
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    print("Starting Web Portal on http://localhost:5000...")
    app.run(port=5000, debug=False)