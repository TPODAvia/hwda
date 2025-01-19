Below is a **step-by-step guide** explaining how to extend your **previous Android project** with cloud capabilities using **ThingSpeak** and **MATLAB** scripts, as well as how to create an additional **Android app** to read the resulting weather forecast. The core idea is that your **first Android app** subscribes to MQTT data, averages it, and periodically sends it to **ThingSpeak**, while a **second Android app** reads the forecast from a separate ThingSpeak channel.

---

## 1. Add Cloud Capabilities to Your Existing Android MQTT App

We will modify the **Android Studio** project from the previous task (the one that receives MQTT messages and displays sensor data).

### 1.1. Add Volley Library Dependency

1. In **Android Studio**, open your existing **Android MQTT project**.
2. In the **Project** pane, expand **Gradle Scripts** and open the `build.gradle (Module: app)` file.
3. Inside the `dependencies` block, **add**:
   ```groovy
   implementation 'com.android.volley:volley:1.2.1'
   ```
4. **Sync** the project so that Gradle fetches the Volley library.

### 1.2. Add the INTERNET Permission

1. Open `AndroidManifest.xml` (found in `app/src/main/AndroidManifest.xml`).
2. If not already present, add:
   ```xml
   <uses-permission android:name="android.permission.INTERNET" />
   ```
3. **Save** the file.  

*(You may already have this permission from the previous steps, but confirm it is there.)*

---

## 2. Create `ThingSpeakClient.java`

We want a client class to handle HTTP requests to ThingSpeak. This class will be responsible for **sending** sensor data (temperature, pressure, humidity, illumination) via REST GET requests.

1. In **Android Studio**, under **app** > **java** > **your.package.name**, **create** a new Java class:
   - File name: **ThingSpeakClient.java**  
2. **Copy** or **type** the following code **(adjusting any package names or keys as necessary)**:

```java
package com.example.myweatherapp; // <-- Your actual package name

import android.content.Context;
import android.util.Log;
import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.StringRequest;
import com.android.volley.toolbox.Volley;

public class ThingSpeakClient {
    private static ThingSpeakClient me;
    private Context ctx;
    private RequestQueue queue;

    // Replace <your_api_key> with the actual Write API Key for your ThingSpeak channel
    private static final String THINGSPEAK_URL =
            "https://api.thingspeak.com/update?api_key=<your_api_key>";

    // Each sensor value is appended as field1, field2, field3, field4
    private String tempdata = "&field1=";
    private String humdata = "&field2=";
    private String pressdata = "&field3=";
    private String lightdata = "&field4=";

    private String deviceId;  // Not strictly required for this example
    private String token;     // Not strictly required for this example

    private String TAG = "ThingSpeakClient";

    // Private constructor for the singleton
    private ThingSpeakClient(Context ctx, String deviceId, String token) {
        this.ctx = ctx;
        this.deviceId = deviceId;
        this.token = token;
        createQueue();
    }

    // Create or reuse the Volley request queue
    private void createQueue() {
        if (queue == null) {
            queue = Volley.newRequestQueue(ctx.getApplicationContext());
        }
    }

    // Public static method to get instance (Singleton pattern)
    public static ThingSpeakClient getInstance(Context ctx, String deviceId, String token) {
        if (me == null) {
            me = new ThingSpeakClient(ctx, deviceId, token);
        }
        return me;
    }

    // Send data to ThingSpeak
    public void sendData(final double temp, final double press, final double hum, final double lux) {
        // Build ONE GET request URL containing all sensor data
        String url = THINGSPEAK_URL
                + tempdata + temp
                + humdata + hum
                + pressdata + press
                + lightdata + lux;

        // Create the request
        StringRequest request = new StringRequest(Request.Method.GET, url,
                new Response.Listener<String>() {
                    @Override
                    public void onResponse(String response) {
                        Log.d(TAG, "Response [" + response + "]");
                    }
                },
                new Response.ErrorListener() {
                    @Override
                    public void onErrorResponse(VolleyError error) {
                        error.printStackTrace();
                    }
                }
        );

        // Add the request to the queue
        queue.add(request);
    }
}
```

> **Important**:  
> - Update `<your_api_key>` in `THINGSPEAK_URL` with the **Write API Key** for your **ThingSpeak channel**.  
> - If you want to pass or store `deviceId`/`token` for future enhancements, keep them. Otherwise, these parameters can remain unused.

---

## 3. Modify `MainActivity.java` to Send Data to ThingSpeak

1. **Open** your `MainActivity.java` (the one receiving MQTT messages).
2. **Add** the variables needed for scheduling data sending (declared near the top of the class):

   ```java
   private static final int TIMEOUT = 30;  // Interval in seconds
   private int tempCounter = 0;
   private int pressCounter = 0;
   private int humCounter = 0;
   private int luxCounter = 0;

   private double totalTemp = 0;
   private double totalPress = 0;
   private double totalHum = 0;
   private double totalLux = 0;

   // If not used, you can keep placeholders
   private static String DEVICE_ID = "3c1e4c0b24f645258400e6e553bcc817";
   private static String TOKEN = "04b92cb5070f48aba72f1e030325c6f9";

   // For parsing JSON from MQTT
   public String temp;
   public String press;
   public String hum;
   public String lux;
   ```

3. In the `onMessage(...)` callback where the MQTT message arrives, **change** the JSON parsing so the data is saved into these variables (if not already):

   ```java
   @Override
   public void onMessage(String topic, MqttMessage message) {
       // ...
       String payload = new String(message.getPayload());
       try {
           JSONObject obj = new JSONObject(payload);
           temp = obj.getString("t");
           press = obj.getString("p");
           hum = obj.getString("h");
           lux = obj.getString("l");
           updateView(topic, temp, press, hum, lux);
       } catch (JSONException jse) {
           jse.printStackTrace();
       }
   }
   ```

4. At the **end** of your `updateView(...)` method, **accumulate** values for later averaging:

   ```java
   private void updateView(String topic, String temp, String press, String hum, String lux) {
       // existing UI updates...

       // Accumulate totals (convert String to int or double as needed)
       totalTemp += Integer.parseInt(temp);
       tempCounter++;

       totalPress += Integer.parseInt(press);
       pressCounter++;

       totalHum += Integer.parseInt(hum);
       humCounter++;

       totalLux += Integer.parseInt(lux);
       luxCounter++;
   }
   ```

5. **Schedule** sending data to ThingSpeak with a background thread. Add a method in `MainActivity.java`:

   ```java
   private void initScheduler() {
       ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();
       scheduler.scheduleWithFixedDelay(new Runnable() {
           @Override
           public void run() {
               // Calculate average sensor values since last push
               double mTemp = totalTemp / tempCounter;
               double mPress = totalPress / pressCounter;
               double mHum = totalHum / humCounter;
               double mLux = totalLux / luxCounter;

               // Reset counters for next cycle
               totalTemp = 0;
               totalPress = 0;
               totalHum = 0;
               totalLux = 0;
               tempCounter = 0;
               pressCounter = 0;
               humCounter = 0;
               luxCounter = 0;

               // Send data to ThingSpeak
               ThingSpeakClient.getInstance(MainActivity.this, DEVICE_ID, TOKEN)
                               .sendData(mTemp, mPress, mHum, mLux);
           }
       }, 30, TIMEOUT, TimeUnit.SECONDS);
       // First run after 30 seconds, repeated every TIMEOUT seconds
   }
   ```

6. In your `onCreate(...)` method, **call** `initScheduler()` at the end:

   ```java
   @Override
   protected void onCreate(Bundle savedInstanceState) {
       super.onCreate(savedInstanceState);
       setContentView(R.layout.activity_main);

       // your existing MQTT and UI setup...

       initScheduler(); // Start the periodic averaging & cloud sending
   }
   ```

With these changes, your app will **receive sensor data** from MQTT, **average** it, and **send** it to your **ThingSpeak channel** every 30 seconds (or however long you set in `TIMEOUT`).

---

## 4. Verify Data in ThingSpeak

1. **Open** your ThingSpeak channel in a browser.  
2. Go to **Private View** to see real-time graphs.  
   - You should see **fields** (Temperature, Pressure, Humidity, Illumination) update as your Android app pushes new data.  
3. **Check** logs in **Logcat** in Android Studio to see the GET request responses. 

---

## 5. Add a Simple Weather Forecast in ThingSpeak (MATLAB Analysis)

**ThingSpeak** can run MATLAB scripts to **read** your sensor data, **compute** a result (like a forecast), and **write** it to a **separate channel**. Below is an outline:

1. **Create a second channel** in ThingSpeak, which will hold a single field (e.g., a textual weather forecast).
2. Get the **Write API Key** of the second channel.
3. In your **first channel** (the one receiving data from the Android app), click **MATLAB Analysis**.
4. **Create** a custom MATLAB script:
   ```matlab
   readChId = 123456;  % ID of first channel
   writeChId = 789012; % ID of second channel
   readKey = 'YOUR_READ_KEY_FOR_CH1';
   writeKey = 'YOUR_WRITE_KEY_FOR_CH2';

   [pressure,time] = thingSpeakRead(readChId, 'Fields',3, 'NumPoints',1, 'ReadKey',readKey);

   LEVEL_1 = 767.2;  % mmHg
   LEVEL_2 = 756.92; % mmHg
   if (pressure >= LEVEL_1)
       text="The weather will be stable";
   elseif (pressure >= LEVEL_2 && pressure <= LEVEL_1)
       text="The weather will be cloudy";
   else
       text="The weather will be rainy";
   end

   thingSpeakWrite(writeChId,'Fields',1,'TimeStamps',time,'Values',text,'Writekey',writeKey);
   disp(text);
   ```
5. **Save** the script, then **Run** it manually once to confirm it writes a forecast string into **Field 1** of the second channel.
6. **Set a TimeControl** in ThingSpeak to run the MATLAB script automatically (for example, every 5 minutes).

---

## 6. Create a Second Android App to Read the Forecast

Finally, we’ll build a **separate Android app** that fetches the forecast from the **second ThingSpeak channel**. This app does **not** need MQTT; it only performs **HTTP GET** requests on the channel’s feed.

### 6.1. Create a New Android Studio Project

1. **File** > **New** > **New Project** in Android Studio.  
2. Choose **Empty Activity** or **Empty Views Activity**.  
3. Name it something like “ThingSpeakForecastReader.”  
4. Set the language to **Java**.

### 6.2. Add INTERNET Permission and Volley Dependency

1. Open `AndroidManifest.xml` and add:
   ```xml
   <uses-permission android:name="android.permission.INTERNET" />
   ```
2. In `build.gradle (Module: app)`, add:
   ```groovy
   dependencies {
       // ...
       implementation 'com.android.volley:volley:1.2.1'
   }
   ```
3. **Sync** your project.

### 6.3. Simple Layout with Two TextViews

1. In `res/layout/activity_main.xml`, create a simple interface with two **TextViews** to show:
   - The **timestamp** of the forecast.
   - The **forecast** text.

   ```xml
   <?xml version="1.0" encoding="utf-8"?>
   <LinearLayout
       xmlns:android="http://schemas.android.com/apk/res/android"
       android:layout_width="match_parent"
       android:layout_height="match_parent"
       android:gravity="center"
       android:orientation="vertical">

       <TextView
           android:id="@+id/textView"
           android:layout_width="wrap_content"
           android:layout_height="wrap_content"
           android:textSize="20sp"
           android:textStyle="bold"
           android:text="Timestamp:" />

       <TextView
           android:id="@+id/textView2"
           android:layout_width="wrap_content"
           android:layout_height="wrap_content"
           android:layout_marginTop="16dp"
           android:textSize="20sp"
           android:text="Forecast will appear here" />
   </LinearLayout>
   ```

### 6.4. Implement `MainActivity.java`

1. Open or create `MainActivity.java` in the same package.
2. Paste the following code (adjusting your package name, IDs, etc.):

   ```java
   package com.example.iotsixthtschannelread;

   import androidx.appcompat.app.AppCompatActivity;
   import android.os.Bundle;
   import android.util.Log;
   import android.widget.TextView;
   import com.android.volley.Request;
   import com.android.volley.RequestQueue;
   import com.android.volley.Response;
   import com.android.volley.VolleyError;
   import com.android.volley.toolbox.StringRequest;
   import com.android.volley.toolbox.Volley;
   import org.json.JSONArray;
   import org.json.JSONException;
   import org.json.JSONObject;
   import java.util.concurrent.Executors;
   import java.util.concurrent.ScheduledExecutorService;
   import java.util.concurrent.TimeUnit;

   public class MainActivity extends AppCompatActivity {
       // Replace with your actual URL for reading the second channel's feed
       // e.g. "https://api.thingspeak.com/channels/<ch2ID>/feeds.json?api_key=<read_key>&results=1"
       private static final String THINGSPEAK_URL =
           "https://api.thingspeak.com/channels/2285639/feeds.json?api_key=XXXXXXXX&results=1";

       private String response1;
       private RequestQueue queue;
       private TextView textdate;
       private TextView textforecast;

       @Override
       protected void onCreate(Bundle savedInstanceState) {
           super.onCreate(savedInstanceState);
           setContentView(R.layout.activity_main);

           textdate = findViewById(R.id.textView);
           textforecast = findViewById(R.id.textView2);

           textdate.setText("");
           textforecast.setText("Loading forecast...");

           // Initialize and start our periodic data fetch
           initScheduler();
       }

       private void initScheduler() {
           ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();
           scheduler.scheduleWithFixedDelay(new Runnable() {
               @Override
               public void run() {
                   // Create or reuse a Volley request queue
                   if (queue == null) {
                       queue = Volley.newRequestQueue(MainActivity.this);
                   }

                   // Make a GET request to read the last forecast entry
                   StringRequest request = new StringRequest(Request.Method.GET, THINGSPEAK_URL,
                           new Response.Listener<String>() {
                               @Override
                               public void onResponse(String response) {
                                   response1 = response;
                                   try {
                                       JSONObject obj = new JSONObject(response1);
                                       JSONArray feeds = obj.getJSONArray("feeds");
                                       JSONObject obj1 = feeds.getJSONObject(0);

                                       // Extract creation time and forecast
                                       String thetime = obj1.getString("created_at");
                                       String theforecast = obj1.getString("field1");

                                       // Update the UI (must be run on main thread)
                                       runOnUiThread(new Runnable() {
                                           @Override
                                           public void run() {
                                               textdate.setText(thetime);
                                               textforecast.setText(theforecast);
                                           }
                                       });
                                   } catch (JSONException jse) {
                                       jse.printStackTrace();
                                   }
                                   Log.d("ThingSpeakForecastReader", "Response [" + response + "]");
                               }
                           },
                           new Response.ErrorListener() {
                               @Override
                               public void onErrorResponse(VolleyError error) {
                                   error.printStackTrace();
                               }
                           }
                   );

                   // Add the request to the queue
                   queue.add(request);
               }
           }, 10, 60, TimeUnit.SECONDS); 
           // first run at 10s, then every 60s
       }
   }
   ```

> **Key Points**:
> - We parse the **JSON** response (similar to Figure 125) to extract `created_at` and `field1`.
> - We then **update** the `TextView` with the **timestamp** and **weather forecast** text.
> - The code runs on a **scheduler** that repeats every 60 seconds.  
>   (You can pick a shorter or longer interval.)

### 6.5. Run & Test Your Forecast App

1. **Run** this new app on an Android device or emulator.
2. It will show the **most recent** forecast string from your **second channel** in ThingSpeak.  
3. The data can be accessed **from anywhere**, as it’s pulled from the **ThingSpeak cloud**.

---

## 7. Putting It All Together

1. **Arduino** (or any MCU) publishes sensor data to `channel1` via MQTT -> **Mosquitto** on Raspberry Pi.  
2. **Android App #1** (MQTT subscriber) receives data, displays it in the UI, then periodically sends averages to **ThingSpeak** (Channel #1).  
3. A **MATLAB script** in ThingSpeak reads the last pressure from Channel #1, computes a forecast, writes the text to **Channel #2**.  
4. **Android App #2** periodically **fetches** the latest forecast from Channel #2’s feed and displays it.

You now have a **complete chain** from sensor -> MQTT -> mobile -> cloud -> forecast -> second mobile app. You can adapt or expand this architecture with more fields, security, or different cloud services.

---

## 8. Troubleshooting Tips

1. **Check your ThingSpeak channel’s Write & Read API keys**: Make sure you are using the correct **channel ID** and **keys** (typos are common).  
2. **Keep an eye on Logcat**: If Volley or MQTT connections fail, you’ll see stack traces or error messages here.  
3. **Scheduling intervals**: If you push/pull data too frequently, you might run into **rate limits** on ThingSpeak’s free tier (usually 15 seconds minimum).  
4. **MATLAB script** limitations**: For free accounts, you can only run scripts every 5 minutes. Adjust TimeControl accordingly.  
5. **Network constraints**: The first Android app and the Arduino must share a LAN or hotspot to reach the Raspberry Pi’s **Mosquitto** broker. However, the second app can be **anywhere** that has internet, because it only queries **ThingSpeak**.

---

### Summary

- **Added Volley** for HTTP requests in your first Android app.  
- **Created `ThingSpeakClient.java`** to **send** sensor data.  
- **Modified `MainActivity.java`** to accumulate data and **send** it periodically.  
- **Verified** data arrives in **ThingSpeak**.  
- **Used MATLAB Analysis** to read pressure and output a simple textual forecast in **Channel #2**.  
- **Built a second Android app** that **fetches** this forecast and displays it in real time.

You now have a **multi-layered IoT architecture**: from raw sensor values through MQTT, local mobile consumption, cloud storage/analysis, and global availability via a second Android client app. This approach showcases how to integrate **ThingSpeak**’s cloud services with **Android** apps, enabling you to develop powerful IoT solutions.