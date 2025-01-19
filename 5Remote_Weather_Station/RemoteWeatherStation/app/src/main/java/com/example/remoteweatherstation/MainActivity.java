package com.example.remoteweatherstation;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import android.widget.TextView;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.json.JSONException;
import org.json.JSONObject;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

public class MainActivity extends Activity implements MQTTClient.MQTTListener {


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
        initScheduler(); // Start the periodic averaging & cloud sending
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
            totalLux += luxValue;
            luxCounter++;
        } catch (NumberFormatException e) {
            luxView.setText("Illumination: N/A");
        }

        // Accumulate totals for valid numeric values
        try {
            totalTemp += Double.parseDouble(temp);
            tempCounter++;
        } catch (NumberFormatException e) {
            Log.w(TAG, "Invalid temperature value: " + temp);
        }

        try {
            totalPress += Double.parseDouble(press);
            pressCounter++;
        } catch (NumberFormatException e) {
            Log.w(TAG, "Invalid pressure value: " + press);
        }

        try {
            totalHum += Double.parseDouble(hum);
            humCounter++;
        } catch (NumberFormatException e) {
            Log.w(TAG, "Invalid humidity value: " + hum);
        }
    }
    private void initScheduler() {
        ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();
        scheduler.scheduleWithFixedDelay(new Runnable() {
            @Override
            public void run() {
                // Safely calculate averages only if counters are non-zero
                double mTemp = (tempCounter > 0) ? totalTemp / tempCounter : 0;
                double mPress = (pressCounter > 0) ? totalPress / pressCounter : 0;
                double mHum = (humCounter > 0) ? totalHum / humCounter : 0;
                double mLux = (luxCounter > 0) ? totalLux / luxCounter : 0;

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

                Log.d(TAG, String.format("Data sent to ThingSpeak: Temp=%.2f, Press=%.2f, Hum=%.2f, Lux=%.2f",
                        mTemp, mPress, mHum, mLux));
            }
        }, 30, TIMEOUT, TimeUnit.SECONDS);
        // First run after 30 seconds, repeated every TIMEOUT seconds
    }
}
