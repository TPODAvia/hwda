2) Now we need to modify our project that we developed in the previous task, because we need to add cloud
capabilities. It would be logical to add cloud capabilities directly to the raspberry app from the previous
project, but then I would have to reveal the code for it here, as I usually do, and you should have written this
code yourself, using, for example, the paho library for the MQTT client. Therefore, we better modify the
mobile application written in Android Studio in Java. It is similar to the raspberry application, because it does
the same thing - listens to the topic to which it is subscribed, and displays the data in the interface received
from the mosquito raspberry.
We can use both Android HTTP library and a custom library to handle HTTP connections. In this project, we will
use the Volley library (https://google.github.io/volley/). This library is widely used and offers interesting
features. It also simplifies HTTP connection management.
Open the Android Studio project for the mobile app from the previous project, find the build.gradle(Module)
file in it and add the following line to the dependencies section:
implementation 'com.android.volley:volley:1.2.1'
99
Open the Android Studio project for the mobile app Add the following line to the AndroidManifest.xml file to
allow internet access through the app (if it is not already there):
<uses-permission android:name="android.permission.INTERNET" />
Now let's create a new class ThingSpeakClient.java in the folder java -> packagename (in my case the package
name is site.makse.iote5test) to handle all the details of the message exchange. Here we will need the
previously remembered URL link for the GET request and its 4 continuations for sending data from the sensor
to the corresponding fields of the previously created channel:
public class ThingSpeakClient {
private static ThingSpeakClient me;
private Context ctx;
private RequestQueue queue;
private static final String THINGSPEAK_URL =
"https://api.thingspeak.com/update?api_key=<your_api_key>";
private String tempdata = "&field1=";
private String humdata = "&field2=";
private String pressdata = "&field3=";
private String lightdata = "&field4=";
private String deviceId;
private String token;
private String TAG = "ThingSpeakClient";
 private ThingSpeakClient (Context ctx, String deviceId, String token) {
 this.ctx = ctx;
 this.deviceId = deviceId;
 this.token = token;
 createQueue();
 }

}
ThingSpeakClient is a singleton and it takes an Android Context, a device ID and a token parameters (the
device ID and token are not needed in our case, but they are needed if you want to refactor the project to
send data in bulk using JSON). Now we need to create a createQueue() method that initializes the Volley
request queue so that the application can send requests to the ThingSpeak Rest API:
private void createQueue() {
 if (queue == null)
 queue = Volley.newRequestQueue(ctx.getApplicationContext());
}
Add the getInstance method – we'll need it later:
public static final ThingSpeakClient getInstance(Context ctx, String deviceId,
String token) {
 if (me == null)
 me = new ThingSpeakClient(ctx,deviceId,token);
 return me;
}
The next method to add is sendData():
public void sendData(final double temp, final double press, final double hum,
final double lux) {
100
}
This calls the ThingSpeak Rest API using the 4 sensor values passed in. Next, inside the method, we create a
StringRequest instance that represents our HTTP request. Add the following to the sendData() method:
StringRequest request1 = new StringRequest(Request.Method.GET,
 THINGSPEAK_URL+tempdata+temp,
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
 });
StringRequest request2 = new StringRequest(Request.Method.GET,
 THINGSPEAK_URL+humdata+hum,
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
 });
StringRequest request3 = new StringRequest(Request.Method.GET,
 THINGSPEAK_URL+pressdata+press,
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
 });
StringRequest request4 = new StringRequest(Request.Method.GET,
 THINGSPEAK_URL+lightdata+lux,
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
101
 });
So, we transmit all four metrics from the sensor via the required link to the ThingSpeak cloud, or more
precisely, to our channel. After that, we only need to add requests to the queue so that Volley can process
them:
queue.add(request1);
queue.add(request2);
queue.add(request3);
queue.add(request4);
These lines complete the sendData() method.
However, this is all theoretical... in practice, the data does not arrive very well, since only 1 request out of 4 is
processed at a time. Therefore, it is better to change this code, sending all 4 values at the same time, in one
request:
StringRequest request1 = new StringRequest(Request.Method.GET,
 THINGSPEAK_URL+tempdata+temp+humdata+hum+pressdata+press+lightdata+lux,
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
 });
queue.add(request1);
Finally, we need to send data from the Android application. To do this, we need to call the client from the
MainActivity.java class (java -> package name). The easiest way to send data to ThingSpeak is to use its API
every time the sensor reads a new value. This would require almost infinite calls to the ThingSpeak API.
Therefore, in order not to overload ThingSpeak, the best approach is to use a scheduler to send data. With the
help of a scheduler, the Android application sends data at certain time intervals. We can customize the
frequency of sending data, thereby having more influence on the behavior of the application and the
bandwidth that the application consumes.
Add the following variables to the variable declaration section of the MainActivity.java class (the variables
device_id and token are not used in this implementation, so you don't have to change their values):
private static final int TIMEOUT = 30;
private int tempCounter = 0;
private int pressCounter = 0;
private int humCounter = 0;
private int luxCounter = 0;
private double totalTemp;
private double totalPress;
private double totalHum;
102
private double totalLux;
private static String DEVICE_ID = "3c1e4c0b24f645258400e6e553bcc817";
private static String TOKEN = "04b92cb5070f48aba72f1e030325c6f9";
We need to change our code in this class a little bit. First, we need to add variables used in another class
(ThingSpeakClient):
public String temp;
public String press;
public String hum;
public String lux;

Secondly, you need to modify the onMessage method so that the values are written where they should be:
JSONObject obj = new JSONObject(payload);
temp = obj.getString("t");
press = obj.getString("p");
hum = obj.getString("h");
lux = obj.optString("l");
updateView(topic, temp, press, hum, lux);
Then in the updateView method you need to add the following to the end:
totalTemp += Integer.parseInt(temp);
tempCounter++;
totalPress += Integer.parseInt(press);
pressCounter++;
totalHum += Integer.parseInt(hum);
humCounter++;
totalLux += Integer.parseInt(lux);
luxCounter++;
And then add the following method to the MainActivity.java class:
private void initScheduler() {
 ScheduledExecutorService scheduler =
 Executors.newSingleThreadScheduledExecutor();
 scheduler.scheduleWithFixedDelay(new Runnable() {
 @Override
 public void run() {
 //Log.d(TAG, "Scheduler running...");
 double mTemp = totalTemp / tempCounter;
 double mPress = totalPress / pressCounter;
 double mHum = totalHum / humCounter;
 double mLux = totalLux / luxCounter;
 totalTemp = 0;
 totalPress = 0;
 totalHum = 0;
 totalLux = 0;
 tempCounter = 0;
 pressCounter = 0;
 humCounter = 0;
 luxCounter = 0;
 // call ThingSpeak
 ThingSpeakClient.getInstance(MainActivity.this,
 DEVICE_ID, TOKEN).sendData(mTemp, mPress, mHum, mLux);
 }
 }, 30, TIMEOUT, TimeUnit.SECONDS);
}
103
In this class we use SchedulerExecutorService, which runs a specific task all the time with a delay specified in
the TIMEOUT variable, taking into account the TimeUnit time units. The task is defined in the run() method. In
this method, the application performs the following steps: calculate the average temperature for the time
interval between the last time data was sent to ThingSpeak and the current time; calculate the average values
of pressure, light and humidity in the same way; call ThingSpeakClient to send the average values; reset the
total value of the variables and the total counter of received values of temperature, pressure, light and
humidity. And the last step is to call this method to schedule the task: in the onCreate() method, add the
following line at the end:
initScheduler();
