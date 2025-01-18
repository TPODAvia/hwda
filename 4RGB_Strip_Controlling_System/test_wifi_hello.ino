#include <WiFiEspAT.h>

// Replace with your network credentials
char ssid[] = "Galaxy S10";      // Your network SSID
char pass[] = "123456789";       // Your network password

// Create a server on port 80
WiFiServer server(80);

void setup() {
  // Initialize Serial for debugging
  Serial.begin(115200);
  while (!Serial) {
    ; // Wait for Serial to be ready
  }

  // Initialize Serial1 for ESP-01 communication
  Serial1.begin(115200);       // Make sure ESP-01 is set to this baud rate
  WiFi.init(Serial1);

  // Connect to Wi-Fi
  Serial.println("Connecting to Wi-Fi...");
  if (WiFi.begin(ssid, pass)) {
    Serial.println("Connected to Wi-Fi!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("Failed to connect to Wi-Fi.");
    while (true);  // Halt on failure
  }

  // Start the web server
  server.begin();
  Serial.println("Web server started!");
}

void loop() {
  // Reconnect if Wi-Fi is disconnected
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi disconnected. Reconnecting...");
    WiFi.begin(ssid, pass);
    while (WiFi.status() != WL_CONNECTED) {
      delay(1000);
      Serial.print(".");
    }
    Serial.println("\nReconnected to Wi-Fi.");
  }

  // Listen for incoming clients
  WiFiClient client = server.available();
  if (client) {
    Serial.println("New client connected");

    // Read the incoming HTTP request
    String request = client.readStringUntil('\r');
    Serial.println(request);

    // Send an HTTP response
    client.print(
      "HTTP/1.1 200 OK\r\n"
      "Content-Type: text/html\r\n"
      "Connection: close\r\n"
      "\r\n"
      "<!DOCTYPE HTML>\r\n"
      "<html>Hello, world!</html>"
    );
    delay(1);
    client.stop();
    Serial.println("Client disconnected");
  }
}