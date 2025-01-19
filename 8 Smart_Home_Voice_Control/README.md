How to pair real phone: https://www.youtube.com/watch?v=1cKPbAGzVNQ&ab_channel=CodexCreator

 python3 raspi8_dummy.py

Below is a detailed, step-by-step guide to creating the “Smart Home Voice Control” project. It covers both the Android application development in Android Studio (with voice recognition and TTS) and the Raspberry Pi server application (with the BME280/BMP280 sensor and an LED strip). You can follow these steps in order.

---

## 1. Project Overview

**What we’re building:**

- **Mobile app** (Android smartphone) that:
  - Uses **speech recognition** to understand voice commands.
  - Makes HTTP requests to a **server** running on the Raspberry Pi.
  - Receives sensor data (temperature, humidity, pressure) from the Pi.
  - Controls an LED strip’s color (or turns it off) on the Raspberry Pi.
  - Uses **speech synthesis (TTS)** to speak back the results of your requests.

- **Server** on Raspberry Pi that:
  - Reads data from a BME280 (or BMP280) sensor.
  - Listens for GET requests on a specified port.
  - Sets the LED strip color based on GET requests.
  - Returns sensor data or a “weather forecast” in its HTTP response.

**Important note:**  
- You will need a real Android device to test speech recognition (emulators often do not handle voice input well).  
- GPIO18 (physical pin 12) on the Raspberry Pi is typically used for driving a WS2812B LED strip (neopixel), and it often requires disabling the onboard audio.  
- You need root access on Raspberry Pi to run the LED strip library properly.

---

## 2. Hardware and Connection Diagram

### 2.1 Required Components

1. **Raspberry Pi 3 or 4** (with SD card, Raspberry Pi OS installed).  
2. **BME280 or BMP280 sensor** (I2C).  
3. **WS2812B LED strip** (12 LEDs in the example, but you can use any number).  
4. **Breadboard** and **jumper wires**.  
5. **5V power supply** for Raspberry Pi (and for LED strip if needed).  
6. **HDMI monitor and cable** (to configure your Pi if you’re using a monitor).  
7. **Android smartphone** (for the client app).  

### 2.2 Wiring

1. **BME280/BMP280**:
   - Connect **VCC** to 3.3V on Raspberry Pi.
   - Connect **GND** to GND on Raspberry Pi.
   - Connect **SCL** to SCL on Raspberry Pi (GPIO3, Physical Pin 5).
   - Connect **SDA** to SDA on Raspberry Pi (GPIO2, Physical Pin 3).

2. **LED strip (WS2812B)**:
   - **5V** pin of LED strip to 5V power supply (Pi’s 5V if using the same supply).
   - **GND** of LED strip to Raspberry Pi GND.
   - **DIN** (data in) of LED strip to **GPIO18** (Physical pin 12) on Raspberry Pi.  
   - Make sure you have a common ground between the LED strip and the Pi.

*(Refer to Figure 162 in the original text for a visual diagram.)*

---

## 3. Preparing the Raspberry Pi

> **Note:** You will likely need to do these steps **as root** on the Pi if you want to run the LED strip code successfully.

### 3.1 Enable `root` Login (if not yet done)

1. Open a terminal on Raspberry Pi.  
2. Set a password for root:  
   ```bash
   sudo passwd root
   ```  
3. Log out from the default user, then log in again as root (username: `root`, password you just set).  

### 3.2 Install Required Libraries

Once logged in as root, in a terminal:

1. **LED strip libraries**:
   ```bash
   sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel
   ```
2. **BME280 / BMP280 libraries**:
   ```bash
   pip install RPi.bme280
   pip install smbus2
   ```
   (You may use `pip3` if you prefer Python 3 environment; verify which version Thonny and your script are using.)

### 3.3 Disable Audio on GPIO18

1. Open the file `/boot/config.txt` (as root) in a text editor:
   ```bash
   nano /boot/config.txt
   ```
2. Find the line:
   ```
   dtparam=audio=on
   ```
   Change it to:
   ```
   dtparam=audio=off
   ```
3. Save and exit (`Ctrl + O`, `Enter`, then `Ctrl + X`).  
4. **Reboot** the Pi to apply changes:
   ```bash
   reboot
   ```
5. Log in again as root.

### 3.4 Create the Server Script

1. Launch Thonny (Menu → Programming → Thonny).  
2. Create a new file (File → New).  
3. Paste in the server code (shown below).
4. Modify **server_address** to use your Pi’s IP address and a port (e.g. `('192.168.x.y', 8000)`).
5. Save the file (e.g. `smart_home_server.py`) somewhere under the root user’s home folder.

**Example server code** (`smart_home_server.py`):

```python
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from io import BytesIO
import smbus2
import bme280
import neopixel
import board
import random

port = 1
address = 0x76  # BME280 or BMP280 I2C address
bus = smbus2.SMBus(port)
calibration_params = bme280.load_calibration_params(bus, address)

# Pressure thresholds for a simple "weather forecast"
lvl1 = 1022.69  # Pa
lvl2 = 1009.14  # Pa

num_pixels = 12  # Number of LEDs in the strip
pixel_pin = board.D18  # GPIO18
ORDER = neopixel.GRB
pixels = neopixel.NeoPixel(pixel_pin, num_pixels,
                           brightness=0.1,
                           auto_write=False,
                           pixel_order=ORDER)

def lightsOn(color):
    global pixels
    if color == "random":
        r = random.randrange(256)
        g = random.randrange(256)
        b = random.randrange(256)
    else:
        # color is a hex string like 'FF0000'
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
    pixels.fill((r, g, b))
    pixels.show()

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        body = self.path  # e.g. '/temperature', '/FF0000', etc.
        print("Request path:", body)

        if 'temperature' in body:
            data = bme280.sample(bus, address, calibration_params)
            body = str(round(data.temperature))
        elif 'pressure' in body:
            data = bme280.sample(bus, address, calibration_params)
            # Convert hPa to mmHg -> 1hPa ~ 1.33322 mmHg
            body = str(round(data.pressure / 1.33322387415))
        elif 'humidity' in body:
            data = bme280.sample(bus, address, calibration_params)
            body = str(round(data.humidity))
        elif 'weather' in body:
            data = bme280.sample(bus, address, calibration_params)
            if data.pressure >= lvl1:
                weather_forecast = 'the weather will be stable'
            elif data.pressure >= lvl2 and data.pressure < lvl1:
                weather_forecast = 'the weather will be cloudy'
            else:
                weather_forecast = 'the weather will be rainy'
            body = weather_forecast

        # LED strip color patterns
        if 'FF0000' in body:
            lightsOn('FF0000')
        elif '00FF00' in body:
            lightsOn('00FF00')
        elif '0000FF' in body:
            lightsOn('0000FF')
        elif 'FFFF00' in body:
            lightsOn('FFFF00')
        elif 'FF00FF' in body:
            lightsOn('FF00FF')
        elif 'FFFFFF' in body:
            lightsOn('FFFFFF')
        elif '000000' in body:
            lightsOn('000000')
        elif 'random' in body:
            lightsOn('random')

        response = BytesIO()
        response.write(bytes(body, "utf-8"))
        self.wfile.write(response.getvalue())
        print("Response:", response.getvalue())

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler):
    server_address = ('192.168.x.y', 8000)  # <--- Change IP and port
    httpd = server_class(server_address, handler_class)
    try:
        print("Server running at http://192.168.x.y:8000/ ...")
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()

run()
```

### 3.5 Run the Server

1. In Thonny, click **Run** (green “play” icon) or press `F5`.  
2. If everything is correct, it should show a message similar to:
   ```
   Server running at http://192.168.x.y:8000/ ...
   ```
3. Keep this window open (the server must be running in order to receive requests).

---

## 4. Building the Android App in Android Studio

### 4.1 Create a New Project

1. Open Android Studio (Electric Eel / Flamingo / latest).  
2. **Create New Project** → **Empty Activity** (or Empty Views Activity).  
3. **Language**: Java.  
4. Check your **minimum SDK** and **target SDK** – match them to your phone if needed (e.g., API 33).

### 4.2 Set Up the Layout

1. Open `app/src/main/res/layout/activity_main.xml`.  
2. Replace its contents with something like:

```xml
<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    tools:context=".MainActivity">

    <Button
        android:id="@+id/button"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="talk"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>
```

*(Only one Button in the center of the screen labeled “talk”.)*

### 4.3 Update `AndroidManifest.xml`

Open `app/src/main/AndroidManifest.xml` and **add**:

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

Also, inside the `<application>` tag, enable cleartext traffic (if your Pi server uses `http` and not `https`):

```xml
<application
    ...
    android:usesCleartextTraffic="true"
    ... >
    ...
</application>
```

### 4.4 Add OkHttp to `build.gradle` (Module level)

In `dependencies`:

```groovy
implementation 'com.squareup.okhttp3:okhttp:3.6.0'
```

Then **sync** the project.

### 4.5 MainActivity Code

Open `MainActivity.java`. Below is a **combined** snippet; you can adapt it to your project. Remember to import all necessary classes (e.g., `OkHttpClient`, `Request`, `Callback`, `SpeechRecognizer`, `TextToSpeech`, etc.).

**Full example**:

```java
package com.example.smarthomevoice;

import androidx.appcompat.app.AppCompatActivity;
import android.content.Intent;
import android.os.Bundle;
import android.speech.RecognizerIntent;
import android.speech.tts.TextToSpeech;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.Toast;

import com.squareup.okhttp.Call;
import com.squareup.okhttp.Callback;
import com.squareup.okhttp.OkHttpClient;
import com.squareup.okhttp.Request;
import com.squareup.okhttp.Response;

import java.io.IOException;
import java.util.List;
import java.util.Locale;

import static java.lang.Thread.sleep;

public class MainActivity extends AppCompatActivity {

    private TextToSpeech TTS;
    boolean ttsEnabled;
    private OkHttpClient client;
    private static final String baseUrl = "http://192.168.x.y:8000/"; // Pi server IP & port
    String request2raspberry;
    String responsefromraspberry;

    Button button;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        button = findViewById(R.id.button);

        // Initialize OkHttp client
        client = new OkHttpClient();

        // Initialize TTS
        TTS = new TextToSpeech(this, new TextToSpeech.OnInitListener() {
            @Override
            public void onInit(int initStatus) {
                if (initStatus == TextToSpeech.SUCCESS) {
                    TTS.setLanguage(Locale.US);
                    TTS.setPitch(1.3f);
                    TTS.setSpeechRate(0.7f);
                    ttsEnabled = true;
                } else {
                    Toast.makeText(MainActivity.this,
                            "TTS initialization failed", Toast.LENGTH_LONG).show();
                    ttsEnabled = false;
                }
            }
        });

        // Button click: start speech recognition
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
                intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                        RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
                intent.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1);
                intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.ENGLISH);
                intent.putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_MINIMUM_LENGTH_MILLIS,
                        3000L);
                startActivityForResult(intent, 1);
            }
        });
    }

    // Handle results from voice recognition
    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == 1 && resultCode == RESULT_OK) {
            List<String> results = data.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS);
            String spokenText = results.get(0).toLowerCase();
            Toast.makeText(MainActivity.this, spokenText, Toast.LENGTH_LONG).show();

            // Check for sensor data queries
            if (spokenText.contains("temperature")) {
                sendRequest("temperature");
                delay(1);
            }
            if (spokenText.contains("pressure")) {
                sendRequest("pressure");
                delay(1);
            }
            if (spokenText.contains("humidity")) {
                sendRequest("humidity");
                delay(1);
            }
            if (spokenText.contains("sensor data")) {
                sendRequest("temperature");
                delay(1);
                sendRequest("pressure");
                delay(1);
                sendRequest("humidity");
                delay(1);
            }
            if (spokenText.contains("weather")) {
                sendRequest("weather");
                delay(1);
            }

            // Check for light control
            if (spokenText.contains("light")) {
                if (spokenText.contains("switch on") || spokenText.contains("turn on")
                        || spokenText.contains("on")) {
                    // specific color?
                    if (spokenText.contains("color")) {
                        if (spokenText.contains("red")) {
                            setColor("FF0000");
                        } else if (spokenText.contains("green")) {
                            setColor("00FF00");
                        } else if (spokenText.contains("blue")) {
                            setColor("0000FF");
                        } else if (spokenText.contains("yellow")) {
                            setColor("FFFF00");
                        } else if (spokenText.contains("purple")) {
                            setColor("FF00FF");
                        } else if (spokenText.contains("random")) {
                            setColor("random");
                        } else {
                            setColor("FFFFFF");
                        }
                    } else {
                        setColor("FFFFFF"); // default white
                    }
                }
                if (spokenText.contains("switch off") || spokenText.contains("turn off")
                        || spokenText.contains("off")) {
                    setColor("000000");
                }
            }
        }
        super.onActivityResult(requestCode, resultCode, data);
    }

    // Send a request for sensor data
    private void sendRequest(String request) {
        Toast.makeText(MainActivity.this, request, Toast.LENGTH_LONG).show();
        if (!ttsEnabled) return;

        String utteranceId = this.hashCode() + "";
        String url = baseUrl;
        request2raspberry = request;

        Request req1 = new Request.Builder()
                .url(url + request)
                .build();

        client.newCall(req1).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                TTS.speak("There was an error: " + e.toString(),
                        TextToSpeech.QUEUE_ADD, null, utteranceId);
                Log.e("sendRequest", "Error", e);
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                responsefromraspberry = response.body().string();
                switch (request2raspberry) {
                    case "temperature":
                        TTS.speak("Current temperature is " + responsefromraspberry
                                + " degrees of Celsius",
                                TextToSpeech.QUEUE_ADD, null, utteranceId);
                        break;
                    case "pressure":
                        TTS.speak("Current pressure is " + responsefromraspberry
                                + " millimeters of mercury",
                                TextToSpeech.QUEUE_ADD, null, utteranceId);
                        break;
                    case "humidity":
                        TTS.speak("Current humidity is " + responsefromraspberry
                                + " percent",
                                TextToSpeech.QUEUE_ADD, null, utteranceId);
                        break;
                    case "weather":
                        TTS.speak("Current weather forecast is: "
                                + responsefromraspberry,
                                TextToSpeech.QUEUE_ADD, null, utteranceId);
                        break;
                }
                Log.i("sendRequest", "Response: " + responsefromraspberry);
            }
        });
    }

    // Send a request to set the LED color
    private void setColor(String color) {
        Toast.makeText(MainActivity.this, color, Toast.LENGTH_LONG).show();
        String utteranceId = this.hashCode() + "";
        String url = baseUrl;
        String LEDstripcolor = color;

        Request req1 = new Request.Builder()
                .url(url + color)  // e.g. "http://192.168.x.y:8000/FF0000"
                .build();

        client.newCall(req1).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                TTS.speak("There was an error: " + e.toString(),
                        TextToSpeech.QUEUE_ADD, null, utteranceId);
                Log.e("setColor", "Error", e);
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                responsefromraspberry = response.body().string();
                switch (LEDstripcolor) {
                    case "FF0000":
                        TTS.speak("The color is set to red",
                                TextToSpeech.QUEUE_ADD, null, utteranceId);
                        break;
                    case "00FF00":
                        TTS.speak("The color is set to green",
                                TextToSpeech.QUEUE_ADD, null, utteranceId);
                        break;
                    case "0000FF":
                        TTS.speak("The color is set to blue",
                                TextToSpeech.QUEUE_ADD, null, utteranceId);
                        break;
                    case "FFFF00":
                        TTS.speak("The color is set to yellow",
                                TextToSpeech.QUEUE_ADD, null, utteranceId);
                        break;
                    case "FF00FF":
                        TTS.speak("The color is set to purple",
                                TextToSpeech.QUEUE_ADD, null, utteranceId);
                        break;
                    case "FFFFFF":
                        TTS.speak("The color is set to white",
                                TextToSpeech.QUEUE_ADD, null, utteranceId);
                        break;
                    case "000000":
                        TTS.speak("The lights are off",
                                TextToSpeech.QUEUE_ADD, null, utteranceId);
                        break;
                    case "random":
                        TTS.speak("The color is set to a random color",
                                TextToSpeech.QUEUE_ADD, null, utteranceId);
                        break;
                }
                Log.i("setColor", "Response: " + responsefromraspberry);
            }
        });
    }

    // Simple delay method to reduce TTS collisions between queries
    private void delay(int seconds) {
        try {
            sleep(seconds * 1000L);
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
    }
}
```

*(Adjust the package name, imports, and references as needed.)*

### 4.6 Build and Install on a Real Android Device

1. Connect your Android phone (with USB Debugging enabled in **Developer Options**) to your computer.  
2. In Android Studio, select **Run** → **Run app**.  
   - Choose your device in the deployment target window.  
   - If you don’t see your device, ensure drivers are installed and debugging is enabled.  

Alternatively:

- **Build** → **Build APK(s)** → Copy the resulting `app-debug.apk` to your device manually → **Install** from file explorer (you may need to enable “Unknown sources” in your phone’s settings).  

After installing and opening the app, you should see just one button labeled “talk”.

---

## 5. Testing the Whole System

1. **Ensure the Pi server is running** in Thonny.  
2. **Open the app** on your Android phone.  
3. Tap “talk” and speak a command, for example:  
   - “What is the temperature?”  
   - “Switch on the light color red.”  
   - “Switch off the light.”  
   - “Give me the weather forecast.”  
4. Observe how the Pi console logs each request.  
   - The LED strip should change color in real time.  
   - The Pi will respond with sensor data.  
   - The app uses TextToSpeech to read the response.

If you encounter issues:

- Check that your phone and the Pi are on the **same local network**.  
- Double-check the IP address and port in `baseUrl` and in the Python server code.  
- Verify that the Pi’s firewall (if any) is not blocking port 8000.  
- Make sure the Pi server code has no syntax errors and is actually running.

---

## 6. (Optional) Troubleshooting Tips

1. **Permission Errors** on Pi:
   - You must be **root** to control the LED strip on GPIO18 with `rpi_ws281x`.
2. **Speech Recognition** not working on phone:
   - Make sure Google’s Speech Services or any required language pack is installed/enabled on your device.  
   - Ensure you have an active internet connection (speech recognition requires it by default, unless you have offline models).
3. **No sound from TTS**:
   - Check phone’s media volume.  
   - Confirm TTS is initialized (watch for TTS init failure in logs).
4. **No response from server**:
   - Try opening `http://<PiIP>:8000/temperature` in a mobile or desktop browser. If it returns a number, the server is reachable. If not, check network or IP config.
5. **LED strip color not changing**:
   - Verify correct wiring.  
   - Double-check that audio is disabled in `/boot/config.txt`.  
   - Confirm you are referencing **GPIO18** (BCM) and not the physical pin incorrectly.

---

## 7. Conclusion

By following these steps:

1. You have set up a **Python HTTP server** on Raspberry Pi to read sensor data and control an LED strip.  
2. You have created an **Android app** with:
   - A single button to trigger **speech recognition**.
   - OkHttp to make requests to the server.
   - TextToSpeech (TTS) to speak the server responses.  

You can expand or customize this project further:

- Add more sensor queries.  
- Add more color options or animations for the LED strip.  
- Add a UI element (e.g. text fields) to show recognized text or sensor data.  
- Use more sophisticated voice command parsing or an NLP library.

You now have a fully functional “Smart Home Voice Control” application!