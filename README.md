# Smart Home Security Automation System

This project focuses on automating a full-fledged home security system to detect theft, intruders, and fire hazards. It features a dual-layer security architecture covering both the interior and exterior of the house.

For exterior security, CCTV cameras utilize computer vision techniques—including moving object detection via Non-Max Suppression and HOG descriptors, as well as face recognition using OpenCV and DeepFace. For interior security, a network of non-invasive sensors (temperature, light, sound, CO2, and PIR) collects environmental data. This data is processed by machine learning models to accurately predict room occupancy, while an Isolation Forest model detects anomalies such as fire hazards. Data is securely transferred in real-time via MQTT and logged into a PostgreSQL database, allowing users to view alerts and sensor logs through a user-friendly Node.js web dashboard.

---

## 📂 Project Structure
```text
smart-home-security/
│
├── dashboard/                 # Frontend Web Interface
│   ├── public/                # HTML/JS/CSS files for the UI
│   ├── package.json           # Node.js dependencies
│   └── server.js              # Node.js/Express backend API routes
│
├── embedded/                  # Microcontroller code
│   └── arduino_node/
│       └── arduino_node.ino   # Arduino script to read sensors and output JSON via USB
│
├── exterior/                  # CCTV, Face Recognition, and Motion Detection
│   ├── config.json            # Reference image paths and camera configurations
│   ├── main_exterior.py       # Main video capture loop and logic processing
│   ├── ui_alerts.py           # Tkinter interface for user confirmation prompts
│   └── vision_utils.py        # Helper functions for DeepFace and Haar Cascades
│
├── integration/               # Central Node messaging and Database linking
│   └── mqtt_client.py         # Subscribes to MQTT topics and pushes to PostgreSQL
│
├── interior/                  # Sensor Data ML and Occupancy Prediction
│   ├── data/                  # Directory for raw and cleaned CSV datasets
│   ├── models/                # Saved ML models (e.g., occupancy_model.pkl, scaler.pkl)
│   ├── data_pipeline.py       # Data cleaning and statistical feature extraction
│   ├── inference.py           # Real-time script for predicting occupancy from live data
│   └── train_model.py         # Script to train and save the Logistic Regression/NN model
│
├── README.md                  # Project overview and usage instructions
└── requirements.txt           # Python dependencies required to run the project
```

---

## ⭐ Key Features

*   **Dual-Layer Monitoring:** Integrates both exterior CCTV analysis and interior environmental sensor processing into a single, comprehensive system.
*   **Advanced Exterior Vision:** Uses Background Subtraction (MOG2) for motion tracking, HOG+NMS for human detection, and DeepFace for verifying family members versus unknown intruders.
*   **Predictive Interior Security:** Employs a machine learning model trained on PyTorch/scikit-learn to determine room occupancy based on multi-sensor data.
*   **Fire & Anomaly Detection:** Utilizes Isolation Forest to flag abnormal sensor readings (e.g., sudden CO2 or temperature spikes) indicative of a house fire.
*   **Secure IoT Messaging:** Uses Mosquitto MQTT as a local broker bridged to CloudMQTT with TLS encryption to reliably transfer data payloads every 10 seconds.
*   **Time-Series Database:** Leverages PostgreSQL combined with TimescaleDB to create continuous aggregate views of sensor data over time.

---

## ⭐ Hardware Requirements

To replicate the physical architecture of this system, you will need the following components:

*   **Microcontrollers & Computers:** 
    *   3x Raspberry Pi (for central and camera nodes)
    *   1x Arduino Uno (for local sensor reading)
*   **Sensors:** 
    *   4x LM35 (Temperature)
    *   4x LDR + Resistors (Light)
    *   4x Analog Mic Sensors (Sound)
    *   1x MH-Z19B (CO2)
    *   2x HC-SR501 (PIR Motion)
*   **Peripherals:** IP/CCTV Cameras, jumper wires, breadboards, and appropriate power supplies.

---
![hardware](assets/backend.png)

## ⭐ System Workflow & Data Pipeline

This project operates on a distributed architecture, merging embedded hardware, computer vision, and machine learning into a single data pipeline:

**1. Exterior Security Segment**
*   **Hardware:** IP/CCTV cameras mounted outside, connected to local edge nodes (Raspberry Pi A & B).
*   **Software (Vision Processing):** Captures live video feeds and applies MOG2 for background subtraction to detect motion. If motion is detected, it uses HOG + Non-Maximum Suppression (NMS) to detect human shapes. OpenCV's Haar Cascades detect faces, and DeepFace verifies them against known family members.
*   **Flow:** Video Capture ➔ Motion Detection ➔ Human/Face Detection ➔ Face Verification.

**2. Interior Security Segment**
*   **Hardware:** A localized sensor suite in each room connected to an Arduino Mega.
*   **Software (Edge Collection):** The Arduino script reads analog and digital pins, formats the sensor states into a structured JSON payload, and transmits it via USB serial.
*   **Flow:** Environmental Changes ➔ Analog/Digital Sensors ➔ Arduino Processing ➔ JSON Serial Output.

**3. Integration & Central Processing (The "Brain")**
*   **Hardware:** A Central Raspberry Pi acting as the main hub.
*   **Software (Routing & ML):** Reads the Arduino's JSON and receives camera metadata. Publishes data locally via Mosquitto MQTT, securely bridged (TLS encryption) to CloudMQTT. A Python client subscribes to these topics, parsing data every 10-30 seconds. Sensor data is fed into a pre-trained ML model to predict room occupancy and an Isolation Forest model to flag fire anomalies.
*   **Flow:** Arduino JSON & Camera Logs ➔ Central Pi ➔ Local MQTT ➔ CloudMQTT ➔ Python Inference Script.

**4. Output to User**
*   **Hardware:** User's personal device accessing the web server.
*   **Software (Database & Dashboard):** ML predictions, camera logs, and raw sensor data are committed to a PostgreSQL database utilizing TimescaleDB. A Node.js/Express backend queries this database and serves the data to an HTML/JS frontend dashboard. 
*   **Instant Alerts:** If an unknown face is detected outside, a Tkinter dialog box immediately prompts the owner for verification.
*   **Flow:** Python Client ➔ PostgreSQL/TimescaleDB ➔ Node.js API ➔ Web Dashboard & Desktop Alerts.

---

## ⭐ Installation & Setup

**Prerequisites**
*   Python 3.8+
*   Node.js & npm
*   Arduino IDE
*   PostgreSQL (with TimescaleDB extension installed)
*   Mosquitto MQTT Broker

**1. Clone the repository**
```bash
git clone [https://github.com/yourusername/smart-home-security.git](https://github.com/yourusername/smart-home-security.git)
cd smart-home-security
```

**2. Install Python Dependencies**  
*(It is highly recommended to use a virtual environment)*
```bash
pip install -r requirements.txt
```

**3. Install Node.js Dependencies**
```bash
cd dashboard
npm install
cd ..
```

---

## ⭐ Usage Guide

**Step 1: Hardware Initialization (Arduino)**
Flash `embedded/arduino_node/arduino_node.ino` to your Arduino Uno. Ensure it is actively reading from the sensor suite and printing JSON payloads to the serial monitor.

**Step 2: Train the Interior ML Model**
Navigate to the interior module to clean the raw sensor data, extract features, and train the occupancy prediction model.
```bash
cd interior
python train_model.py
```

**Step 3: Start the MQTT Bridge & Integration Node**
Ensure your local Mosquitto broker is running. Start the Python client to subscribe to sensor topics, run real-time inference, and log outputs to TimescaleDB.
```bash
cd integration
python mqtt_client.py
```

**Step 4: Launch Exterior Security Vision**
Run the computer vision script on the camera-connected nodes.
```bash
cd exterior
python main_exterior.py
```

**Step 5: Run the Web Dashboard**
Start the Express server to serve the frontend UI.
```bash
cd dashboard
node server.js
```

---

## ⭐ API Reference

The Node.js Express server exposes the following endpoints for the frontend to retrieve logs:

*   `GET /api/sensor-data`: Retrieves historical and real-time environmental data.
*   `GET /api/camera-data`: Fetches camera logs including timestamps and recognized people.
*   `GET /api/triggered-events`: Returns a log of all system alerts (e.g., motion detected, fire anomalies).

---

## ⭐ Future Roadmap

*   **Mobile Application Integration:** Push notifications directly to iOS/Android.
*   **Battery Backup System:** Implementing UPS for the Raspberry Pis and Arduino to ensure uptime during power cuts.
*   **Smart Lock Integration:** Triggering automated door locking mechanisms when unauthorized intruders are detected.
