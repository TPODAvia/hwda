#include <Adafruit_NeoPixel.h>
#define PIN 5
#define LED_NUMBER 16 //number of LEDs in the LED strip; can be 8!
#define FORWARD 1
#define REVERSE 2
 struct data {
 String color;
 int wait;
 int dir;
 int func;
 int r;
 int g;
 int b;
 } ;
 Adafruit_NeoPixel strip = Adafruit_NeoPixel(LED_NUMBER, PIN,
NEO_RGB+NEO_KHZ800);
//check for more settings at github.com/adafruit/Adafruit_NeoPixel
 void setup() {
 // put your setup code here, to run once:
 Serial.begin(115200);
 Serial.println("Arduino Strip RGB Led");
 strip.begin();
 }
 void loop() {
 // put your main code here, to run repeatedly:
 clearStrip(100, REVERSE);
 rainbow(100, FORWARD);
 clearStrip(100, REVERSE);
 fillStrip(strip.Color(255,0,0), 100, FORWARD); // color = GRB!
 fillStrip(strip.Color(0,255,0), 100, FORWARD); // color = GRB
 fillStrip(strip.Color(0,0,255), 100, FORWARD); // color = GRB
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
 fillStrip(strip.Color(color[0], color[1], color[2]), wait, direction);
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