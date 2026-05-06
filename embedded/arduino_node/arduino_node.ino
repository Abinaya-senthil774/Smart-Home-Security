/*
  arduino_node.ino - For Arduino MEGA 2560
  Reads analog and digital sensor data and outputs JSON over USB Serial 
  for the Raspberry Pi Central Node.
*/

// ==========================================
// PIN DEFINITIONS (Based on Table 1 of Report)
// ==========================================

// Temperature Sensors (LM35) [A0-A3]
const int tempPins[4] = {A0, A1, A2, A3};

// Light Sensors (LDR + resistor) [A4-A7]
const int lightPins[4] = {A4, A5, A6, A7}; 

// Sound Sensors (Mic sensor) [A8-A11]
const int soundPins[4] = {A8, A9, A10, A11};

// CO2 Sensor (MH-Z19B) [A12, A13]
const int co2Pin = A12;
const int co2SlopePin = A13;

// PIR Motion Sensors (HC-SR501) [D2, D3]
const int pirPins[2] = {2, 3}; 


void setup() {
  // Initialize Serial Communication at 9600 baud rate.
  // The Raspberry Pi Python script will need to listen at this same baud rate.
  Serial.begin(9600);

  // Initialize digital pins for PIR sensors as INPUT
  pinMode(pirPins[0], INPUT);
  pinMode(pirPins[1], INPUT);

  // Note: Analog pins (A0-A13) do not require explicit pinMode declarations 
  // when using analogRead(), but it is good practice to know they are inputs.
}

void loop() {
  // 1. Read Temperature Sensors
  int t1 = analogRead(tempPins[0]);
  int t2 = analogRead(tempPins[1]);
  int t3 = analogRead(tempPins[2]);
  int t4 = analogRead(tempPins[3]);

  // 2. Read Light Sensors
  int l1 = analogRead(lightPins[0]);
  int l2 = analogRead(lightPins[1]);
  int l3 = analogRead(lightPins[2]);
  int l4 = analogRead(lightPins[3]);

  // 3. Read Sound Sensors
  int s1 = analogRead(soundPins[0]);
  int s2 = analogRead(soundPins[1]);
  int s3 = analogRead(soundPins[2]);
  int s4 = analogRead(soundPins[3]);

  // 4. Read CO2 Sensor
  int co2 = analogRead(co2Pin);
  int co2_slope = analogRead(co2SlopePin);

  // 5. Read PIR Sensors
  int pir1 = digitalRead(pirPins[0]);
  int pir2 = digitalRead(pirPins[1]);

  // ==========================================
  // CONSTRUCT AND SEND JSON STRING
  // ==========================================
  // The data is printed directly to the Serial port. 
  // The Raspberry Pi will read this incoming stream and parse it using json.loads().
  
  Serial.print("{");
  
  // Temperature
  Serial.print("\"S1_Temp\":"); Serial.print(t1); Serial.print(",");
  Serial.print("\"S2_Temp\":"); Serial.print(t2); Serial.print(",");
  Serial.print("\"S3_Temp\":"); Serial.print(t3); Serial.print(",");
  Serial.print("\"S4_Temp\":"); Serial.print(t4); Serial.print(",");
  
  // Light
  Serial.print("\"S1_Light\":"); Serial.print(l1); Serial.print(",");
  Serial.print("\"S2_Light\":"); Serial.print(l2); Serial.print(",");
  Serial.print("\"S3_Light\":"); Serial.print(l3); Serial.print(",");
  Serial.print("\"S4_Light\":"); Serial.print(l4); Serial.print(",");
  
  // Sound
  Serial.print("\"S1_Sound\":"); Serial.print(s1); Serial.print(",");
  Serial.print("\"S2_Sound\":"); Serial.print(s2); Serial.print(",");
  Serial.print("\"S3_Sound\":"); Serial.print(s3); Serial.print(",");
  Serial.print("\"S4_Sound\":"); Serial.print(s4); Serial.print(",");
  
  // CO2
  Serial.print("\"S5_CO2\":"); Serial.print(co2); Serial.print(",");
  Serial.print("\"S5_CO2_Slope\":"); Serial.print(co2_slope); Serial.print(",");
  
  // PIR
  Serial.print("\"S6_PIR\":"); Serial.print(pir1); Serial.print(",");
  Serial.print("\"S7_PIR\":"); Serial.print(pir2);
  
  Serial.println("}"); // End the JSON object and add a newline character (\n)

  // ==========================================
  // DELAY
  // ==========================================
  // Wait before sending the next reading. 
  // 2000 milliseconds (2 seconds) is a safe default to prevent overwhelming the Pi's serial buffer.
  delay(2000); 
}
