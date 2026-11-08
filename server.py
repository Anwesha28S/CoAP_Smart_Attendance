import asyncio
import csv
import os
from datetime import datetime
import aiocoap
import aiocoap.resource as resource

CSV_FILE = "attendance.csv"

logged_today = set()

def load_existing_records():
    """Load all existing records from CSV into the in-memory set."""
    logged_today.clear()
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if not row or len(row) < 2:
                    continue
                raw_ts = row[0].strip()
                raw_id = row[1].strip().upper()

                if raw_id == "STUDENT_ID" or raw_ts.upper() == "TIMESTAMP":
                    continue
                row_date = raw_ts.split()[0] if " " in raw_ts else raw_ts
                logged_today.add((row_date, raw_id))


try:
    with open(CSV_FILE, "x", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Student_ID", "Status"])
except FileExistsError:
    pass

load_existing_records()

class AttendanceResource(resource.Resource):
    def __init__(self):
        super().__init__()

    async def render_post(self, request):
        student_id = request.payload.decode('utf-8').strip().upper()
        now = datetime.now()
        today_date = now.strftime("%Y-%m-%d")
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        
        if not student_id:
            return aiocoap.Message(code=aiocoap.BAD_REQUEST, payload=b"ERROR: Empty ID")

        load_existing_records()

  
        if (today_date, student_id) in logged_today:
            print(f"[{timestamp}] -> REJECTED DUPLICATE: {student_id}")
            response_payload = f"DUPLICATE: {student_id} already logged today".encode('utf-8')
            return aiocoap.Message(code=aiocoap.FORBIDDEN, payload=response_payload)


        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, student_id, "PRESENT"])
            f.flush()

        logged_today.add((today_date, student_id))
        
        print(f"[{timestamp}] -> SUCCESS LOGGED: {student_id}")
        response_payload = f"SUCCESS: Logged ID {student_id} at {timestamp}".encode('utf-8')
        return aiocoap.Message(code=aiocoap.CHANGED, payload=response_payload)

async def main():
    root = resource.Site()
    root.add_resource(['attendance'], AttendanceResource())

    await aiocoap.Context.create_server_context(root, bind=('127.0.0.1', 5683))
    print("---------------------------------------------------------")
    print("CoAP Attendance Server running locally on UDP port 5683...")
    print("Waiting for incoming attendance logs from Wokwi...")
    print("---------------------------------------------------------")
    await asyncio.get_running_loop().create_future()

if __name__ == '__main__':
    asyncio.run(main())