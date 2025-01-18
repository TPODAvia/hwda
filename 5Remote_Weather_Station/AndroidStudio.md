Below is a **step-by-step** guide on how to create an **Android Studio** application that can **receive MQTT messages** (published by your Arduino or any other MQTT client). This guide is based on the setup you provided, but organized as a clear checklist.

---

## 1. Create a New Project in Android Studio
1. **Open Android Studio** and click on **"New Project"** (or **File > New > New Project**).
2. Select **"Phone and Tablet"** as the form factor.
3. Choose **"Empty Views Activity"** (or simply **Empty Activity**, depending on your version of Android Studio).
4. Enter the **Project Name**: for example, **Remote Weather Station**.
5. Click **Finish** to create the project.

---

## 2. Add Required Permissions in AndroidManifest.xml

1. In Android Studio’s **Project** pane, expand **`app > manifests`** and open **`AndroidManifest.xml`**.
2. Before the opening `<application ...>` tag, add the following permissions:
   ```xml
   <uses-permission android:name="android.permission.WAKE_LOCK" />
   <uses-permission android:name="android.permission.INTERNET" />
   <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
   <uses-permission android:name="android.permission.READ_PHONE_STATE" />
   ```
3. After the **closing** `</activity>` tag (inside `<application>...</application>`), add the MQTT service for Paho:
   ```xml
   <service android:name="org.eclipse.paho.android.service.MqttService" />
   ```

Your **AndroidManifest.xml** might look like this:

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest ... >

    <uses-permission android:name="android.permission.WAKE_LOCK" />
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.READ_PHONE_STATE" />

    <application
        ... >

        <activity
            android:name=".MainActivity"
            android:label="@string/app_name"
            ... >
        </activity>

        <service android:name="org.eclipse.paho.android.service.MqttService" />

    </application>

</manifest>
```

---

## 3. Add MQTT Dependencies in build.gradle (Module: app)
1. In the **Project** pane, expand **`Gradle Scripts`** and open **`build.gradle (Module: app)`**.
2. In the **dependencies** block, add:
   ```groovy
   implementation 'org.eclipse.paho:org.eclipse.paho.client.mqttv3:1.2.5'
   implementation 'org.eclipse.paho:org.eclipse.paho.android.service:1.1.1'
   ```
3. Make sure your **targetSdkVersion** is **30** or below. For example:
   ```groovy
   android {
       compileSdkVersion 30

       defaultConfig {
           applicationId "com.example.iotesixthmobile"
           minSdkVersion 21
           targetSdkVersion 30
           versionCode 1
           versionName "1.0"
       }
       ...
   }
   ```
4. Click **"Sync Now"** (or **"Sync Project with Gradle Files"**) after editing `build.gradle`.

---

## 4. Add `android.enableJetifier=true` to Gradle Properties
1. In the **Project** pane, expand **Gradle Scripts**.
2. Open **`gradle.properties (Project Properties)`**.
3. Add the following line (if not already present):
   ```groovy
   android.enableJetifier=true
   ```
4. Sync the project again to ensure the setting takes effect.

---

## 5. Create/Update the Layout (activity_main.xml)
1. In **`res/layout`**, open or create **`activity_main.xml`**.
2. Replace the contents with the following example (or adapt it as needed):
   ```xml
   <?xml version="1.0" encoding="utf-8"?>
   <androidx.constraintlayout.widget.ConstraintLayout
       xmlns:android="http://schemas.android.com/apk/res/android"
       xmlns:app="http://schemas.android.com/apk/res-auto"
       xmlns:tools="http://schemas.android.com/tools"
       android:layout_width="match_parent"
       android:layout_height="match_parent"
       tools:context=".MainActivity">

       <TextView
           android:id="@+id/temp"
           android:layout_width="wrap_content"
           android:layout_height="wrap_content"
           android:text="Hello World!"
           android:textSize="24sp"
           android:textColor="@android:color/holo_green_dark"
           app:layout_constraintStart_toStartOf="parent"
           app:layout_constraintEnd_toEndOf="parent"
           app:layout_constraintTop_toTopOf="parent" />

       <TextView
           android:id="@+id/press"
           android:layout_width="wrap_content"
           android:layout_height="wrap_content"
           android:text="TextView"
           android:textSize="24sp"
           android:textColor="@android:color/holo_purple"
           app:layout_constraintStart_toStartOf="parent"
           app:layout_constraintEnd_toEndOf="parent"
           app:layout_constraintTop_toBottomOf="@+id/temp" />

       <TextView
           android:id="@+id/hum"
           android:layout_width="wrap_content"
           android:layout_height="wrap_content"
           android:text="TextView"
           android:textSize="24sp"
           android:textColor="@android:color/holo_blue_light"
           app:layout_constraintStart_toStartOf="parent"
           app:layout_constraintEnd_toEndOf="parent"
           app:layout_constraintTop_toBottomOf="@+id/press" />

       <TextView
           android:id="@+id/lux"
           android:layout_width="wrap_content"
           android:layout_height="wrap_content"
           android:text="TextView"
           android:textSize="24sp"
           android:textAlignment="center"
           android:textColor="@android:color/holo_orange_dark"
           app:layout_constraintStart_toStartOf="parent"
           app:layout_constraintEnd_toEndOf="parent"
           app:layout_constraintTop_toBottomOf="@+id/hum" />

       <TextView
           android:id="@+id/topic"
           android:layout_width="wrap_content"
           android:layout_height="wrap_content"
           android:text="TextView"
           android:textSize="24sp"
           android:textColor="@android:color/holo_red_light"
           app:layout_constraintStart_toStartOf="parent"
           app:layout_constraintEnd_toEndOf="parent"
           app:layout_constraintTop_toBottomOf="@+id/lux" />

       <androidx.appcompat.widget.Toolbar
           android:id="@+id/toolbar"
           android:layout_width="match_parent"
           android:layout_height="wrap_content"
           android:background="?attr/colorPrimary"
           android:theme="?attr/actionBarTheme"
           app:layout_constraintTop_toTopOf="parent" />

       <TextView
           android:id="@+id/textView"
           android:layout_width="wrap_content"
           android:layout_height="wrap_content"
           android:text="@string/app_title"
           android:textSize="24sp"
           android:textColor="@android:color/white"
           app:layout_constraintBottom_toBottomOf="@+id/toolbar"
           app:layout_constraintEnd_toEndOf="parent"
           app:layout_constraintStart_toStartOf="parent"
           app:layout_constraintTop_toTopOf="@+id/toolbar" />

   </androidx.constraintlayout.widget.ConstraintLayout>
   ```

3. In the **`res/values/strings.xml`** file, add (or modify) a line for your app title:
   ```xml
   <string name="app_title">Remote Weather Station</string>
   ```

---

## 6. Create the MainActivity Class
1. In **`app/java/your_package_name`**, open (or create) **`MainActivity.java`**.
2. Paste the following code, ensuring the package name at the top matches your project:
   ```java
   package com.example.iotesixthmobile; // <-- change to your own package name

   import android.app.Activity;
   import android.os.Bundle;
   import android.util.Log;
   import android.widget.TextView;

   import org.eclipse.paho.client.mqttv3.MqttException;
   import org.eclipse.paho.client.mqttv3.MqttMessage;
   import org.json.JSONException;
   import org.json.JSONObject;

   public class MainActivity extends Activity implements MQTTClient.MQTTListener {

       private static final String TAG = MainActivity.class.getSimpleName();

       private MQTTClient mqttClient;
       private TextView chView;
       private TextView tempView;
       private TextView pressView;
       private TextView humView;
       private TextView luxView;

       // The MQTT topic you want to subscribe to.
       private String topicstr = "channel1";

       @Override
       protected void onCreate(Bundle savedInstanceState) {
           super.onCreate(savedInstanceState);
           setContentView(R.layout.activity_main);

           Log.d(TAG, "onCreate");
           initView();
           initMQTT();
       }

       @Override
       protected void onDestroy() {
           super.onDestroy();
           Log.d(TAG, "onDestroy");
       }

       // MQTTListener callbacks
       @Override
       public void onConnected() {
           mqttClient.subscribe(topicstr);
       }

       @Override
       public void onConnectionFailure(Throwable t) {
           // Handle connection failure
       }

       @Override
       public void onMessage(String topic, MqttMessage message) {
           // Parse the payload
           Log.d(TAG, "Parsing message...");
           String payload = new String(message.getPayload());
           Log.d(TAG, "Payload [" + payload + "]");

           try {
               JSONObject obj = new JSONObject(payload);
               // Extract values from the JSON object
               String temp = obj.optString("t", "0");
               String press = obj.optString("p", "0");
               String hum = obj.optString("h", "0");
               String lux = obj.optString("l", "0");

               // Update the UI
               updateView(topic, temp, press, hum, lux);

           } catch (JSONException jse) {
               jse.printStackTrace();
           }
       }

       @Override
       public void onError(MqttException mqe) {
           // Handle MQTT errors
       }

       // Initialize the MQTT client
       private void initMQTT() {
           mqttClient = MQTTClient.getInstance(this);
           mqttClient.setListener(this);
           mqttClient.connectToMQTT(MQTTClient.MQTT_SERVER);
       }

       // Link XML views to Java
       private void initView() {
           chView = findViewById(R.id.topic);
           chView.setText("Topic: ");

           tempView = findViewById(R.id.temp);
           tempView.setText("Temperature: ");

           pressView = findViewById(R.id.press);
           pressView.setText("Pressure: ");

           humView = findViewById(R.id.hum);
           humView.setText("Humidity: ");

           luxView = findViewById(R.id.lux);
           luxView.setText("Illumination: ");
       }

       // Update text fields in the UI with MQTT data
       private void updateView(String topic, String temp, String press, String hum, String lux) {
           chView.setText("Topic: " + topic);
           tempView.setText("Temperature: " + temp + " °C");
           pressView.setText("Pressure: " + press + " mmHg");
           humView.setText("Humidity: " + hum + " %");

           // Example logic for 'lux' or 'lightVal'
           // Convert the lux string to an int
           int luxInt = Integer.parseInt(lux);
           float voltage = luxInt * 5.0f / 1024.0f;

           luxView.setText("Illumination: " + voltage + ". Resistance value: " + luxInt);
       }
   }
   ```

---

## 7. Create the MQTTClient Class
1. In the same package (e.g., `com.example.iotesixthmobile`), create a new Java class named **`MQTTClient.java`**.
2. Paste the following code, again ensuring the package name matches your project:

   ```java
   package com.example.iotesixthmobile; // change to your own package name

   import android.content.Context;
   import android.util.Log;

   import org.eclipse.paho.android.service.MqttAndroidClient;
   import org.eclipse.paho.client.mqttv3.IMqttActionListener;
   import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
   import org.eclipse.paho.client.mqttv3.IMqttToken;
   import org.eclipse.paho.client.mqttv3.MqttCallback;
   import org.eclipse.paho.client.mqttv3.MqttClient;
   import org.eclipse.paho.client.mqttv3.MqttException;
   import org.eclipse.paho.client.mqttv3.MqttMessage;

   public class MQTTClient implements MqttCallback {

       private static final String TAG = "MQTTClient";
       // Replace this with your Raspberry Pi's IP address and MQTT port.
       public static final String MQTT_SERVER = "tcp://192.168.1.106:1883";

       private static MQTTClient instance;
       private Context ctx;
       private MQTTListener listener;
       private MqttAndroidClient mqttClient;

       private MQTTClient(Context ctx) {
           this.ctx = ctx;
       }

       // Obtain an instance of MQTTClient
       public static MQTTClient getInstance(MainActivity ctx) {
           if (instance == null) {
               instance = new MQTTClient(ctx);
           }
           return instance;
       }

       // Set the listener for callbacks
       public void setListener(MQTTListener listener) {
           this.listener = listener;
       }

       // Connect to the MQTT broker
       public void connectToMQTT(String server) {
           Log.d(TAG, "Connecting to MQTT Server..");
           String clientId = MqttClient.generateClientId();
           Log.d(TAG, "Client Id [" + clientId + "]");

           mqttClient = new MqttAndroidClient(ctx, server, clientId);
           mqttClient.setCallback(this);

           try {
               IMqttToken mqttToken = mqttClient.connect();
               mqttToken.setActionCallback(new IMqttActionListener() {
                   @Override
                   public void onSuccess(IMqttToken asyncActionToken) {
                       Log.i(TAG, "Connected to MQTT server");
                       if (listener != null) listener.onConnected();
                   }

                   @Override
                   public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
                       Log.e(TAG, "Failure connecting to MQTT server");
                       exception.printStackTrace();
                       if (listener != null) listener.onConnectionFailure(exception);
                   }
               });
           } catch (MqttException mqe) {
               Log.e(TAG, "Unable to connect to MQTT Server");
               mqe.printStackTrace();
               if (listener != null) listener.onError(mqe);
           }
       }

       // Subscribe to a topic
       public void subscribe(final String topic) {
           try {
               IMqttToken subToken = mqttClient.subscribe(topic, 1);
               subToken.setActionCallback(new IMqttActionListener() {
                   @Override
                   public void onSuccess(IMqttToken asyncActionToken) {
                       Log.d(TAG, "Subscribed to topic [" + topic + "]");
                   }

                   @Override
                   public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
                       Log.e(TAG, "Error subscribing to topic [" + topic + "]");
                       exception.printStackTrace();
                   }
               });
           } catch (MqttException e) {
               e.printStackTrace();
           }
       }

       // MqttCallback overrides
       @Override
       public void connectionLost(Throwable cause) {
           Log.e(TAG, "Connection lost", cause);
       }

       @Override
       public void messageArrived(String topic, MqttMessage message) {
           Log.d(TAG, "Message arrived...");
           String payload = new String(message.getPayload());
           Log.d(TAG, "Payload [" + payload + "]");
           if (listener != null) {
               listener.onMessage(topic, message);
           }
       }

       @Override
       public void deliveryComplete(IMqttDeliveryToken token) {
           // Not used in this example
       }

       // Listener interface for callbacks
       public interface MQTTListener {
           void onConnected();
           void onConnectionFailure(Throwable t);
           void onMessage(String topic, MqttMessage message);
           void onError(MqttException mqe);
       }
   }
   ```

---

## 8. Run the Application
1. **Connect your Android device** (or use an emulator). Ensure your device or emulator **has internet access** on the **same network** as your Raspberry Pi MQTT broker (if testing locally).
2. **Click "Run"** in Android Studio.  
3. The application should install and launch on your device.

---

## 9. Verify MQTT Reception
1. Make sure **Mosquitto** (MQTT broker) is running on your Raspberry Pi at `192.168.1.106:1883` or your chosen address/port.
2. **Publish a test message** to the topic `channel1` from any MQTT client (for example, `mosquitto_pub` on the Raspberry Pi):
   ```bash
   mosquitto_pub -h 192.168.1.106 -t channel1 -m '{"t":"25","h":"15","p":"766","l":"278"}'
   ```
3. Check the **Logcat** in Android Studio or the on-screen text to see if the message arrives. The text fields (`tempView`, `pressView`, `humView`, `luxView`) should update accordingly.

---

## 10. Additional Notes
- If you need to **subscribe to a different topic** or **broker address**, simply change:
  - `topicstr` in **`MainActivity.java`** for the topic.
  - `MQTT_SERVER` in **`MQTTClient.java`** for the broker URL and port.
- If your Raspberry Pi or server is outside your local network, you’ll need proper **port forwarding** or a **public IP**.
- For advanced features (SSL/TLS, last will messages, etc.), consult the [Eclipse Paho Android documentation](https://www.eclipse.org/paho/).

---

# Finished!
You now have a **basic Android application** that **connects to an MQTT broker** using **Eclipse Paho** to **receive sensor data** published by an Arduino or any other MQTT client. This setup can be expanded with additional views, dynamic configuration, or more robust error handling as needed.