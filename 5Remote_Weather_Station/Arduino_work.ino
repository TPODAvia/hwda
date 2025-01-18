#include <DHT.h>
#include <WiFiEspAT.h>
#include <PubSubClient.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <Wire.h>

// WiFi credentials
const char ssid[] = "Galaxy S10"; // your network SSID (name)
const char pass[] = "123456789"; // your network password

// Pin and sensor definitions
#define DHTPIN 5
#define DHTTYPE DHT11
#define TEMTPIN A0

// Communication with ESP8266
#define ESP_BAUDRATE 115200
#define SERIAL_PORT Serial1

// Initialize WiFi and MQTT
WiFiClient client;
PubSubClient mqttClient(client);

// Initialize sensors
DHT dht(DHTPIN, DHTTYPE);
Adafruit_BME280 bme; // I2C interface

// MQTT server information
IPAddress mqtt_server(192, 168, 172, 122); // your Raspberry MQTT server IP
const char *topic = "channel1";

void setup() {
    // Initialize serial communication
    Serial.begin(9600);
    SERIAL_PORT.begin(ESP_BAUDRATE);

    pinMode(LED_BUILTIN, OUTPUT);
    dht.begin();

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

    // Initialize BME280 sensor
    Wire.begin();
    if (!bme.begin(0x76)) { // Replace 0x76 with your sensor's I2C address
        Serial.println("Could not find BME280 sensor! Check wiring.");
        while (1);
    }
    Serial.println("Found BME280 sensor! Success.");
}

void loop() {
    digitalWrite(LED_BUILTIN, LOW); // LED ON

    // Read sensor data
    float h = dht.readHumidity();
    float t = dht.readTemperature();
    float pressure = bme.readPressure() / 100.0F; // Convert to hPa
    float temper = bme.readTemperature();

    int lightVal = analogRead(TEMTPIN) * 0.9765625;

    // Print sensor values
    Serial.println("Temperature (DHT): " + String(round(t)) + " °C");
    Serial.println("Humidity: " + String(round(h)) + " %");
    Serial.println("Light Intensity: " + String(lightVal));
    Serial.println("Temperature (BME280): " + String(round(temper)) + " °C");
    Serial.println("Pressure: " + String(round(pressure)) + " hPa");

    // Ensure MQTT connection
    if (!mqttClient.connected()) {
        connectMQTT();
    }

    // Publish data to MQTT
    String payload = "{\"t_dht\":\"" + String(round(t)) + "\", \"h\":\"" +
                     String(round(h)) + "\", \"p\":\"" + String(round(pressure)) +
                     "\", \"t_bme\":\"" + String(round(temper)) + "\", \"l\":\"" + 
                     String(lightVal) + "\"}";
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
