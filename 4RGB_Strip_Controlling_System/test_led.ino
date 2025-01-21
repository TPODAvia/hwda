#include <Adafruit_NeoPixel.h>

#define PIN 5             // Pin connected to the NeoPixel strip
#define LED_NUMBER 16     // Number of LEDs in the strip
#define FORWARD 1         // Direction forward
#define REVERSE 2         // Direction reverse

// Initialize the NeoPixel strip
Adafruit_NeoPixel strip = Adafruit_NeoPixel(LED_NUMBER, PIN, NEO_RGB + NEO_KHZ800);

// Setup function to run once
void setup() {
  Serial.begin(115200);
  Serial.println("Arduino Strip RGB LED Initialized");
  strip.begin();
  strip.show(); // Initialize all pixels to 'off'
}

// Main loop function
void loop() {
  clearStrip(100, REVERSE);                      // Clear the strip in reverse direction
  rainbow(100, FORWARD);                         // Display rainbow colors in forward direction
  clearStrip(100, REVERSE);                      // Clear the strip in reverse direction
  fillStrip(strip.Color(255, 0, 0), 100, FORWARD); // Fill strip with red
  fillStrip(strip.Color(0, 255, 0), 100, FORWARD); // Fill strip with green
  fillStrip(strip.Color(0, 0, 255), 100, FORWARD); // Fill strip with blue
}

// Function to display a rainbow effect
void rainbow(int wait, int direction) {
  int first, last;
  setDirection(&first, &last, direction);

  byte color[3];
  byte count = 0;

  for (int i = 0; i < 10; i++) {
    color[count] = random(256); // Random base color
    byte a0 = count + random(1) + 1;
    color[a0 % 3] = random(256 - color[count]);
    color[(a0 + 1) % 3] = 255 - color[a0 % 3] - color[count];
    count = (count + random(15)) % 3; // Avoid repeating patterns

    fillStrip(strip.Color(color[0], color[1], color[2]), wait, direction);

    if (direction == FORWARD) {
      clearStrip(wait, REVERSE);
    } else {
      clearStrip(wait, FORWARD);
    }
  }
}

// Function to fill the strip with a specified color
void fillStrip(uint32_t color, int wait, int direction) {
  int first, last;
  setDirection(&first, &last, direction);

  for (int p = first; p <= last; p++) {
    strip.setPixelColor(abs(p), color);
    strip.show();
    delay(wait);
  }
}

// Function to clear the strip (turn off all LEDs)
void clearStrip(int wait, int direction) {
  int first, last;
  setDirection(&first, &last, direction);

  for (int p = first; p <= last; p++) {
    strip.setPixelColor(abs(p), 0);
    strip.show();
    delay(wait);
  }
}

// Function to set the direction (FORWARD or REVERSE) for the LED operations
void setDirection(int *first, int *last, int direction) {
  if (direction == FORWARD) {
    *first = 0;
    *last = LED_NUMBER - 1;
  } else {
    *first = -LED_NUMBER + 1;
    *last = 0;
  }
}
