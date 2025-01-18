#include <WiFiEspAT.h>
#include <PubSubClient.h>

// WiFi credentials
const char ssid[] = "Galaxy S10"; // your network SSID (name)
const char pass[] = "123456789"; // your network password

// Communication with ESP8266
#define ESP_BAUDRATE 115200
#define SERIAL_PORT Serial1

// Initialize WiFi and MQTT
WiFiClient client;
PubSubClient mqttClient(client);

// MQTT server information
IPAddress mqtt_server(192, 168, 172, 122); // your Raspberry MQTT server IP
const char *topic = "channel1";

void setup() {
    // Initialize serial communication
    Serial.begin(115200);
    SERIAL_PORT.begin(ESP_BAUDRATE);

    pinMode(LED_BUILTIN, OUTPUT);

    // Initialize WiFiEspAT library
    WiFi.init(SERIAL_PORT);

    // Wait for the ESP8266 to respond
    if (WiFi.status() == WL_NO_MODULE) {
        Serial.println("ESP8266 module not found!");
        while (true);
    }

    Serial.println("Attempting to connect to WiFi...");
    connectWiFi();

    Serial.println("WiFi connected!");
    initMQTT();
}

void loop() {
    digitalWrite(LED_BUILTIN, LOW); // LED ON

    // Generate dummy values for testing
    float temperature = 25.0; // Dummy temperature value
    float humidity = 50.0;    // Dummy humidity value
    float pressure = 1013.25; // Dummy pressure value (hPa)
    int lightVal = 100;       // Dummy light intensity value

    // Print dummy values
    Serial.println("Temperature: " + String(temperature) + " °C");
    Serial.println("Humidity: " + String(humidity) + " %");
    Serial.println("Pressure: " + String(pressure) + " hPa");
    Serial.println("Light Intensity: " + String(lightVal));

    // Ensure MQTT connection
    if (!mqttClient.connected()) {
        connectMQTT();
    }

    // Publish dummy data to MQTT
    String payload = "{\"temperature\":\"" + String(temperature) + "\", \"humidity\":\"" +
                     String(humidity) + "\", \"pressure\":\"" + String(pressure) +
                     "\", \"light\":\"" + String(lightVal) + "\"}";
    mqttClient.publish(topic, payload.c_str());
    Serial.println("Published: " + payload);

    digitalWrite(LED_BUILTIN, HIGH); // LED OFF
    delay(30000); // Delay for 30 seconds
}

void connectWiFi() {
    while (WiFi.status() != WL_CONNECTED) {
        Serial.print("Connecting to SSID: ");
        Serial.println(ssid);
        WiFi.begin(ssid, pass);

        // Wait for connection
        delay(5000);
    }
}

void initMQTT() {
    mqttClient.setServer(mqtt_server, 1883);
}

void connectMQTT() {
    while (!mqttClient.connected()) {
        Serial.println("Connecting to MQTT Server...");
        if (mqttClient.connect("clientID")) {
            Serial.println("MQTT Client connected!");
        } else {
            Serial.println("MQTT Client failed to connect. Retrying in 5 seconds...");
            delay(5000);
        }
    }
}
