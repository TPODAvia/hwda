Below is a **step-by-step** guide on how to create an Android application in **Android Studio (codenamed "Android Studio **[version may be named Ladybug, Electric Eel, etc.]"**)** that receives MQTT messages from an Arduino setup (or any other device) via a Mosquitto broker. This tutorial will walk you through **project creation**, **Gradle configuration**, **layout setup**, **permission settings**, **MQTT library integration**, and **code usage**.

---

## 1. Create a New Android Studio Project

1. **Launch Android Studio**.  
2. Click **New Project** (or **File** > **New** > **New Project**).
3. Select **Phone and Tablet** > **Empty Views Activity** (or a similar empty activity template).
4. Click **Next**.
5. **Name** your application, for example:  
   ```
   Remote Weather Station
   ```
6. Choose your **package name**, **save location**, **language** (Java, in this example), and **minimum SDK** (at least API 21 or higher).
7. Click **Finish** to create the project.

---

## 2. Add Required Permissions in `AndroidManifest.xml`

1. In the **Project** pane, open the `AndroidManifest.xml` file (usually in `app/src/main/AndroidManifest.xml`).
2. **Before** the `<application>` tag, add the following permissions:

   ```xml
   <uses-permission android:name="android.permission.WAKE_LOCK" />
   <uses-permission android:name="android.permission.INTERNET" />
   <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
   <uses-permission android:name="android.permission.READ_PHONE_STATE" />
   ```

3. **Inside** the `<application>` tag but **after** the `</activity>` tag, add the service definition for the Paho library:

   ```xml
   <service android:name="org.eclipse.paho.android.service.MqttService" />
   ```

Your `AndroidManifest.xml` might look like this (simplified example):

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.iotesixthmobile">

    <uses-permission android:name="android.permission.WAKE_LOCK" />
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.READ_PHONE_STATE" />

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.YourApp">

        <activity android:name=".MainActivity">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <service android:name="org.eclipse.paho.android.service.MqttService" />
        
    </application>

</manifest>
```

---

## 3. Configure Your `build.gradle` Files

### 3.1. **Module-level** `build.gradle` (usually `app/build.gradle`)

1. Open **Gradle Scripts** > **Module: app** (`build.gradle`).
2. In the `dependencies` section, **add** the Paho MQTT libraries:

   ```groovy
   dependencies {
       // ... other dependencies ...

       implementation 'org.eclipse.paho:org.eclipse.paho.client.mqttv3:1.2.5'
       implementation 'org.eclipse.paho:org.eclipse.paho.android.service:1.1.1'
   }
   ```

3. Ensure your `targetSdkVersion` and `compileSdkVersion` in the `defaultConfig` section are **30 or lower**. For example:

   ```groovy
   android {
       compileSdkVersion 35

       defaultConfig {
           applicationId "com.example.iotesixthmobile"
           minSdkVersion 21
           targetSdkVersion 30
           versionCode 1
           versionName "1.0"
       }
       // ...
   }
   ```

> **Important**: The Paho library used here has limitations on newer SDKs beyond 31. If you want to target a higher SDK, you may need a more up-to-date MQTT library or additional workarounds.

4. **Sync** the project by clicking **Sync Now** (usually appears at the top of the `build.gradle` file). This will download and link the MQTT libraries.

### 3.2. **Project-level** `gradle.properties` (usually in the **Gradle Scripts** folder)

1. Open **gradle.properties**.
2. Add the following line if not already present:
   ```properties
   android.enableJetifier=true
   ```
3. Save and re-sync if prompted.

---

## 4. Create the Layout (`activity_main.xml`)

1. In **Project** pane, expand **app** > **res** > **layout**.
2. Open or create **activity_main.xml**.
3. Replace its contents with the provided layout example (or customize as needed). Below is the provided sample layout:

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
           android:layout_marginBottom="32dp"
           android:text="Hello World!"
           android:textColor="@android:color/holo_green_dark"
           android:textSize="24sp"
           app:layout_constraintBottom_toTopOf="@+id/press"
           app:layout_constraintEnd_toEndOf="parent"
           app:layout_constraintStart_toStartOf="parent" />

       <TextView
           android:id="@+id/press"
           android:layout_width="wrap_content"
           android:layout_height="wrap_content"
           android:text="TextView"
           android:textColor="@android:color/holo_purple"
           android:textSize="24sp"
           app:layout_constraintBottom_toBottomOf="parent"
           app:layout_constraintEnd_toEndOf="parent"
           app:layout_constraintStart_toStartOf="parent"
           app:layout_constraintTop_toTopOf="parent" />

       <TextView
           android:id="@+id/hum"
           android:layout_width="wrap_content"
           android:layout_height="wrap_content"
           android:layout_marginTop="32dp"
           android:text="TextView"
           android:textColor="@android:color/holo_blue_light"
           android:textSize="24sp"
           app:layout_constraintEnd_toEndOf="parent"
           app:layout_constraintStart_toStartOf="parent"
           app:layout_constraintTop_toBottomOf="@+id/press" />

       <TextView
           android:id="@+id/lux"
           android:layout_width="wrap_content"
           android:layout_height="wrap_content"
           android:layout_marginTop="32dp"
           android:text="TextView"
           android:textColor="@android:color/holo_orange_dark"
           android:textSize="24sp"
           app:layout_constraintEnd_toEndOf="parent"
           app:layout_constraintStart_toStartOf="parent"
           app:layout_constraintTop_toBottomOf="@+id/hum" />

       <TextView
           android:id="@+id/topic"
           android:layout_width="wrap_content"
           android:layout_height="wrap_content"
           android:layout_marginBottom="32dp"
           android:text="TextView"
           android:textColor="@android:color/holo_red_light"
           android:textSize="24sp"
           app:layout_constraintBottom_toTopOf="@+id/temp"
           app:layout_constraintEnd_toEndOf="parent"
           app:layout_constraintStart_toStartOf="parent" />

       <androidx.appcompat.widget.Toolbar
           android:id="@+id/toolbar"
           android:layout_width="409dp"
           android:layout_height="wrap_content"
           android:background="?attr/colorPrimary"
           app:layout_constraintEnd_toEndOf="parent"
           app:layout_constraintStart_toStartOf="parent"
           app:layout_constraintTop_toTopOf="parent" />

       <TextView
           android:id="@+id/textView"
           android:layout_width="wrap_content"
           android:layout_height="wrap_content"
           android:text="@string/app_title"
           android:textColor="@android:color/white"
           android:textSize="24sp"
           app:layout_constraintBottom_toBottomOf="@+id/toolbar"
           app:layout_constraintEnd_toEndOf="parent"
           app:layout_constraintStart_toStartOf="parent"
           app:layout_constraintTop_toTopOf="@+id/toolbar" />

   </androidx.constraintlayout.widget.ConstraintLayout>
   ```

4. In **res** > **values** > **strings.xml**, add the following line:
   ```xml
   <string name="app_title">Remote Weather Station</string>
   ```

---

## 5. Create the Main Activity Class (`MainActivity.java`)

1. In your **java** folder (e.g., `app/src/main/java/com/example/iotesixthmobile/`), open or create **MainActivity.java**.
2. **Replace** the contents with the sample code below. Remember to change the package name to **your** package:

   ```java
   package com.example.iotesixthmobile;

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

       // The MQTT topic you want to subscribe to
       private String topicstr;

       @Override
       protected void onCreate(Bundle savedInstanceState) {
           super.onCreate(savedInstanceState);
           setContentView(R.layout.activity_main);

           // The topic your Arduino or other device is publishing to
           topicstr = "channel1";
           Log.d(TAG, "onCreate");

           initView();
           initMQTT();
       }

       @Override
       protected void onDestroy() {
           super.onDestroy();
           Log.d(TAG, "onDestroy");
           // You could optionally disconnect from MQTT here if desired
       }

       //region MQTTListener callbacks
       @Override
       public void onConnected() {
           mqttClient.subscribe(topicstr);
       }

       @Override
       public void onConnectionFailure(Throwable t) {
           // Handle a failed connection
       }

       @Override
       public void onMessage(String topic, MqttMessage message) {
           Log.d(TAG, "Parsing message...");
           String payload = new String(message.getPayload());
           Log.d(TAG, "Payload [" + payload + "]");

           try {
               // Parse JSON
               JSONObject obj = new JSONObject(payload);
               String temp = obj.optString("t");
               String press = obj.optString("p");
               String hum = obj.optString("h");
               String lux = obj.optString("l");

               updateView(topic, temp, press, hum, lux);
           } catch (JSONException jse) {
               jse.printStackTrace();
           }
       }

       @Override
       public void onError(MqttException mqe) {
           // Handle errors
       }
       //endregion

       private void initMQTT() {
           mqttClient = MQTTClient.getInstance(this);
           mqttClient.setListener(this);
           mqttClient.connectToMQTT(MQTTClient.MQTT_SERVER);
       }

       private void initView() {
           chView = findViewById(R.id.topic);
           tempView = findViewById(R.id.temp);
           pressView = findViewById(R.id.press);
           humView = findViewById(R.id.hum);
           luxView = findViewById(R.id.lux);

           chView.setText("Topic: ");
           tempView.setText("Temperature: ");
           pressView.setText("Pressure: ");
           humView.setText("Humidity: ");
           luxView.setText("Illumination: ");
       }

       private void updateView(String topic, String temp, String press, String hum, String lux) {
           chView.setText("Topic: " + topic);
           tempView.setText("Temperature: " + temp + " C");
           pressView.setText("Pressure: " + press + " mmHg");
           humView.setText("Humidity: " + hum + " %");

           // Example logic to interpret "lux" if it's an integer
           try {
               int luxValue = Integer.parseInt(lux);
               float voltage = luxValue * 5.0f / 1024.0f;

               if (voltage >= 0 && voltage <= 0.4) {
                   luxView.setText("Illumination: " + voltage + "V. It is light. Resistance value: " + luxValue);
               } else if (voltage > 0.4 && voltage <= 2) {
                   luxView.setText("Illumination: " + voltage + "V. It is bright. Resistance value: " + luxValue);
               } else {
                   luxView.setText("Illumination: " + voltage + "V. It is dark. Resistance value: " + luxValue);
               }
           } catch (NumberFormatException e) {
               // If not a number or missing
               luxView.setText("Illumination: N/A");
           }
       }
   }
   ```

- Adjust the `topicstr` to the **MQTT topic** that your Arduino publishes messages on.  
- Adjust text or logic as needed for your JSON structure.

---

## 6. Create the `MQTTClient.java` Class

1. In your **java** folder, create a new Java class file named **MQTTClient.java**.
2. Replace its contents with the provided code, updating the package name and MQTT server address if needed:

   ```java
   package com.example.iotesixthmobile;  // change to your package

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

       // Change to your Raspberry Pi or Mosquitto server IP/Port
       public static final String MQTT_SERVER = "tcp://192.168.1.106:1883";

       private static MQTTClient me;
       private Context ctx;
       private MQTTListener listener;
       private MqttAndroidClient mqttClient;

       private MQTTClient(Context ctx) {
           this.ctx = ctx;
       }

       public static MQTTClient getInstance(MainActivity ctx) {
           if (me == null) {
               me = new MQTTClient(ctx);
           }
           return me;
       }

       public void setListener(MQTTListener listener) {
           this.listener = listener;
       }

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
                       if (listener != null) {
                           listener.onConnected();
                       }
                   }

                   @Override
                   public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
                       Log.e(TAG, "Failure");
                       exception.printStackTrace();
                       if (listener != null) {
                           listener.onConnectionFailure(exception);
                       }
                   }
               });
           } catch (MqttException mqe) {
               Log.e(TAG, "Unable to connect to MQTT Server");
               mqe.printStackTrace();
               if (listener != null) {
                   listener.onError(mqe);
               }
           }
       }

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
                       Log.e(TAG, "Error while subscribing to the topic [" + topic + "]");
                       exception.printStackTrace();
                   }
               });
           } catch (MqttException e) {
               e.printStackTrace();
           }
       }

       //region MqttCallback methods
       @Override
       public void connectionLost(Throwable cause) {
           Log.w(TAG, "Connection to MQTT lost!");
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
           Log.d(TAG, "Delivery complete");
       }
       //endregion

       public interface MQTTListener {
           void onConnected();
           void onConnectionFailure(Throwable t);
           void onMessage(String topic, MqttMessage message);
           void onError(MqttException mqe);
       }
   }
   ```

> **Key items to update**:
> - `public static final String MQTT_SERVER = "tcp://192.168.1.106:1883";`  
>   Replace with your **Mosquitto** broker IP address and **port** (e.g., `tcp://192.168.0.10:1883`).

---

## 7. Double-Check Your Configuration

1. **Package Name**: Make sure `MainActivity.java` and `MQTTClient.java` are in the same package or that you adjust `import` statements accordingly.
2. **MQTT IP/Port**: Make sure the broker (`Raspberry Pi` or any server) is actually **192.168.1.106**:1883 or update to your setup.
3. **Network**: Your **Android device** running this application must be on the **same network** as the MQTT broker. If using a hotspot from a phone, ensure both the **Arduino** (or other device) and the **Raspberry Pi** or broker **connect to that same hotspot**.

---

## 8. Run the Application

1. **Connect** a real Android device via USB or use an **Android Emulator** (though emulators can have networking constraints).
2. **Click** the green "Run" button in Android Studio.
3. **Select** your device/emulator.
4. The application should build, install, and run on the device.

---

## 9. Verify MQTT Messages

1. If your Arduino (or other MQTT publisher) is publishing JSON messages to the topic `channel1`, you should see the logs in **Logcat** in Android Studio:
   ```
   D/MQTTClient: Message arrived...
   Payload [{"t":"25","h":"15","p":"766","l":"270"}]
   ```
2. The **TextViews** on the main screen should update with the incoming values.

---

## 10. Troubleshooting Tips

- **Check the Broker**: Ensure Mosquitto is running on your Raspberry Pi:
  ```bash
  sudo systemctl status mosquitto
  ```
- **Monitor Broker Messages**: On your Raspberry Pi, subscribe to the same topic with:
  ```bash
  mosquitto_sub -t channel1 -v
  ```
  This confirms whether messages are actually arriving at the broker.
- **Logcat Output**: Use **Logcat** (bottom panel in Android Studio) to see if the app is connecting or encountering errors.
- **Same Network**: Verify that the phone (or emulator), Raspberry Pi, and Arduino are all on the same local network or hotspot.

---

## 11. (Optional) Dynamically Changing MQTT Topic or IP

As mentioned, you can:
- Add **EditText** fields in `activity_main.xml` for **broker IP** and **topic**.
- Store those values and pass them when calling `connectToMQTT()` or `subscribe()`.
- This way, you can change topics or broker addresses on the fly without recompiling.

---

## Conclusion

By following the steps above, you’ll have:

1. A **new Android app** in Android Studio.
2. Permissions and a **service** for the Paho MQTT library configured in `AndroidManifest.xml`.
3. Correctly **added Paho MQTT dependencies** to `build.gradle`.
4. A **simple UI** (`activity_main.xml`) to display sensor data.
5. A **`MainActivity`** that implements `MQTTClient.MQTTListener` to handle connection, subscription, and messages.
6. An **`MQTTClient`** class that manages the connection to your Mosquitto broker.

When the Arduino publishes data in **JSON** format (e.g., `{"t":"25","h":"15","p":"766","l":"270"}`), you’ll see it **decoded** in the Android app. The text views will update with temperature, humidity, pressure, and illumination values as new messages arrive. 

That’s it! You now have a **Remote Weather Station** Android application receiving MQTT data in real time.