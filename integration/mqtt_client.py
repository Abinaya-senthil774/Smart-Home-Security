"""
DESCRIPTION:
The Central Integration Node. This script connects to the MQTT broker, listens for 
incoming JSON sensor data and camera triggers, performs real-time ML inference to 
predict room occupancy, and logs everything into PostgreSQL/TimescaleDB.

INPUT:
Subscribes to MQTT topics (e.g., 'home/room1/sensors', 'home/security/motion/#').
Loads 'occupancy_model.pkl' and 'scaler.pkl' for real-time inference.

OUTPUT:
Prints live logs to the console and inserts timestamped rows (sensor data + predictions) 
directly into the PostgreSQL database for the Node.js dashboard to query.
"""

import paho.mqtt.client as mqtt
import json
import psycopg2
import pickle
import pandas as pd
import ssl
from datetime import datetime

# ==========================================
# 1. LOAD MACHINE LEARNING MODEL & SCALER
# ==========================================
# Assuming this script runs from the 'integration/' folder, 
# we point to the models saved in the 'interior/models/' folder.
try:
    with open('../interior/models/occupancy_model.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('../interior/models/scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
    print("✅ ML Model and Scaler loaded successfully.")
except Exception as e:
    print(f"❌ Error loading ML files: {e}")

# The feature order MUST exactly match the order used during training
FEATURES = ['S1_Light', 'S3_Light', 'S2_Light', 'S1_Temp', 'S7_PIR',
            'S2_Temp', 'S5_CO2', 'S3_Temp', 'S6_PIR', 'S5_CO2_Slope',
            'S1_Sound', 'S2_Sound', 'S3_Sound', 'S4_Temp', 'S4_Sound', 'S4_Light']

# ==========================================
# 2. POSTGRESQL / TIMESCALEDB SETUP
# ==========================================
try:
    # Update these credentials to match your PostgreSQL setup
    conn = psycopg2.connect(
        host="localhost",
        database="smarthome_db",
        user="postgres",
        password="yourpassword",
        port="5432"
    )
    cursor = conn.cursor()
    print("✅ Connected to PostgreSQL database.")
except Exception as e:
    print(f"❌ Database connection failed: {e}")


# ==========================================
# 3. MQTT CALLBACK FUNCTIONS
# ==========================================
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Successfully connected to MQTT Broker.")
        # Subscribe to topics defined in Table 2 of the report
        client.subscribe("home/+/sensors")      # Matches home/room1/sensors, etc.
        client.subscribe("home/security/#")     # Matches all security/camera topics
    else:
        print(f"❌ Failed to connect to MQTT Broker, return code {rc}")

def on_message(client, userdata, msg):
    topic = msg.topic
    
    try:
        # Parse incoming JSON payload
        payload = json.loads(msg.payload.decode('utf-8'))
        
        # ----------------------------------------------------
        # HANDLE SENSOR DATA (Predict Occupancy & Save to DB)
        # ----------------------------------------------------
        if "sensors" in topic:
            room_id = topic.split('/')[1]  # Extracts 'room1' from 'home/room1/sensors'
            
            # Extract features from JSON into a DataFrame
            input_data = [[payload.get(feat, 0) for feat in FEATURES]]
            df = pd.DataFrame(input_data, columns=FEATURES)
            
            # Scale the data and predict
            scaled_data = scaler.transform(df)
            prediction = model.predict(scaled_data)[0]
            
            print(f"📊 [SENSOR UPDATE] Room: {room_id} | Predicted Occupancy: {prediction}")
            
            # Insert the prediction and timestamp into PostgreSQL
            cursor.execute("""
                INSERT INTO sensor_logs (timestamp, room_id, predicted_occupancy, motion_detected, anomaly)
                VALUES (%s, %s, %s, %s, %s)
            """, (datetime.now(), room_id, int(prediction), False, False)) 
            conn.commit()

        # ----------------------------------------------------
        # HANDLE CAMERA / SECURITY EVENTS
        # ----------------------------------------------------
        elif "security" in topic:
            if "motion" in topic:
                print(f"⚠️ [MOTION ALERT] Camera: {topic} | Data: {payload}")
                # Optional: Update the database to flag motion for this specific timestamp
                
            elif "human" in topic:
                print(f"🚶 [HUMAN DETECTED] Camera: {topic} | Data: {payload}")
                
            elif "face/verified" in topic:
                print(f"✅ [FACE VERIFIED] Welcome back! Data: {payload}")
                
            elif "face/unverified" in topic:
                print(f"🚨 [UNKNOWN FACE] Data: {payload}")

    except Exception as e:
        print(f"❌ Error processing MQTT message on topic {topic}: {e}")

# ==========================================
# 4. MQTT CLIENT INITIALIZATION
# ==========================================
client = mqtt.Client(client_id="RaspberryPi_Central_Node")
client.on_connect = on_connect
client.on_message = on_message

# Uncomment and update the lines below if using CloudMQTT with TLS (Port 8883)
# client.username_pw_set("your_cloudmqtt_username", "your_cloudmqtt_password")
# client.tls_set(ca_certs="/etc/ssl/certs/ca-certificates.crt", tls_version=ssl.PROTOCOL_TLSv1_2)
# client.connect("your.cloudmqtt.url", 8883, 60)

# For local Mosquitto testing without TLS:
client.connect("localhost", 1883, 60)

# Start the loop to listen for messages continuously
print("⏳ Starting MQTT Listener loop...")
client.loop_forever()
