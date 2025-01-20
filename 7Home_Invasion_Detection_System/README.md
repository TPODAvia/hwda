Below is a comprehensive, step-by-step guide to building a Home Invasion Detection System using:

1. **A Raspberry Pi** (3 or 4) with a PIR sensor and camera,  
2. **Google Firebase** (as the cloud platform to store images and send push notifications),  
3. **An Android app built in Android Studio** (here referred to as “Ladybug,” though these steps are generally the same for most recent versions of Android Studio).

---

## Table of Contents

1. [Project Overview](#project-overview)  
2. [Hardware Setup](#hardware-setup)  
   - [Required Components](#required-components)  
   - [Wiring the PIR Sensor to the Raspberry Pi](#wiring-the-pir-sensor-to-the-raspberry-pi)  
   - [Connecting the Raspberry Pi Camera Module](#connecting-the-raspberry-pi-camera-module)  
3. [Setting Up Raspberry Pi Software](#setting-up-raspberry-pi-software)  
   - [Installing Python Libraries](#installing-python-libraries)  
   - [Creating the Python Script](#creating-the-python-script)  
   - [How the Code Works](#how-the-code-works)  
   - [Testing the Raspberry Pi Code (Without Firebase)](#testing-the-raspberry-pi-code-without-firebase)  
4. [Setting Up Google Firebase](#setting-up-google-firebase)  
   - [Create a Firebase Project](#create-a-firebase-project)  
   - [Add an Android App to Firebase](#add-an-android-app-to-firebase)  
   - [Configure Firebase Storage](#configure-firebase-storage)  
   - [Configure Firebase Realtime Database](#configure-firebase-realtime-database)  
   - [Add a Web App to Retrieve `firebaseConfig` Object](#add-a-web-app-to-retrieve-firebaseconfig-object)  
   - [Generate a Service Account Key for the Raspberry Pi](#generate-a-service-account-key-for-the-raspberry-pi)  
5. [Integrating Raspberry Pi with Firebase](#integrating-raspberry-pi-with-firebase)  
   - [Updating the Python Script to Send Data to Firebase](#updating-the-python-script-to-send-data-to-firebase)  
   - [Verifying Raspberry Pi → Firebase Communication](#verifying-raspberry-pi-–-firebase-communication)  
6. [Building the Android App (in Android Studio Ladybug)](#building-the-android-app-in-android-studio-ladybug)  
   - [Create a New Android Project](#create-a-new-android-project)  
   - [Add the Firebase SDK and Configuration Files](#add-the-firebase-sdk-and-configuration-files)  
   - [Add Dependencies to `build.gradle` (Module: app)](#add-dependencies-to-buildgradle-module-app)  
   - [Configure Permissions in `AndroidManifest.xml`](#configure-permissions-in-androidmanifestxml)  
   - [Implementing Firebase Messaging Services](#implementing-firebase-messaging-services)  
   - [Creating the App UI (`activity_main.xml`)](#creating-the-app-ui-activity_mainxml)  
   - [MainActivity Logic to Subscribe and Display Images](#mainactivity-logic-to-subscribe-and-display-images)  
   - [Testing the Android App](#testing-the-android-app)  
7. [Final Integration and Testing](#final-integration-and-testing)  
8. [Troubleshooting](#troubleshooting)  

---

## 1. Project Overview
The goal is to detect motion in a room using a **PIR sensor** on a Raspberry Pi. Whenever the sensor detects movement:

1. The Raspberry Pi camera takes a snapshot (`image.png`).  
2. The Raspberry Pi uploads the snapshot to **Firebase Storage**.  
3. The Raspberry Pi sends a **push notification** via **Firebase Cloud Messaging (FCM)** to any subscribed Android device(s).  
4. The user’s Android app receives the notification (even if the app is closed), opens upon user tapping the notification, and then downloads and displays the snapshot from Firebase Storage.

---

## 2. Hardware Setup

### Required Components
1. **Raspberry Pi 3 or 4** (with Raspberry Pi OS installed, monitor/keyboard/mouse or SSH/VNC for setup).  
2. **PIR Sensor** (commonly with 3 pins: VCC, GND, and OUT).  
3. **Raspberry Pi Camera Module** (compatible with Pi 3/4).  
4. **Connecting Wires** (jumper wires).  
5. **HDMI cable** and monitor (if configuring Pi locally).  
6. **5V/2.5A (or higher) power adapter** for the Raspberry Pi.  
7. **Google account** and **Firebase account**.

### Wiring the PIR Sensor to the Raspberry Pi
1. **Power off** the Raspberry Pi before connecting any wires.  
2. The PIR sensor has three pins (check the back or remove the dome carefully if labels are hidden):
   - **VCC** (5V or 3.3V—many PIR sensors work at 5V or 3.3V, but consult your sensor specs)  
   - **GND**  
   - **OUT** (signal pin)  
3. On a Raspberry Pi board laid out with the pin numbers in **BOARD** mode:
   - Connect the **PIR VCC** to **Pin 2** or **Pin 4** (5V).  
   - Connect the **PIR GND** to **Pin 6** or any GND pin.  
   - Connect the **PIR OUT** to **Pin 7** (GPIO4 in BCM, but Pin 7 in BOARD numbering).  

```
+-----+-----+---------+------ ... 
| Pi3 | Pin | Function| 
+-----+-----+---------+------ ...
|     |  7  | GPIO4   | <-- PIR Out
|     |  2  | 5V      | <-- PIR VCC
|     |  6  | Ground  | <-- PIR GND
+-----+-----+---------+------
```

### Connecting the Raspberry Pi Camera Module
1. Locate the **CSI port** on the Raspberry Pi.  
2. Gently lift the plastic latch and insert the ribbon cable (metal contacts facing away from the Ethernet/USB ports, depending on Pi version).  
3. Push the latch back down.  
4. In **Raspberry Pi OS**, enable the camera interface if needed:
   - Go to `raspi-config` → `Interface Options` → `Camera` → Enable.  
   - Reboot if prompted.

---

## 3. Setting Up Raspberry Pi Software

### Installing Python Libraries
Open a terminal (or use Thonny’s “Terminal” area) on your Raspberry Pi and install the necessary libraries:

```bash
sudo apt-get update
sudo apt-get install python3-pip
pip3 install PySimpleGUI RPi.GPIO picamera
```

*(These are used for the GUI, GPIO control, and camera capture.)*

Later, when integrating with Firebase, you will also install:

```bash
pip3 install google-api-python-client pyrebase requests google-auth google-auth-oauthlib
```

### Creating the Python Script
Create (or open) a file called `motion_detector.py` (or similar) in the Pi’s home directory:

```python
import PySimpleGUI as sg
import RPi.GPIO as GPIO
from time import sleep
from picamera import PiCamera
import os

Movement_detected = False
camera = PiCamera(resolution=(800,600))
camera.shutter_speed = 60000  # shutter speed in microseconds (about 60ms)
camera.iso = 200

layout = [
    [sg.Image(size=(800, 600), key='-image-', pad=((5,5),(5,5)), background_color='white', expand_x=True)],
    [sg.Text('', key='-movement-', size=(20,1), expand_x=True, font=('Calibri', 48), justification='center')]
]

window = sg.Window('Home Invasion Detection', layout, size=(1280,800), finalize=True)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
GPIO.setup(7, GPIO.IN)

def DetectedCallback(channel):
    global Movement_detected
    Movement_detected = True
    print('Movement detected!')

GPIO.add_event_detect(7, GPIO.RISING, callback=DetectedCallback)

try:
    while True:
        if not Movement_detected:
            window['-movement-'].update('Waiting for movement…', text_color='white')
            window.refresh()
        else:
            try:
                # Capture image
                filename = os.path.join('image.png')
                camera.capture(filename)
                window['-image-'].update(filename=filename)
                window['-movement-'].update('Movement detected!', text_color='red')
                window.refresh()
                sleep(5)
            except Exception as E:
                print(f'** Error {E} **')
                pass
            Movement_detected = False
        sleep(0.1)
except KeyboardInterrupt:
    window.close()
    camera.close()
    GPIO.cleanup()

window.close()
camera.close()
GPIO.cleanup()
```

### How the Code Works
1. **Initialize** camera and GUI (with PySimpleGUI).  
2. **Set up GPIO** in `BOARD` mode and monitor **Pin 7** for rising edges (the PIR sensor’s output).  
3. When motion is detected, `DetectedCallback` sets `Movement_detected = True`.  
4. In the main loop, if `Movement_detected` is True:
   - The Pi camera captures an image (`image.png`), updates the GUI to show the picture, and sets a “Movement detected!” label.  
   - Resets `Movement_detected = False` after 5 seconds.

### Testing the Raspberry Pi Code (Without Firebase)
1. Ensure your camera is properly connected.  
2. Run the script in Thonny or via Terminal:
   ```bash
   python3 motion_detector.py
   ```  
3. Move your hand in front of the PIR sensor. The sensor’s LED (if present) should light briefly, and the application window on the Pi’s screen should update with a snapshot from the camera.

---

## 4. Setting Up Google Firebase

### Create a Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com/).  
2. Click **“Add project”** (or **“Create project”**).  
3. Enter a project name (e.g., `yet-another-motion-detector`), click **Continue**.  
4. You can disable Google Analytics if you wish, then click **Continue**.  
5. Wait for creation to finish, then click **Continue** to go to the project’s dashboard.

### Add an Android App to Firebase
1. In your Firebase project’s **Project Overview** page, click the **Android** icon (*“Add app”*).  
2. Enter your **Android package name** (e.g., `com.example.myapp`), the **app nickname** (optional), and click **Register app**.  
3. Download the `google-services.json` file.  
4. In Android Studio, place the `google-services.json` file in the **app** folder.  
5. Follow the instructions that appear to add Firebase to your Android build (we will detail this in [Section 6](#building-the-android-app-in-android-studio-ladybug)).

### Configure Firebase Storage
1. In the left-hand menu of the Firebase console, go to **Build** → **Storage**.  
2. Click **Get started**, then **Next**.  
3. Select a storage location (region closest to you), then click **Done**.  
4. Go to **Rules** tab:
   ```javascript
   rules_version = '2';
   service firebase.storage {
     match /b/{bucket}/o {
       match /{allPaths=**} {
         allow read, write;
       }
     }
   }
   ```
   - Replace the existing `allow read, write: if false;` with `allow read, write;` for testing.  
5. Click **Publish**.

### Configure Firebase Realtime Database
1. In the left-hand menu, go to **Build** → **Realtime Database**.  
2. Click **Create Database**.  
3. Choose the database location (same region as your storage, if possible).  
4. Select **Start in test mode** → **Enable**.  
5. You do not need to change the rules in test mode unless you want more security.

### Add a Web App to Retrieve `firebaseConfig` Object
1. Go to **Project Overview**.  
2. Click **Add app** → the **web icon** (`</>`).  
3. Name the app (e.g., “motion detector web config”) and click **Register app**.  
4. A `firebaseConfig` object will appear. Copy it somewhere safe. It looks like:
   ```js
   const firebaseConfig = {
     apiKey: "YOUR_API_KEY",
     authDomain: "your_project_id.firebaseapp.com",
     databaseURL: "https://your_project_id.firebaseio.com",
     projectId: "your_project_id",
     storageBucket: "your_project_id.appspot.com",
     messagingSenderId: "XXXXXXXXXXX",
     appId: "1:XXXXXXXXXXX:web:XXXXXXXXXXXXXX",
     measurementId: "G-XXXXXXXXXX"
   };
   ```

### Generate a Service Account Key for the Raspberry Pi
1. In the Firebase console, click the **gear icon** → **Project Settings**.  
2. Go to the **Service accounts** tab.  
3. Under **Firebase Admin SDK**, pick **Python** in the drop-down.  
4. Click **Generate new private key** → a JSON file downloads.  
5. Rename it to `service-account.json` and place it on the Raspberry Pi in the same directory as your `motion_detector.py` script.

---

## 5. Integrating Raspberry Pi with Firebase

### Updating the Python Script to Send Data to Firebase
Edit your `motion_detector.py` (or a copy of it) to include Firebase functionality:

1. **Install additional libraries** on Raspberry Pi (if not already done):
   ```bash
   pip3 install google-api-python-client pyrebase requests google-auth google-auth-oauthlib
   ```
2. **Add imports** to the top:
   ```python
   import json
   import requests
   import google.auth.transport.requests
   from google.oauth2 import service_account
   import pyrebase
   ```
3. **Define constants** for Firebase:
   ```python
   PROJECT_ID = 'yet-another-motion-detector'  # Your actual project ID
   BASE_URL = 'https://fcm.googleapis.com'
   FCM_ENDPOINT = f'v1/projects/{PROJECT_ID}/messages:send'
   FCM_URL = f'{BASE_URL}/{FCM_ENDPOINT}'
   SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']
   ```
4. **Add helper functions** for sending messages to FCM (HTTPv1):
   ```python
   def _get_access_token():
       credentials = service_account.Credentials.from_service_account_file(
           'service-account.json', scopes=SCOPES)
       request = google.auth.transport.requests.Request()
       credentials.refresh(request)
       return credentials.token

   def _send_fcm_message(fcm_message):
       headers = {
           'Authorization': 'Bearer ' + _get_access_token(),
           'Content-Type': 'application/json; UTF-8',
       }
       resp = requests.post(FCM_URL, data=json.dumps(fcm_message), headers=headers)
       if resp.status_code == 200:
           print('Message sent to Firebase for delivery, response:')
           print(resp.text)
       else:
           print('Unable to send message to Firebase')
           print(resp.text)

   def _build_common_message():
       # We send to the "alarm" topic
       return {
           'message': {
               'topic': 'alarm',
               'data': {
                   'message': 'Alarm! Someone is at home!'
               }
           }
       }
   ```
5. **Initialize Pyrebase** for Storage (using your `firebaseConfig` from the web app step):
   ```python
   firebaseConfig = {
       'apiKey': "YOUR_API_KEY",
       'authDomain': "your_project_id.firebaseapp.com",
       'databaseURL': "https://your_project_id.firebaseio.com",
       'projectId': "your_project_id",
       'storageBucket': "your_project_id.appspot.com",
       'messagingSenderId': "XXXXXXXXXXX",
       'appId': "1:XXXXXXXXXXX:web:XXXXXXXXXXXXXX",
       'measurementId': "G-XXXXXXXXXX"
   }

   firebase = pyrebase.initialize_app(firebaseConfig)
   storage = firebase.storage()
   ```
6. **Put it all together** in the `while True:` loop, after capturing the image:
   ```python
   filename = 'image.png'
   camera.capture(filename)
   # Update GUI
   window['-image-'].update(filename=filename)
   window['-movement-'].update('Movement detected!', text_color='red')
   window.refresh()

   # 1) Upload image to Firebase Storage
   storage.child(filename).put(filename)
   print(f'{filename} sent to firebase storage')

   # 2) Send FCM push notification
   common_message = _build_common_message()
   print('FCM request body:', json.dumps(common_message, indent=2))
   _send_fcm_message(common_message)

   # Avoid spamming notifications
   sleep(30)
   ```

### Verifying Raspberry Pi – Firebase Communication
1. **Run the updated script** on your Raspberry Pi:
   ```bash
   python3 motion_detector.py
   ```
2. Trigger motion (wave your hand in front of the PIR sensor).  
3. Look for console output in Thonny or the terminal indicating:
   - “Movement detected!”  
   - “Message sent to Firebase for delivery, response: … (JSON)…”  
4. In your Firebase console, go to **Storage** → **Files**. You should see `image.png`.  
5. Clicking it shows a thumbnail and a “File location” + “Access token” link you could open in a browser.

---

## 6. Building the Android App (in Android Studio Ladybug)

### Create a New Android Project
1. Open Android Studio Ladybug.  
2. **Start a new Android Studio project** → “Empty Activity”.  
3. **Language** = Java (or Kotlin, but this guide uses Java).  
4. **Minimum SDK**: choose something that covers your test device/emulator.  
5. **Finish** to create the project.

### Add the Firebase SDK and Configuration Files
1. Place the `google-services.json` file you downloaded earlier into the **app** folder.  
2. Open your top-level `build.gradle` (Project: *YourProjectName*). In the `dependencies` section or `plugins` block, add:
   ```groovy
   buildscript {
       dependencies {
           // ...
           classpath 'com.google.gms:google-services:4.3.15'
       }
   }
   ```
   or in newer Gradle versions:
   ```groovy
   plugins {
       id 'com.android.application' version 'X.Y.Z' apply false
       id 'com.google.gms.google-services' version '4.3.15' apply false
       // ...
   }
   ```
3. Open **Module-level** `build.gradle` (usually `app/build.gradle`), add:
   ```groovy
   plugins {
       id 'com.android.application'
       id 'com.google.gms.google-services'
       // ...
   }

   dependencies {
       implementation platform('com.google.firebase:firebase-bom:32.3.1')
       implementation 'com.google.firebase:firebase-messaging:23.2.1'
       // The rest of your dependencies
   }

   // At the bottom, ensure the apply plugin statement is there if needed:
   // apply plugin: 'com.google.gms.google-services'
   ```
4. **Sync** your Gradle files.

### Add Dependencies to `build.gradle` (Module: app)
Besides FCM, you’ll also need for image handling:
```groovy
dependencies {
    // ...
    implementation 'com.google.firebase:firebase-storage:20.2.1'
    implementation 'com.github.bumptech.glide:glide:4.11.0'
    annotationProcessor 'com.github.bumptech.glide:compiler:4.14.2'
}
```
*(Sync the project again.)*

### Configure Permissions in `AndroidManifest.xml`
In the `<manifest>` tag (but **outside** `<application>`):
```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
```

### Implementing Firebase Messaging Services

#### 1. Create a Service to Retrieve Tokens
Create `FireIDService.java` (or similar):
```java
import android.util.Log;
import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.firebase.messaging.FirebaseMessaging;
import com.google.firebase.messaging.FirebaseMessagingService;

public class FireIDService extends FirebaseMessagingService {
    @Override
    public void onNewToken(String token) {
        super.onNewToken(token);
        Log.d("Not","Token ["+token+"]");
        // You could save the token in shared prefs or send to your server
    }
}
```
*(Note: the older `onTokenRefresh()` is replaced by `onNewToken(String token)` in newer FCM.)*

#### 2. Create a Service to Handle Incoming Messages
Create `FireMsgService.java`:
```java
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import android.util.Log;
import androidx.core.app.NotificationCompat;
import com.google.firebase.messaging.FirebaseMessagingService;
import com.google.firebase.messaging.RemoteMessage;

public class FireMsgService extends FirebaseMessagingService {
    @Override
    public void onMessageReceived(RemoteMessage remoteMessage) {
        super.onMessageReceived(remoteMessage);
        Log.d("Msg", "Message received ["+remoteMessage+"]");

        // Create an Intent to launch MainActivity
        Intent intent = new Intent(this, MainActivity.class);
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP);

        // This is crucial to indicate that an image is available
        intent.putExtra("Image", "Intruder detected");

        PendingIntent pendingIntent = PendingIntent.getActivity(
                this,
                1410,
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_MUTABLE  // If targeting newer APIs
        );

        // Extract info from RemoteMessage
        String info = null;
        if (remoteMessage.getData().size() > 0) {
            info = remoteMessage.getData().get("message");
        }
        if (remoteMessage.getNotification() != null) {
            info = remoteMessage.getNotification().getBody();
        }

        NotificationManager notificationManager =
                (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);

        // For Android O (8.0) and above, you need a notification channel
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                    "mychannel",
                    "mychannel",
                    NotificationManager.IMPORTANCE_HIGH
            );
            notificationManager.createNotificationChannel(channel);

            Notification notification = new Notification.Builder(this, "mychannel")
                    .setContentTitle("Message")
                    .setContentText(info)
                    .setSmallIcon(R.drawable.ic_launcher_background)
                    .setContentIntent(pendingIntent)
                    .setAutoCancel(true)
                    .build();

            notificationManager.notify(1410, notification);
        } else {
            // For older Android versions
            NotificationCompat.Builder notificationBuilder = new NotificationCompat.Builder(this)
                    .setSmallIcon(R.drawable.ic_launcher_background)
                    .setContentTitle("Message")
                    .setContentText(info)
                    .setAutoCancel(true)
                    .setContentIntent(pendingIntent);

            notificationManager.notify(1410, notificationBuilder.build());
        }
    }
}
```

#### 3. Register Services in `AndroidManifest.xml`
Inside the `<application>` tag:
```xml
<service
    android:name=".FireIDService"
    android:exported="true">
    <intent-filter>
        <action android:name="com.google.firebase.INSTANCE_ID_EVENT"/>
    </intent-filter>
</service>

<service
    android:name=".FireMsgService"
    android:exported="true">
    <intent-filter>
        <action android:name="com.google.firebase.MESSAGING_EVENT"/>
    </intent-filter>
</service>

<!-- Default notification metadata -->
<meta-data
    android:name="com.google.firebase.messaging.default_notification_icon"
    android:resource="@drawable/ic_launcher_background"/>
<meta-data
    android:name="com.google.firebase.messaging.default_notification_color"
    android:resource="@android:color/holo_purple"/>
```

### Creating the App UI (`activity_main.xml`)
For simplicity, an example layout:
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
        android:id="@+id/textView2"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="TextView"
        android:textSize="20sp"
        android:textColor="@color/purple_200"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent" />

    <ImageView
        android:id="@+id/imageView"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:src="@drawable/ic_launcher_foreground"
        app:layout_constraintTop_toBottomOf="@+id/textView2"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent" />

    <TextView
        android:id="@+id/textView3"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="TextView"
        android:textSize="20sp"
        android:textColor="@color/purple_200"
        app:layout_constraintTop_toBottomOf="@+id/imageView"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent" />

    <WebView
        android:id="@+id/webView"
        android:layout_width="0dp"
        android:layout_height="0dp"
        app:layout_constraintTop_toBottomOf="@+id/textView3"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintBottom_toTopOf="@+id/textView" />

    <TextView
        android:id="@+id/textView"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="TextView"
        android:textSize="20sp"
        android:textColor="@color/purple_200"
        app:layout_constraintBottom_toTopOf="@+id/button"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent" />

    <Button
        android:id="@+id/button"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Subscribe"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>
```

*(Adjust constraints as needed. This layout has a button, two text views, an image view, and a web view.)*

### MainActivity Logic to Subscribe and Display Images

#### 1. Fields in `MainActivity.java`
```java
public class MainActivity extends AppCompatActivity {
    ImageView imageView;
    TextView textView;
    TextView textView2;  // etc. if needed
    WebView webView;
    Uri imguri;
    ProgressDialog progressDialog;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        // Bind UI
        Button but1 = findViewById(R.id.button);
        imageView = findViewById(R.id.imageView);
        textView = findViewById(R.id.textView);
        textView2 = findViewById(R.id.textView2);
        TextView textView3 = findViewById(R.id.textView3);
        webView = findViewById(R.id.webView);

        textView.setText("");
        textView2.setText("");
        textView3.setText("");

        // If launched via notification: check intent extras
        if (getIntent().hasExtra("Image")) {
            // Means we have an intruder alert
            // Initialize Firebase Storage
            FirebaseStorage storage = FirebaseStorage.getInstance();
            StorageReference storageRef = storage.getReference();
            
            // Show a progress dialog while downloading
            progressDialog = new ProgressDialog(this);
            progressDialog.setTitle("Downloading image...");
            progressDialog.show();

            storageRef.child("image.png").getDownloadUrl()
                .addOnSuccessListener(new OnSuccessListener<Uri>() {
                    @Override
                    public void onSuccess(Uri uri) {
                        imguri = uri;
                        progressDialog.dismiss();
                        textView.setText("Click here to open the image in browser");
                        textView2.setText("Intruder photo:");
                        textView3.setText("Intruder bigger photo in WebView:");

                        // Load image via Glide
                        DisplayMetrics metrics = new DisplayMetrics();
                        getWindowManager().getDefaultDisplay().getMetrics(metrics);

                        Glide.with(getApplicationContext())
                                .load(imguri)
                                .override(metrics.widthPixels, metrics.heightPixels)
                                .into(imageView);

                        // Load image into WebView
                        webView.loadUrl(uri.toString());
                    }
                })
                .addOnFailureListener(new OnFailureListener() {
                    @Override
                    public void onFailure(@NonNull Exception e) {
                        progressDialog.dismiss();
                        Log.e("MainActivity", "Failed to load image from Firebase", e);
                    }
                });
        } else {
            // App opened normally (no PIR event triggered)
        }

        // Clicking textView -> open in default browser
        textView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if (imguri != null) {
                    Intent intent = new Intent(Intent.ACTION_VIEW, imguri);
                    // In some emulators, must use chooser
                    startActivity(Intent.createChooser(intent, "Browse with"));
                }
            }
        });

        // Subscribe button
        but1.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                FirebaseMessaging.getInstance().subscribeToTopic("alarm");
                FirebaseMessaging.getInstance().getToken()
                    .addOnCompleteListener(new OnCompleteListener<String>() {
                        @Override
                        public void onComplete(@NonNull Task<String> task) {
                            if (!task.isSuccessful()) {
                                Log.w("MainActivity", "Fetching FCM registration token failed", task.getException());
                                return;
                            }
                            // Get new FCM registration token
                            String token = task.getResult();
                            Toast.makeText(MainActivity.this,
                                    "Subscribed to alarm channel. Token: " + token,
                                    Toast.LENGTH_SHORT).show();
                            Log.d("MainActivity", "Token: " + token);
                        }
                    });
            }
        });
    }
}
```

### Testing the Android App
1. **Run/Debug** on a physical device or emulator with Google APIs.  
2. If using a real device, enable **USB debugging** in Developer Options.  
3. Install the app on the device.  
4. Tap **Subscribe** to subscribe to the “alarm” topic.  
5. Check **Logcat** for any token messages or subscription success messages.  
6. Confirm that your device can receive notifications:
   - *For Android 13+*, system-level notification permissions must be granted manually in Settings → Apps → YourApp → Notifications.

---

## 7. Final Integration and Testing

1. **Launch the Raspberry Pi script** and the Android app (subscribe on Android).  
2. Walk in front of the PIR sensor or wave your hand—motion is detected:  
   - The Pi script captures `image.png`.  
   - The Pi uploads it to Firebase Storage.  
   - The Pi sends a push notification via Firebase Cloud Messaging.  
3. After a short delay, your phone gets a push notification:  
   - The notification includes the text “Alarm! Someone is at home!” (or similar).  
4. Tap on the notification:  
   - The Android app opens (`MainActivity`), sees `"Image"` extra in the intent, and begins downloading the photo from Storage.  
   - A progress dialog is displayed (e.g., “Downloading image…”).  
   - The image appears in an `ImageView` and a `WebView`. A `TextView` also offers a link to view the image in the device’s default browser.  

---

## 8. Troubleshooting

1. **No notifications?**  
   - Make sure the device is subscribed (`subscribeToTopic("alarm")`).  
   - Check if your Android device has allowed notifications from your app (Settings → Apps → [Your App] → Notifications).  
   - Verify the Pi code logs “Message sent to Firebase for delivery” with a 200 status.  
   - If you’re on Android 13+, you must grant notification permission in the phone’s settings.  

2. **Image not loading in the app?**  
   - Check if the rules in Firebase Storage are set to allow read/write in test mode.  
   - Confirm the file is named exactly `"image.png"` in both Pi code and in `storageRef.child("image.png")` in the Android code.  
   - Check that your app has internet permission and your device/emulator actually has network access.  

3. **Slow image loading in emulator**  
   - Emulators sometimes have slower network performance. On a real device, the image typically loads faster.  

4. **Service account key issues**  
   - Ensure `service-account.json` on the Pi matches the Firebase project.  
   - If using HTTP v1 for FCM, confirm the `PROJECT_ID` is correct and the OAuth scopes are set properly.  

5. **Crashes on older devices**  
   - Adjust your `minSdkVersion` or test on a relevant emulator if you need older compatibility.  
   - Check for AndroidX vs. Support libraries mismatches in your `FireMsgService`.  

---

# Congratulations!
You’ve successfully set up a **Home Invasion Detection System** that leverages a Raspberry Pi with a PIR sensor and camera, along with Firebase Cloud Messaging and Firebase Storage, and an Android companion app built in Android Studio Ladybug (or similar versions). 

This project can be further customized for additional features such as:
- **Multiple camera captures** or short videos.  
- **More secure Firebase Rules**.  
- **SMS/Email alerts**.  
- **Integration with other IoT devices** (lights, locks, etc.).

Enjoy building and enhancing your smart home project!