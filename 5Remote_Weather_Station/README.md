sudo journalctl -u mosquitto

Write a step by step how to write app in Android Studio and raspberry to subscriibe to http and print out in GUI

5) It’s time to take care of the Raspberry Pi OS application. But first, let’s make a mobile application in Android
Studio. Let’s start as usual. Create a new project in Android Studio. Give the project a name, for example –
Remote Weather Station. In the next window, select the Phone and Tablet template. In the next window,
select Empty Views Activity, give the activity a name, then click Next and Finish.
Before the application tag in the AndroidManifest.xml file, add a couple of permissions without which the
application will not work:
<uses-permission android:name="android.permission.WAKE_LOCK" />
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
<uses-permission android:name="android.permission.READ_PHONE_STATE" />
86
After the closing </activity> tag, add the service:
<service android:name="org.eclipse.paho.android.service.MqttService" >
</service>
Additionally, we need to add dependencies to the build.gradle file (Module) and then sync the project (Sync
Now):
implementation 'org.eclipse.paho:org.eclipse.paho.client.mqttv3:1.2.5'
implementation 'org.eclipse.paho:org.eclipse.paho.android.service:1.1.1'
Let's create the application interface. Let's go to the res/layout folder and create the interface for our
application in the activity_main.xml file using ConstraintLayout.
The code for the activity_main.xml file could be like this:
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
 android:layout_marginStart="8dp"
 android:layout_marginEnd="8dp"
 android:layout_marginBottom="32dp"
 android:text="Hello World!"
 android:textColor="@android:color/holo_green_dark"
 android:textSize="24sp"
 app:layout_constraintBottom_toTopOf="@+id/press"
 app:layout_constraintEnd_toEndOf="parent"
 app:layout_constraintHorizontal_bias="0.498"
 app:layout_constraintLeft_toLeftOf="parent"
 app:layout_constraintRight_toRightOf="parent"
 app:layout_constraintStart_toStartOf="parent" />
 <TextView
 android:id="@+id/press"
 android:layout_width="wrap_content"
 android:layout_height="wrap_content"
 android:layout_marginStart="8dp"
 android:layout_marginEnd="8dp"
 android:text="TextView"
 android:textColor="@android:color/holo_purple"
 android:textSize="24sp"
 app:layout_constraintBottom_toBottomOf="parent"
 app:layout_constraintEnd_toEndOf="parent"
 app:layout_constraintStart_toStartOf="parent"
 app:layout_constraintTop_toTopOf="parent" />
 <TextView
 android:id="@+id/lux"
 android:layout_width="wrap_content"
 android:layout_height="wrap_content"
87
 android:layout_marginStart="8dp"
 android:layout_marginTop="32dp"
 android:layout_marginEnd="8dp"
 android:inputType="textMultiLine"
 android:text="TextView"
 android:textAlignment="center"
 android:textColor="@android:color/holo_orange_dark"
 android:textSize="24sp"
 app:layout_constraintEnd_toEndOf="parent"
 app:layout_constraintStart_toStartOf="parent"
 app:layout_constraintTop_toBottomOf="@+id/hum" />
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
 android:minHeight="?attr/actionBarSize"
 android:theme="?attr/actionBarTheme"
 app:layout_constraintEnd_toEndOf="parent"
 app:layout_constraintStart_toStartOf="parent"
 app:layout_constraintTop_toTopOf="parent" />
 <TextView
 android:id="@+id/textView"
 android:layout_width="wrap_content"
 android:layout_height="wrap_content"
 android:text="@string/app_title"
 android:textColor="@color/white"
 android:textSize="24sp"
 app:layout_constraintBottom_toBottomOf="@+id/toolbar"
 app:layout_constraintEnd_toEndOf="parent"
 app:layout_constraintStart_toStartOf="parent"
 app:layout_constraintTop_toTopOf="@+id/toolbar" />
</androidx.constraintlayout.widget.ConstraintLayout>
In this case, you need to add one line to the string.xml file in the res->values folder:
88
<string name="app_title">Remote Weather Station</string>
Let's move on to the application code. We will need 2 classes: the first one is, as usual, MainActivity.java, and
the second one will be needed for the MQTT client to work and will be called MQTTClient.java.
The first class creates a connection with the interface and displays data from the sensors in the application
interface; works with parsing messages in JSON format - extracts from them the message that came to the
mosquito server, and displays the necessary data in the application interface, and for lighting, it also makes a
conclusion according to the formula depending on the sensor readings (MainActivity.java):
package com.example.iotesixthmobile; //change to your package
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
 private String topicstr;
 @Override
 protected void onCreate(Bundle savedInstanceState) {
 super.onCreate(savedInstanceState);
 setContentView(R.layout.activity_main);
 topicstr = "channel1";
 Log.d(TAG, "onCreate");
 initView();
 initMQTT();
 }
 @Override
 protected void onDestroy() {
 super.onDestroy();
 Log.d(TAG, "onDestroy");
 }
 @Override
 public void onConnected() {
 mqttClient.subscribe(topicstr);
 }
 @Override
 public void onConnectionFailure(Throwable t) {
 }
 @Override
89
 public void onMessage(String topic, MqttMessage message) {
 // Parse the payload
 Log.d(TAG, "Parsing message...");
 String payload = new String(message.getPayload());
 Log.d(TAG, "Payload ["+payload+"]");
 try {
 JSONObject obj = new JSONObject(payload);
 String temp = obj.getString("t");
 String press = obj.getString("p");
 String hum = obj.getString("h");
 String lux = obj.optString("l");
 updateView(topic, temp, press, hum, lux);
 }
 catch(JSONException jse) {
 jse.printStackTrace();
 }
 }
 @Override
 public void onError(MqttException mqe) {
 }
 private void initMQTT() {
 mqttClient = MQTTClient.getInstance(this);
 mqttClient.setListener(this);
 mqttClient.connectToMQTT(MQTTClient.MQTT_SERVER);
 }
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
 private void updateView(String topic, String temp, String press, String hum,
String lux) {
 chView.setText("Topic: " + topic);
 tempView.setText("Temperature: " + temp + " C");
 pressView.setText("Pressure: " + press + " mmHg");
 humView.setText("Humidity: "+ hum + " %");
 if (Integer.valueOf(lux)*5/1024>=0 && Integer.valueOf(lux)*5/1024<=0.4) {
 luxView.setText("Illumination: " +
String.valueOf(Integer.valueOf(lux)*5/1024) + ". It is light. Resistance value is
" + String.valueOf(Integer.valueOf(lux)));
 } else if (Integer.valueOf(lux)*5/1024>0.4 &&
Integer.valueOf(lux)*5/1024<=2) {
 luxView.setText("Illumination: " +
String.valueOf(Integer.valueOf(lux)*5/1024) + ". It is bright. Resistance value is
" + String.valueOf(Integer.valueOf(lux)));
 } else {
 luxView.setText("Illumination: " +
String.valueOf(Integer.valueOf(lux)*5/1024) + ". It is dark. Resistance value is "
+ String.valueOf(Integer.valueOf(lux)));
 }
 }
}
90
The second class contains the methods needed to connect to the MQTT server, subscribe to a channel, and do
other work with Mosquitto; it contains the IP address and port of the mosquito raspberry, which need to be
replaced with your own (MQTTClient.java):
package com.example.iotesixthmobile; // change to your package
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
 public static final String MQTT_SERVER = "tcp://192.168.1.106:1883";// change
to your mosquito raspberry pi IP
 private static MQTTClient me;
 private Context ctx;
 private MQTTListener listener;
 private MqttAndroidClient mqttClient;
 private MQTTClient(Context ctx) {
 this.ctx = ctx;
 }
 public static final MQTTClient getInstance(MainActivity ctx) {
 if (me == null)
 me = new MQTTClient(ctx);
 return me;
 }
 public void setListener(MQTTListener listener) {
 this.listener = listener;
 }
 public void connectToMQTT(String server) {
 Log.d(TAG, "Connecting to MQTT Server..");
 String clientId = MqttClient.generateClientId();
 Log.d(TAG, "Client Id ["+clientId+"]");
 mqttClient = new MqttAndroidClient(ctx, server, clientId);
 mqttClient.setCallback(this);
 try {
 IMqttToken mqttToken = mqttClient.connect();
 mqttToken.setActionCallback(new IMqttActionListener() {
 @Override
 public void onSuccess(IMqttToken asyncActionToken) {
 Log.i(TAG, "Connected to MQTT server");
 listener.onConnected();
 }
91
 @Override
 public void onFailure(IMqttToken asyncActionToken, Throwable
exception) {
 Log.e(TAG, "Failure");
 exception.printStackTrace();
listener.onConnectionFailure(exception);
 }
 });
 }
 catch (MqttException mqe) {
 Log.e(TAG, "Unable to connect to MQTT Server");
 mqe.printStackTrace();
 listener.onError(mqe);
 }
 }
 public void subscribe(final String topic) {
 try {
 IMqttToken subToken = mqttClient.subscribe(topic, 1);
 subToken.setActionCallback(new IMqttActionListener() {
 @Override
 public void onSuccess(IMqttToken asyncActionToken) {
 Log.d(TAG, "Subscribed to topic ["+topic+"]");
 }
 @Override
 public void onFailure(IMqttToken asyncActionToken,
 Throwable exception) {
 Log.e(TAG, "Error while subscribing to the topic
["+topic+"]");
 exception.printStackTrace();
 }
 });
 } catch (MqttException e) {
 e.printStackTrace();
 }
 }
 @Override
 public void connectionLost(Throwable cause) {
 }
 @Override
 public void messageArrived(String topic, MqttMessage message) throws Exception
{
 Log.d(TAG, "Message arrived...");
 String payload = new String(message.getPayload());
 Log.d(TAG, "Payload ["+payload+"]");
 listener.onMessage(topic, message);
 }
 @Override
 public void deliveryComplete(IMqttDeliveryToken token) {
 }
 public interface MQTTListener {
 public void onConnected();
 public void onConnectionFailure(Throwable t);
 public void onMessage(String topic, MqttMessage message);
 public void onError(MqttException mqe);
 }
92
}
Next, we need to make sure that the app-level build.gradle (Module:app) file has targetSdk 30. This is because
the paho library has not been updated for a long time and does not have the necessary code to support API
version 35, 34 or even 31 for Android. However, everything will work fine with versions below API 31. If you
know of a more recent MQTT library for Android, you can use it instead of paho.
If we run the application, we will see... oops, we won't see anything again. There is a mysterious line:
android.enableJetifier=true
Add it to the gradle scripts -> gradle.properties (Project Properties) file. And now the sensor data and topic
name are in the mobile application interface, as shown in Figure 109.
If we open LogCat in Android Studio, we will see approximately the same thing after the Message arrived… line
and in the Payload [] line that we see in the terminal on the mosquito raspberry - i.e. data from sensors in
JSON format:
D/MQTTClient: Connecting to MQTT Server..
D/MQTTClient: Client Id [paho202695882161]
D/vndksupport: Loading /vendor/lib/hw/android.hardware.graphics.mapper@2.0-impl.so
from current namespace instead of sphal namespace.
D/AlarmPingSender: Register alarmreceiver to
MqttServiceMqttService.pingSender.paho202695882161
D/AlarmPingSender: Schedule next alarm at 1633631075021
D/AlarmPingSender: Alarm scheule using setExactAndAllowWhileIdle, next: 60000
I/MQTTClient: Connected to MQTT server
D/MQTTClient: Subscribed to topic [channel1]
D/MQTTClient: Message arrived...
 Payload [{"t":"25", "h":"15", "p":"766", "l":"278"}]
D/MainActivity: Parsing message...
 Payload [{"t":"25", "h":"15", "p":"766", "l":"278"}]
D/MQTTClient: Message arrived...
 Payload [{"t":"25", "h":"15", "p":"766", "l":"270"}]
D/MainActivity: Parsing message...
 Payload [{"t":"25", "h":"15", "p":"766", "l":"270"}]
Yes, and you can additionally add 2 EditText elements to this application, with which you can manually type
the topic and IP address of the desired mosquito server, and read data not only from your sensors! And - yes,
for this project, you again need to connect all devices to a single portable hotspot, distributed, for example,
from a smartphone, so that they are on the same network, otherwise something may not work, see the notes
in the previous project.
6) You, of course, already guess that this is not enough for us, and that this time we missed something big and
important... an application for Raspberry! It can be written either on a separate Raspberry or on a mosquito
Raspberry, so in fact, we do not really need 2 Raspberries in this project. I want you to write the Raspberry
application yourself this time, having suffered with the interface in Python, as I did before. This will also be a
ten mark task for this project! 
Hint: you can use the third project as a template for the interface and code: we do not interact with the
interface elements, the application simply shows us the data from the sensors, as there, and the name of the
93
topic we subscribed to. In general, the interface and code of this application are very similar to the interface
and code of the mobile application.

The third project look like this:
import PySimpleGUI as sg
import RPi.GPIO as GPIO
from time import sleep
import smbus2
import bme280

port = 1
address = 0x76
bus = smbus2.SMBus(port)
calibration_params = bme280.load_calibration_params(bus, address)

lvl1 = 1022.69 #Паскалей, или 767.2 мм.рт.ст.
lvl2 = 1009.14 #Паскалей, или 756.92 мм.рт.ст.
tempmeltinglvl = 30

layout = [[sg.Text('temperature:', size=(None, None), key='-temp-', auto_size_text=True, pad=((5,5),(200,0)), expand_x=True, font=('Calibri', 48), text_color = 'green', justification='center')],
[sg.Text('pressure:', size=(None, None), key='-press-', auto_size_text=True, pad=((5,5),(0,0)), expand_x=True, font=('Calibri', 48), text_color = 'violet', justification='center')],
[sg.Text('weather:', size=(None, None), key='-weather-', auto_size_text=True, pad=((5,5),(0,0)), expand_x=True, font=('Calibri', 48), text_color = 'orange', justification='center')]]

window = sg.Window('Temperature+Humidity+Pressure Sensor', layout, size=(1280,800), finalize=True)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD) #по простому номеру пина, от 1 до 40 
GPIO.setup(31, GPIO.OUT, initial=GPIO.LOW) #red led
GPIO.setup(35, GPIO.OUT, initial=GPIO.LOW) #green led
GPIO.setup(37, GPIO.OUT, initial=GPIO.LOW) #blue led
GPIO.setup(29, GPIO.OUT, initial=GPIO.LOW) #red alarm led

try:
    while True:
        #считываем данные
        data = bme280.sample(bus, address, calibration_params)
        #отображаем их в интерфейсе 
        window['-temp-'].update('temperature: ' + str(round(data.temperature)) + ' C')
        window['-press-'].update('pressure: ' + str(round(data.pressure)) + ' mb')
        #и на светодиодах
        if data.temperature >= tempmeltinglvl:
            GPIO.output(29, GPIO.HIGH)
            print('HOT')   
        else:
            GPIO.output(29, GPIO.LOW)
        if data.pressure >= lvl1:
            weather_forecast = 'the weather will be stable'
            #красный + зелёный = жёлтый
            GPIO.output(31, GPIO.HIGH)
            GPIO.output(35, GPIO.HIGH)
            GPIO.output(37, GPIO.LOW)
        elif data.pressure >= lvl2 and data.pressure < lvl1:
            weather_forecast = 'the weather will be cloudy'
            #белый для облачной погоды, облака белые обычно
            GPIO.output(31, GPIO.HIGH)
            GPIO.output(35, GPIO.HIGH)
            GPIO.output(37, GPIO.HIGH)
        else:
            weather_forecast = 'the weather will be rainy'
            #синий для дождливой погоды
            GPIO.output(31, GPIO.LOW)
            GPIO.output(35, GPIO.LOW)
            GPIO.output(37, GPIO.HIGH)
        window['-weather-'].update('weather: ' + weather_forecast)
        window.refresh()
        #и в консоли
        print(data.temperature)
        print(data.pressure)
        print(weather_forecast)
        sleep(1)

except Exception as E:
    print(f'** Error {E} **')
    pass
        
# закрываем окно и освобождаем используемые ресурсы
window.close()
GPIO.cleanup()

