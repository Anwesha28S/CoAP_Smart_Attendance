# Smart Attendance System

A hybrid attendance tracking system that combines a Flask web portal with an IoT-based CoAP input channel. Attendance records are stored in a shared CSV file and duplicate entries for the same student on the same date are prevented.

## Overview

This project supports two attendance submission paths:

- IoT hardware input via CoAP using an ESP32/Wokwi simulation
- Manual web entry through a simple Flask interface

Both methods write to the same `attendance.csv` file, so the system maintains a single attendance log across devices.

## Features

- Web-based attendance form for manual student roll number entry
- CoAP server for receiving device-based attendance logs
- Automatic duplicate detection per student per date
- Real-time attendance display in the web dashboard
- CSV-based storage for easy record access and portability

## System Architecture

1. Hardware / IoT layer: ESP32 sends student IDs over UDP through a `playit.gg` tunnel to the local CoAP server.
2. Web layer: Flask app exposes a browser interface at `http://localhost:5000`.
3. Data layer: `attendance.csv` stores timestamps, student IDs, and status entries.

## Repository Structure

```text
IoT proj/
├── app.py             # Flask web app for manual attendance entry
├── server.py          # CoAP server that listens for IoT attendance updates
├── attendance.csv     # Central attendance data store
├── requirements.txt   # Python dependencies
├── README.md          # Project documentation
```

## Prerequisites

Make sure you have the following installed:

- Python 3.9+
- `pip` for installing Python packages
- Optional: Wokwi or ESP32 simulation environment for hardware testing

## Installation

Open a terminal in the project folder and run:

```bash
pip install -r requirements.txt
```

## Running the Project

### 1. Start the CoAP server

```bash
python server.py
```

This starts the local CoAP listener on port `5683`.

### 2. Start the web portal

Open a second terminal and run:

```bash
python app.py
```

Then open:

```text
http://localhost:5000
```
### Live Hardware Simulation
You can run and test the ESP32 CoAP hardware simulation directly in your browser:
**[Wokwi ESP32 Simulation](https://wokwi.com/projects/479829434475947009)**
### 3. Submit attendance

- Manual entry: use the form on the web page
- IoT input: send a student roll number from the Wokwi/ESP32 simulation to the CoAP server

## Using `playit.gg` with Wokwi

If the simulator runs outside your local network, it cannot directly access `127.0.0.1`. A `playit.gg` tunnel forwards UDP traffic from the public simulation environment to the local CoAP server.

### Steps

1. Download and run `playit` on your PC.
2. Create a UDP tunnel pointing to port `5683`.
3. Check the generated tunnel address and mapped port.
4. Update the ESP32/Wokwi code with the tunnel IP and port.

Example:

```cpp
IPAddress coapServerIP(147, 185, 221, 217);
const int coapPort = 32792;
```

> Note: The tunnel IP may change occasionally, so re-check the mapping if communication fails.

## Data Format

The attendance file is stored as CSV with the following columns:

```csv
Timestamp,Student_ID,Status
2026-11-08 09:15:00,124CS0058,PRESENT
```

The app checks whether a student has already marked attendance on the current date and rejects duplicate entries.

## Troubleshooting

- If the Flask app does not open, verify Python dependencies are installed.
- If the IoT input is not received, confirm the `playit.gg` tunnel and port are configured correctly.
- If the server does not accept requests, make sure no other service is already bound to port `5683`.

## License

This project is intended for educational and prototype use.
