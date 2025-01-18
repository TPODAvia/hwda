void setup() {
  // Initialize Serial for debugging (connected to PC)
  Serial.begin(115200);
  while (!Serial) {
    ; // Wait for Serial to initialize
  }
  Serial.println("Serial bridge started. Type anything:");

  // Initialize Serial1 for ESP-01 communication
  Serial1.begin(115200); // Adjust if your ESP-01 uses a different baud rate
}

void loop() {
  // Forward data from Serial to Serial1
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n'); // Read input until newline
    Serial1.println(command);                     // Send input to ESP-01
  }

  // Forward data from Serial1 to Serial
  if (Serial1.available()) {
    String response = Serial1.readString(); // Read input from ESP-01
    Serial.print(response);                 // Send input back to Serial Monitor
  }
}
