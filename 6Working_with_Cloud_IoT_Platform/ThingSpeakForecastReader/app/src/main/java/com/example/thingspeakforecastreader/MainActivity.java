package com.example.thingspeakforecastreader;

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
            "https://api.thingspeak.com/channels/2285639/feeds.json?api_key=9KH02T33NWPOTZSW&results=1";

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
