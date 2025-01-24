http://arduino.esp8266.com/stable/package_esp8266com_index.json

https://github.com/RamNishanth/esp01

Below is **one possible** example showing how to serve a simple web page on an ESP-01 (using `WiFiEspAT` on an Arduino Due) and control an 8-pixel WS2812B strip with three commands:

1. **`/fill?params=...`** – Fill the strip with a color, optionally animating from one end to the other.  
2. **`/clear`** – Turn off all pixels.  
3. **`/rainbow`** – Cycle through a rainbow effect a set number of times.

You can adapt this code to fit your exact parameter format and animation requirements.

---

## 1) Hardware and Library Setup

1. **Hardware Connections**  
   - **Arduino Due** → **ESP-01**  
     - `3.3V` → `VCC` & `CH_PD`  
     - `GND` → `GND`  
     - `TX1 (Pin 18)` → `RX` on ESP-01  
     - `RX1 (Pin 19)` → `TX` on ESP-01  
   - **Arduino Due** → **WS2812B strip**  
     - Use a digital pin (e.g., **Pin 6** for data).  
     - Power the strip with a **5V** or **3.3V** supply (depending on your LEDs), but make sure to **use a level shifter or a 330–470 Ω resistor** on the data line if powering the strip at 5V.  
     - Common ground between Arduino and strip.

2. **Libraries**  
   Make sure you have installed:  
   - [**WiFiEspAT** library](https://github.com/jandrassy/WiFiEspAT)  
   - [**Adafruit NeoPixel** library](https://github.com/adafruit/Adafruit_NeoPixel)

3. **ESP-01 Firmware**  
   - The ESP-01 must have **AT firmware compatible** with the `WiFiEspAT` library.  
   - Baud rate set to **115200** (or whichever rate you choose in `Serial1.begin(...)`).

---

## 2) Sketch Overview

- **Wi-Fi Setup**: Connect to the Wi-Fi network (`Galaxy S10`) and start an HTTP server on port **80**.  
- **Web Server**: On each request:
  - Parse the requested URL (`/fill`, `/clear`, `/rainbow`).
  - Extract any parameters if provided (e.g., `/fill?params=100FF00109`).
  - Call the matching LED function.
  - Send back a simple HTML response.

- **LED Functions**:
  1. **`clearStrip()`**: Turns off all pixels.
  2. **`fillStrip(...)`**: Fills the strip with color, optionally animating in a direction with a certain delay.
  3. **`rainbow(...)`**: Displays a rainbow animation a set number of times.

### Parameter Format Example
For the **`/fill?params=100FF00109`** example, you might parse this string as follows:

```
"1"         -> direction (0 or 1)
"00FF00"    -> color in hex (R=00, G=FF, B=00)
"10"        -> delay in ms
"9"         -> number of cycles (optional)
```

Feel free to modify this format to suit your needs.

---

## 3) Complete Example Code

```cpp
/***************************************************
  Example: Arduino Due + ESP-01 (WiFiEspAT library)
  Controlling WS2812B strip with HTTP commands:
    - /clear
    - /fill?params=100FF00109
    - /rainbow?params=11050  (as an example)
***************************************************/

// ========== LIBRARIES ==========
#include <WiFiEspAT.h>
#include <Adafruit_NeoPixel.h>

// ========== WIFI CREDENTIALS ==========
char ssid[] = "Galaxy S10";      // Your network SSID
char pass[] = "123456789";       // Your network password
volatile bool stopRainbow = false;

// ========== WS2812B SETTINGS ==========
#define LED_PIN     5      // Digital pin on Arduino Due connected to the NeoPixel data line
#define LED_COUNT   8      // Number of NeoPixels in the strip
Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

// ========== WEB SERVER ==========
WiFiServer server(80);

// ========== SETUP FUNCTION ==========
void setup() {
  // Initialize serial for debug output
  Serial.begin(115200);
  while (!Serial) { ; }  // Wait for Serial port to be ready (especially on Due)

  // Initialize the NeoPixel strip
  strip.begin();      // Initialize all pixels
  strip.show();       // Turn OFF all pixels ASAP
  strip.setBrightness(50); // Adjust brightness 0-255 as needed

  // Initialize Serial1 for ESP-01 communication
  Serial1.begin(115200);
  WiFi.init(Serial1);

  // Connect to WiFi
  Serial.println("Connecting to Wi-Fi...");
  if (WiFi.begin(ssid, pass)) {
    Serial.println("Connected to Wi-Fi!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("Failed to connect to Wi-Fi.");
    while (true);  // Halt if no connection
  }

  // Start the web server
  server.begin();
  Serial.println("Web server started! You can connect now.");
}

// ========== MAIN LOOP ==========
void loop() {
  // Reconnect if Wi-Fi drops
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi disconnected. Reconnecting...");
    WiFi.begin(ssid, pass);
    while (WiFi.status() != WL_CONNECTED) {
      delay(1000);
      Serial.print(".");
    }
    Serial.println("\nReconnected to Wi-Fi.");
  }

  // Check for a new client
  WiFiClient client = server.available();
  if (!client) return; // No new client, do nothing

  // Wait for data from the client
  Serial.println("New client connected");
  while (!client.available()) {
    delay(1);
  }

  // Read the first line of the request
  String request = client.readStringUntil('\r');
  Serial.println(request);
  client.flush();  // Clear the buffer

  // ========== PARSE THE REQUEST ==========
  // Example requests:
  //   GET /clear
  //   GET /fill?params=100FF00109
  //   GET /rainbow?params=11050
  // We'll look for substrings in 'request'

  if (request.indexOf("GET /clear") != -1) {
    clearStrip();

  } else if (request.indexOf("GET /fill?params=") != -1) {
    // Extract the parameter substring after "?params="
    String params = extractParams(request, "fill");
    if (params.length() > 0) {
      // Example: "100FF00109"
      //  index 0: direction ('0' or '1')
      //  index 1..6: color in hex ("00FF00")
      //  index 7..8: wait in ms (two digits, e.g. "10" -> 10 ms)
      //  index 9..: (optional) iteration or something else
      byte direction = (byte)(params[0] - '0');
      String colorStr = params.substring(1, 7); // 6 hex digits
      String waitStr  = params.substring(7, 9); // 2 digits

      // Convert color from hex string to 32-bit
      uint32_t color = (uint32_t) strtol(colorStr.c_str(), NULL, 16);
      // Convert wait time to integer
      int waitTime = waitStr.toInt();
      // Optional cycles (if your string includes it)
      byte cycles = 1; // default
      if (params.length() >= 10) {
        String cycleStr = params.substring(9); // from index 9 to end
        cycles = cycleStr.toInt();
      }

      fillStrip(direction, color, waitTime, cycles);
    }

  } else if (request.indexOf("GET /rainbow?params=") != -1) {
    // Extract the parameter substring after "?params="
    String params = extractParams(request, "rainbow");
    if (params.length() > 0) {
      // Example: "11050"
      //  index 0: direction
      //  index 1: cycles or something
      //  index 2..: wait in ms
      byte direction = (byte)(params[0] - '0');
      byte cycles    = (byte)(params[1] - '0');
      int waitTime   = params.substring(2).toInt();

      rainbow(direction, waitTime, cycles);
    } else {
      // If no params given, just show a default rainbow
      rainbow(0, 50, 1);
    }

  } else {
    // No recognized command, do nothing or handle differently
  }

  // ========== SEND HTTP RESPONSE ==========
  // You can create a dynamic response if desired
  client.print(
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: text/html\r\n"
    "Connection: close\r\n"
    "\r\n"
    "<!DOCTYPE HTML>\r\n"
    "<html>"
      "<h2>LED Controller</h2>"
      "<p>Try <a href=\"/clear\">/clear</a>, "
      "<a href=\"/fill?params=100FF00109\">/fill?params=100FF00109</a>, "
      "<a href=\"/rainbow?params=11050\">/rainbow?params=11050</a></p>"
    "</html>"
  );

  delay(1);        // Short delay
  client.stop();   // Disconnect
  Serial.println("Client disconnected");
}

// ========== HELPER: EXTRACT PARAMS FROM REQUEST ==========
String extractParams(const String &request, const String &cmd) {
  // Typically the request line is "GET /fill?params=100FF00109 HTTP/1.1"
  // We want what's after "?params="
  // e.g., "100FF00109"

  String match = cmd + "?params="; // e.g., "fill?params="
  int startIndex = request.indexOf(match);
  if (startIndex == -1) return "";
  startIndex += match.length();  // move index to after "?params="
  
  // Find the space or " " after the params
  int endIndex = request.indexOf(' ', startIndex);
  if (endIndex == -1) {
    // fallback if not found
    endIndex = request.length();
  }

  // Extract substring
  String result = request.substring(startIndex, endIndex);
  result.trim();
  return result;
}

// ========== LED FUNCTIONS ==========

// Turn off all pixels
void clearStrip() {
  for (int i = 0; i < LED_COUNT; i++) {
    strip.setPixelColor(i, 0);
  }
  strip.show();
}

// Fill the strip with color, possibly animating in a direction
// direction: 0 -> forward, 1 -> backward
// color: 0xRRGGBB
// waitTime: delay (ms) between lighting up each pixel
// cycles: how many times to repeat
void fillStrip(byte direction, uint32_t color, int waitTime, byte cycles) {
  for (byte c = 0; c < cycles; c++) {
    if (direction == 0) {
      // Forward fill
      for (int i = 0; i < LED_COUNT; i++) {
        strip.setPixelColor(i, color);
        strip.show();
        delay(waitTime);
      }
    } else {
      // Backward fill
      for (int i = LED_COUNT - 1; i >= 0; i--) {
        strip.setPixelColor(i, color);
        strip.show();
        delay(waitTime);
      }
    }
  }
}

// Display a rainbow effect on the strip
// direction: 0 -> forward, 1 -> backward
// waitTime: delay (ms) between frames
// cycles: how many times to cycle the rainbow
void rainbow(byte direction, int waitTime, byte cycles) {
  stopRainbow = false;  // reset any previous stop

  for (byte c = 0; c < cycles; c++) {
    for (int pos = 0; pos < 256; pos++) {
      // Check if we must stop
      if (stopRainbow) {
        return;
      }

      // Optionally check for new clients
      WiFiClient client = server.available();
      if (client) {
        // If you want to handle the request right here:
        String request = client.readStringUntil('\r');
        client.flush();

        if (request.indexOf("GET /clear") != -1) {
          stopRainbow = true;      // set flag
          clearStrip();           // immediate effect
          return;                 // break out
        }
        // else parse other requests similarly...

        // Send response, etc.
        client.stop();
      }

      // Now do the step for 'pos'
      for (int i = 0; i < LED_COUNT; i++) {
        int colorIndex = (direction == 0) ? (i + pos) & 255 : (i - pos) & 255;
        strip.setPixelColor(i, wheel(colorIndex));
      }
      strip.show();
      delay(waitTime);
    }
  }
}

// Helper function to produce color from a 'wheel' position
uint32_t wheel(byte wheelPos) {
  wheelPos = 255 - wheelPos;
  if(wheelPos < 85) {
    return strip.Color(255 - wheelPos * 3, 0, wheelPos * 3);
  }
  if(wheelPos < 170) {
    wheelPos -= 85;
    return strip.Color(0, wheelPos * 3, 255 - wheelPos * 3);
  }
  wheelPos -= 170;
  return strip.Color(wheelPos * 3, 255 - wheelPos * 3, 0);
}
```

---

### How the Code Works

1. **Setup**:
   - Initializes the **WS2812B** strip (using **Adafruit_NeoPixel**).
   - Sets up the **ESP-01** connection using `WiFiEspAT` on `Serial1`.
   - Connects to the configured Wi-Fi network (`Galaxy S10`).
   - Starts an HTTP server on port **80**.

2. **Loop**:
   - Monitors Wi-Fi connection status. Reconnects automatically if dropped.
   - Waits for an incoming client request (e.g., from a browser).
   - Parses the request line to determine which command was called:
     - **`/clear`**  
       → Calls `clearStrip()`.
     - **`/fill?params=...`**  
       → Parses the parameter string, extracts **direction**, **color**, **waitTime**, and **cycles**, then calls `fillStrip()`.
     - **`/rainbow?params=...`**  
       → Parses the parameter string, extracts **direction**, **waitTime**, and **cycles**, then calls `rainbow()`.
   - Returns a simple **HTML** response.

3. **HTTP Request & Parameter Parsing**:
   - The function `extractParams()` looks for `GET /fill?params=` (or `rainbow?params=`) within the request and pulls out the substring after `?params=`.
   - Example:
     - `GET /fill?params=100FF00109 HTTP/1.1`
     - Parameter substring is `100FF00109`
       - `1` → direction  
       - `00FF00` → color in hex  
       - `10` → wait time (10 ms)  
       - `9` → cycles  

4. **LED Functions**:
   - **`clearStrip()`**: Turns off every pixel.  
   - **`fillStrip(direction, color, wait, cycles)`**: Sequentially lights pixels from one end or the other.  
   - **`rainbow(direction, wait, cycles)`**: Displays a rainbow animation by cycling through color positions.

---

## 4) Usage Examples

1. **Clear the Strip**  
   - Open a browser and go to:  
     ```
     http://<your_esp_ip_address>/clear
     ```
   - All LEDs turn off.

2. **Fill the Strip**  
   - Example:  
     ```
     http://<your_esp_ip_address>/fill?params=100FF00109
     ```
   - Breakdown:  
     - `direction` = `1` → fill backwards.  
     - `color` = `00FF00` → bright green.  
     - `waitTime` = `10` ms between lighting each LED.  
     - `cycles` = `9` → do this fill animation 9 times.

3. **Rainbow**  
   - Example:  
     ```
     http://<your_esp_ip_address>/rainbow?params=11050
     ```
   - Breakdown:  
     - `direction` = `1` (reverse).  
     - `cycles` = `1`.  
     - `waitTime` = `050` → 50 ms (leading zero not required).  

---

### Tips and Notes

- **Power**: Ensure your WS2812B strip is powered adequately. A single WS2812B LED can draw up to 60 mA at full brightness white. Even an 8-LED strip can draw ~480 mA when fully lit white.  
- **Level shifting** (Data Line): When powering the strip at 5V, you usually need a 3.3V → 5V level shifter or at least a series resistor to avoid damaging the first LED.  
- **Parameter Parsing**: Adjust the parsing logic if your parameter format changes.  
- **Security**: This is a simple open HTTP server. For production or public networks, consider authentication or encryption.  

With this example, you can open a browser on any device connected to the same Wi-Fi network, visit the ESP-01’s IP address, and send commands to control your WS2812B strip in real time!