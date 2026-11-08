import asyncio
import csv
from datetime import datetime
import aiocoap
import aiocoap.resource as resource

CSV_FILE = "attendance.csv"

# Create CSV file with header if it doesn't exist
try:
    with open(CSV_FILE, "x", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Student_ID", "Status"])
except FileExistsError:
    pass

class AttendanceResource(resource.Resource):
    def __init__(self):
        super().__init__()

    async def render_post(self, request):
        student_id = request.payload.decode('utf-8').strip()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if student_id:
            with open(CSV_FILE, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, student_id, "PRESENT"])
            
            print(f"[{timestamp}] Attendance logged for Student ID: {student_id}")
            response_payload = f"SUCCESS: Logged ID {student_id} at {timestamp}".encode('utf-8')
            return aiocoap.Message(code=aiocoap.CHANGED, payload=response_payload)
        else:
            return aiocoap.Message(code=aiocoap.BAD_REQUEST, payload=b"ERROR: Empty ID")

async def main():
    root = resource.Site()
    root.add_resource(['attendance'], AttendanceResource())

    # Playit forwards traffic to this machine's loopback interface.
    await aiocoap.Context.create_server_context(root, bind=('127.0.0.1', 5683))
    print("---------------------------------------------------------")
    print("CoAP Attendance Server running locally on UDP port 5683...")
    print("Waiting for incoming attendance logs from Wokwi...")
    print("---------------------------------------------------------")
    await asyncio.get_running_loop().create_future()

if __name__ == '__main__':
    asyncio.run(main())