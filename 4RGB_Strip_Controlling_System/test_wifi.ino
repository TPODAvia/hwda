#include <WiFiEsp.h>
#include "aREST.h"

#define ESP_BAUDRATE 9600

char ssid[] = "Galaxy S10";      // Your network SSID (name)
char pass[] = "123456789";  // Your network password
int status = WL_IDLE_STATUS;    // The WiFi radio's status
WiFiEspServer server(80);
aREST rest = aREST();

// Functions for handling LED strip
int setStripColor(String command);
int setClearStrip(String command);
int setRainbow(String command);

// Initialize the WiFi and ESP-01 module
void setup() {
  // Start the serial communication with the PC
  Serial.begin(115200);
  while (!Serial); // Wait for Serial monitor to open

  Serial.println("Searching for ESP8266...");

  // Initialize Serial3 for communication with ESP-01
  Serial3.begin(ESP_BAUDRATE);

  // Initialize WiFi library with the ESP-01 module
  WiFi.init(&Serial3);

  // Check if the WiFi module is available
  if (WiFi.status() == WL_NO_SHIELD) {
    Serial.println("WiFi shield not present");
    while (true); // Don't proceed
  }

  // Attempt to connect to the WiFi network
  while (status != WL_CONNECTED) {
    Serial.print("Attempting to connect to WPA SSID: ");
    Serial.println(ssid);
    status = WiFi.begin(ssid, pass);
  }

  Serial.println("You're connected to the network");
  printWifiStatus();

  // Start the server
  server.begin();

  // Register functions with aREST
  rest.function("fill", setStripColor);
  rest.function("clear", setClearStrip);
  rest.function("rainbow", setRainbow);
}

void loop() {
  // Listen for incoming clients
  WiFiEspClient client = server.available();
  if (client) {
    rest.handle(client);
  }
}

// Utility to parse command data
struct data {
  String color;
  int dir;
  int wait;
  int func;
  int r, g, b;
};

struct data parseCommand(String command) {
  struct data parsedData;
  parsedData.color = command.substring(1, 7);
  String p = command.substring(0, 1);
  parsedData.dir = p.toInt();
  p = command.substring(7, 9);
  parsedData.wait = p.toInt();
  parsedData.func = command.substring(9).toInt();
  long tmpColor = strtol(&("#" + parsedData.color)[1], NULL, 16);
  parsedData.g = tmpColor >> 8 & 0xFF;
  parsedData.r = tmpColor >> 16;
  parsedData.b = tmpColor & 0xFF;
  return parsedData;
}

int setStripColor(String command) {
  Serial.println("Color strip function...");
  struct data value = parseCommand(command);
  debugData(value);
  // fillStrip(strip.Color(value.g, value.r, value.b), value.wait, value.dir); // Uncomment with your LED strip library
  return 1;
}

int setClearStrip(String command) {
  Serial.println("Clear strip function...");
  struct data value = parseCommand(command);
  debugData(value);
  // clearStrip(value.wait, value.dir); // Uncomment with your LED strip library
  return 1;
}

int setRainbow(String command) {
  Serial.println("Rainbow strip function...");
  struct data value = parseCommand(command);
  debugData(value);
  // rainbow(value.wait, value.dir); // Uncomment with your LED strip library
  return 1;
}

void debugData(struct data value) {
  Serial.println("=========================");
  Serial.println("Color [" + value.color + "]");
  Serial.println("Direction [" + String(value.dir) + "]");
  Serial.println("Wait [" + String(value.wait) + "]");
  Serial.println("Func [" + String(value.func) + "]");
  Serial.println("R [" + String(value.r) + "]");
  Serial.println("G [" + String(value.g) + "]");
  Serial.println("B [" + String(value.b) + "]");
  Serial.println("=========================");
}

void printWifiStatus() {
  // Print the SSID of the network you're attached to
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());
  
  // Print your WiFi shield's IP address
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);
  
  // Print where to go in the browser
  Serial.println();
  Serial.print("To see this page in action, open a browser to http://");
  Serial.println(ip);
  Serial.println();
}
