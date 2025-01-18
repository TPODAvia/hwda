#include <DHT.h>
#include <WiFiEsp.h>
#include <PubSubClient.h>
#include <BME280I2C.h>
#include <Wire.h>

// WiFi credentials
char ssid[] = "Galaxy S10"; // your network SSID (name)
char pass[] = "123456789"; // your network password
int status = WL_IDLE_STATUS; // the WiFi radio's status

// Pin and sensor definitions
#define DHTPIN 5
#define DHTTYPE DHT11
#define TEMTPIN A0

// Emulate Serial1 on pins 6/7 if not present
#ifndef HAVE_HWSERIAL1
#include "SoftwareSerial.h"
SoftwareSerial Serial1(6, 7); // RX, TX
#endif

#define ESP_BAUDRATE 9600

// Initialize WiFi and MQTT
WiFiEspClient client;
PubSubClient mqttClient(client);

// Initialize sensors
DHT dht(DHTPIN, DHTTYPE);
BME280I2C bme;

// MQTT server information
IPAddress mqtt_server(192, 168, 1, 106); // your Raspberry MQTT server IP
char *topic = "channel1";

void setup() {
    // Initialize serial communication
    Serial.begin(ESP_BAUDRATE);
    pinMode(LED_BUILTIN, OUTPUT);
    dht.begin();
    
    Serial.println("Searching for ESP8266...");
    Serial1.begin(ESP_BAUDRATE);

    // Initialize WiFi module
    WiFi.init(&Serial1);

    // Check for the presence of the shield
    if (WiFi.status() == WL_NO_SHIELD) {
        Serial.println("WiFi shield not present");
        while (true);
    }

    // Attempt to connect to WiFi network
    while (status != WL_CONNECTED) {
        Serial.print("Attempting to connect to WPA SSID: ");
        Serial.println(ssid);
        status = WiFi.begin(ssid, pass);
        delay(1000);
    }

    Serial.println("You're connected to the network");
    initMQTT();

    // Initialize BME280 sensor
    Wire.begin();
    while (!bme.begin()) {
        Serial.println("Could not find BME280 sensor!");
        delay(1000);
    }

    switch (bme.chipModel()) {
        case BME280::ChipModel_BME280:
            Serial.println("Found BME280 sensor! Success.");
            break;
        case BME280::ChipModel_BMP280:
            Serial.println("Found BMP280 sensor! No Humidity available.");
            break;
        default:
            Serial.println("Found UNKNOWN sensor! Error!");
    }
}

void loop() {
    digitalWrite(LED_BUILTIN, LOW); // LED ON

    // Read sensor data
    float h = dht.readHumidity();
    float t = dht.readTemperature();
    float temper(NAN), humidity(NAN), press(NAN);

    BME280::TempUnit tempUnit(BME280::TempUnit_Celsius);
    BME280::PresUnit presUnit(BME280::PresUnit_Pa);
    bme.read(press, temper, humidity, tempUnit, presUnit);

    int lightVal = analogRead(TEMTPIN) * 0.9765625;

    // Print sensor values
    Serial.println("Temperature: " + String(round(t)));
    Serial.println("Humidity: " + String(round(h)));
    Serial.println("Light Intensity: " + String(lightVal));
    Serial.println("Pressure: " + String(round(press)));

    // Ensure MQTT connection
    if (!mqttClient.connected()) {
        connect();
    }

    // Publish data to MQTT
    String payload = "{\"t\":\"" + String(round(t)) + "\", \"h\":\"" +
                     String(round(h)) + "\", \"p\":\"" + String(round(press)) +
                     "\", \"l\":\"" + String(lightVal) + "\"}";
    mqttClient.publish(topic, payload.c_str());
    Serial.println("Published: " + payload);

    digitalWrite(LED_BUILTIN, HIGH); // LED OFF
    delay(30000); // Delay for 30 seconds
}

void initMQTT() {
    mqttClient.setServer(mqtt_server, 1883);
}

void connect() {
    while (!mqttClient.connected()) {
        Serial.println("Connecting to MQTT Server...");
        if (mqttClient.connect("clientID")) {
            Serial.println("Client connected");
        } else {
            Serial.println("Client not connected. Retrying in 5 seconds...");
            delay(5000);
        }
    }
}
