package com.example.remoteweatherstation;

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
            "https://api.thingspeak.com/update?api_key=IDQIIBQKAD6FQGPI";

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

