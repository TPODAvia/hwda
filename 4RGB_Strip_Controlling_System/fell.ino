#include <Ethernet.h>
#include "aREST.h"
#include <Adafruit_NeoPixel.h>
#define PIN 5
#define LED_NUMBER 16 //number of LEDs in the LED strip; can be 8!
#define FORWARD 1
#define REVERSE 2
#define ESP_BAUDRATE 9600
 EthernetServer server(80);
 byte mac[] = { 0xDD, 0xAB, 0xCE, 0xFF, 0xEE, 0xED }; // your Arduino with
Ethernet Shield mac address
 IPAddress ip(192,168,1,7); //your IP address for Arduino
 struct data {
 String color;
 int wait;
 int dir;
 int func;
 int r;
 int g;
 int b;
 } ;
 aREST rest = aREST();
 Adafruit_NeoPixel strip = Adafruit_NeoPixel(LED_NUMBER, PIN,
NEO_RGB+NEO_KHZ800);
//check for more settings at github.com/adafruit/Adafruit_NeoPixel
void setup() {
 // put your setup code here, to run once:
 Serial.begin(ESP_BAUDRATE);
 Serial.println("Arduino Strip RGB Led");
 strip.begin();
 // Give name and ID to device (ID should be 6 characters long)
 //rest.set_id("002");
 //rest.set_name("my_1st_arest_device");
 if (Ethernet.begin(mac) == 0) {
 Serial.println("Failed to configure Ethernet using DHCP");
 Ethernet.begin(mac, ip);
 }
 Serial.println("You're connected to the network");
 printNetStatus();
 server.begin();
 rest.function("fill", setStripColor);
 rest.function("clear", setClearStrip);
 rest.function("rainbow", setRainbow);
 }
 void loop() {
 // put your main code here, to run repeatedly:
 EthernetClient client = server.available();
 rest.handle(client);
 //clearStrip(100, REVERSE);
 //rainbow(100, FORWARD);
 //fillStrip(strip.Color(255,0,0), 100, FORWARD); // color = GRB
 //fillStrip(strip.Color(0,255,0), 100, FORWARD); // color = GRB
 //fillStrip(strip.Color(0,0,255), 100, FORWARD); // color = GRB
 }
 void rainbow(int wait, int direction) {
 int first, last;
 setDirection(&first, &last, direction);
 byte color[3];
 byte count, a0, a1, a2;
 for (int i=0;i<10;i++) {
 color[count]=random(256);
 a0=count+random(1)+1;
 color[a0%3]=random(256-color[count]);
 color[(a0+1)%3]=255-color[a0%3]-color[count];
 count+=random(15); // to avoid repeating patterns
 count%=3;
 fillStrip(strip.Color(color[0], color[1], color[2]), wait,
direction);
 if (direction == FORWARD) clearStrip(wait, REVERSE);
 else clearStrip(wait, FORWARD);
 }
 }
 void fillStrip(uint32_t color, int wait, int direction) {
 int first, last;
 setDirection(&first, &last, direction);
 for (int p=first; p<=last; p++) {
strip.setPixelColor(abs(p),color);
 strip.show();
 delay(wait);
 }
 }
 void clearStrip(int wait, int direction) {
 int first, last;
 setDirection(&first, &last, direction);
 for (int p=first; p<=last; p++) {
 strip.setPixelColor(abs(p),0);
 strip.show();
 delay(wait);
 }
 }
 void setDirection(int *first, int *last,int direction) {
 if (direction == FORWARD) {
 *first = 0;
 *last = LED_NUMBER;
 }
 else {
 *first = -LED_NUMBER;
 *last = 0;
 }
 }
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
 // Function exposed
 int setStripColor(String command) {
 Serial.println("Color strip function...");
 struct data value = parseCommand(command);
 debugData(value);
 fillStrip(strip.Color(value.g,value.r,value.b), value.wait,
value.dir);
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
 void printNetStatus()
 {
 // print your WiFi shield's IP address
 IPAddress ip = Ethernet.localIP();
 Serial.print("IP Address: ");
 Serial.println(ip);
 // print where to go in the browser
 Serial.println();
 Serial.print("To see this page in action, open a browser to http://");
 Serial.println(ip);
 Serial.println();
 }
