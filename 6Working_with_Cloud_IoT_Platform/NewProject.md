Let's create a new project in Android Studio. Select Empty Activity (AS Electric Eel) or Empty Views Activity (AS
Koala/Ladybug) and Java language.
The application interface will be simple and straightforward - just 2 TextView elements in the center of the
screen. You can also add a toolbar containing an additional TextView with the application name if the toolbar
is missing by default when the application is launched. An example of the interface is shown in Figure 126.
Figure 126 – Example of a mobile application interface
In order for the app to work, there are a few things that need to be taken into account. First, the app will be
accessing the ThingSpeak channel over the internet, so you need to add the line
<uses-permission android:name="android.permission.INTERNET"/>
to the AndroidManifest.xml manifest file. Then, we will use the same Volley HTTP request library, so we need
to add the dependency to the build.gradle (Module) file:
implementation 'com.android.volley:volley:1.2.1'
and then sync the project. Finally, you need to write the necessary code in MainActivity.java, which can be
extracted in parts from the previous Android mobile application in this project:
115
package com.example.iotsixthtschannelread; //your package name here
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
 private static final String THINGSPEAK_URL =
"https://api.thingspeak.com/channels/2285639/feeds.json?api_key=1RPXPUMQHZU0ZYYE&r
esults=1"; //your read api key and channel 2 id here
 private String response1;
 private static String DEVICE_ID = "3c1e4c0b24f645258400e6e553bcc817";
 private static String TOKEN = "04b92cb5070f48aba72f1e030325c6f9";
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
 textforecast.setText("wait for it....");
 initScheduler();
 }
 private void initScheduler() {
 ScheduledExecutorService scheduler =
 Executors.newSingleThreadScheduledExecutor();
 scheduler.scheduleWithFixedDelay(new Runnable() {
 @Override
 public void run() {
 //Log.d(TAG, "Scheduler running...");
 // call ThingSpeak
queue = Volley.newRequestQueue(MainActivity.this);
 StringRequest request1 = new StringRequest(Request.Method.GET,
 THINGSPEAK_URL,
new Response.Listener<String>() {
 @Override
public void onResponse(String response) {
 response1 = response;
try {
 JSONObject obj = new JSONObject(response1);
 JSONArray feeds = obj.getJSONArray("feeds");
 JSONObject obj1 = feeds.getJSONObject(0);
116
 String thetime = obj1.getString("created_at");
 String theforecast = obj1.getString("field1");
 textdate.setText(thetime);
 textforecast.setText(theforecast);
 }
 catch(JSONException jse) {
 jse.printStackTrace();
 }
Log.d("iotsixthtschannelread", "Response [" +
response + "]");
 }
 },
new Response.ErrorListener() {
 @Override
public void onErrorResponse(VolleyError error) {
 error.printStackTrace();
 }
 });
 queue.add(request1);
 }
 }, 10, 60, TimeUnit.SECONDS);
 }
}
Note that it takes some effort to extract the desired values from the JSON structure shown in Figure 125!
Now we can run the application from the previous project, i.e. the Arduino application, the MQTT service on
the Mosquitto raspberry with a subscription to the topic channel1, the first mobile application in this project
and the second application that we have just made, if we open it in a separate Android Studio project. Thus, in
fact, we will have 5 applications running simultaneously (if we consider the mosquitto MQTT service on the
raspberry to be an application): after all, we also have a MATLAB script running in the ThingSpeak cloud, which
generates a weather forecast every 5 minutes and sends it to the second channel based on pressure readings.
As a result, according to the code, the first mobile application of this project will stream data to ThingSpeak,
and the second one will receive them from the second cloud channel and display them on the screen, updating
the weather forecast every 5 minutes, see Figure 127. And this time, the second mobile application will work
from any network, from anywhere, since it accesses the ThingSpeak cloud.