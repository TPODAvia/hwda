#include <WiFiEsp.h>
#include "aREST.h"
// Emulate Serial1 on pins 6/7 if not present
#ifndef HAVE_HWSERIAL1
#include "SoftwareSerial.h"
 SoftwareSerial Serial1(6, 7); // TX, RX
#endif
#define ESP_BAUDRATE 9600

 char ssid[] = "wifi_SSID"; // your network SSID (name)
 char pass[] = "wifi_PASSWORD"; // your network password
 int status = WL_IDLE_STATUS; // the Wifi radio's status
 WiFiEspServer server(80);
 aREST rest = aREST();
// Give name and ID to device (ID should be 6 characters long)
 //rest.set_id("002");
 //rest.set_name("my_1st_arest_device");
Serial.print("Searching for ESP8266...");
 // initialize serial for ESP module
Serial1.begin(ESP_BAUDRATE);
 // initialize ESP module
WiFi.init(&Serial1);
 // check for the presence of the shield
if (WiFi.status() == WL_NO_SHIELD) {
 Serial.println("WiFi shield not present");
 // don't continue
 while (true);
 }
 // attempt to connect to WiFi network
while ( status != WL_CONNECTED) {
    Serial.print("Attempting to connect to WPA SSID: ");
 Serial.println(ssid);
 // Connect to WPA/WPA2 network
 status = WiFi.begin(ssid, pass);
 }
Serial.println("You're connected to the network");
printWifiStatus();
server.begin();
rest.function("fill", setStripColor);
rest.function("clear", setClearStrip);
rest.function("rainbow", setRainbow);

WiFiEspClient client = server.available();
rest.handle(client);
//we have 2 comment this, otherwise there is a conflict with aRESt services:
//clearStrip(100, REVERSE);
//rainbow(100, FORWARD);
//clearStrip(100, REVERSE);
//fillStrip(strip.Color(255,0,0), 100, FORWARD); // color = GRB!
//fillStrip(strip.Color(0,255,0), 100, FORWARD); // color = GRB
//fillStrip(strip.Color(0,0,255), 100, FORWARD); // color = GRB

// AABBDD Dir(1) Wait(2)
 struct data parseCommand(String command) {
 struct data parsedData;
 parsedData.color = command.substring(1,7);
 String p = command.substring(0,1);
 parsedData.dir = p.toInt();
 p = command.substring(7,9);
 parsedData.wait = p.toInt();
 parsedData.func = command.substring(9).toInt();
 long tmpColor = strtol( &("#" + parsedData.color)[1], NULL, 16);
 parsedData.g = tmpColor >> 8 & 0xFF; //tmpColor >> 16;
 parsedData.r = tmpColor >> 16; //tmpColor >> 8 & 0xFF;
 parsedData.b = tmpColor & 0xFF;
 return parsedData;
}


int setStripColor(String command) {
 Serial.println("Color strip function...");
 struct data value = parseCommand(command);
 debugData(value);
 fillStrip(strip.Color(value.g,value.r,value.b), value.wait, value.dir);
 return 1;
 }
 int setClearStrip(String command) {
 Serial.println("Clear strip function...");
 struct data value = parseCommand(command);
 debugData(value);
 clearStrip(value.wait, value.dir);
 return 1;
 }
 int setRainbow(String command) {
 Serial.println("Rainbow strip function...");
 struct data value = parseCommand(command);
 debugData(value);
 rainbow(value.wait, value.dir);
 return 1;
 }
 void debugData(struct data value) {
 Serial.println("=========================");
 Serial.println("Color ["+value.color+"]");
 Serial.println("Direction ["+String(value.dir)+"]");
 Serial.println("Wait ["+String(value.wait)+"]");
 Serial.println("Func ["+String(value.func)+"]");
 Serial.println("R ["+String(value.r)+"]");
 Serial.println("G ["+String(value.g)+"]");
 Serial.println("B ["+String(value.b)+"]");
 Serial.println("=========================");
 }
 void printWifiStatus()
 {
 // print the SSID of the network you're attached to
 Serial.print("SSID: ");
 Serial.println(WiFi.SSID());
 // print your WiFi shield's IP address
 IPAddress ip = WiFi.localIP();
 Serial.print("IP Address: ");
 Serial.println(ip);
 // print where to go in the browser
 Serial.println();
 Serial.print("To see this page in action, open a browser to http://");
 Serial.println(ip);
 Serial.println();
 }
