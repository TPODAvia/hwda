package com.example.weathermqttapp;

import androidx.appcompat.app.AppCompatActivity;
import androidx.fragment.app.Fragment;
import androidx.fragment.app.FragmentManager;

import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;

import org.eclipse.paho.android.service.MqttAndroidClient;
import org.eclipse.paho.client.mqttv3.IMqttActionListener;
import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.IMqttToken;
import org.eclipse.paho.client.mqttv3.MqttCallback;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;

public class MainActivity extends AppCompatActivity {

    private static final String TAG = "MainActivity";

    /**
     * 1) Replace <LaptopHotspotIP> with the actual IP address your laptop uses when hosting the hotspot.
     * 2) Replace 1883 with the port of your MQTT broker if it’s different.
     */
    private static final String MQTT_BROKER_URL = "tcp://192.168.223.50:1883";

    private static final String MQTT_TOPIC = "weather/data";

    private MqttAndroidClient mqttAndroidClient;

    // Fragments
    private HourlyFragment hourlyFragment;
    private DailyFragment dailyFragment;
    private PredictionFragment predictionFragment;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Create our fragments
        hourlyFragment = new HourlyFragment();
        dailyFragment = new DailyFragment();
        predictionFragment = new PredictionFragment();

        // Display Hourly fragment by default
        replaceFragment(hourlyFragment);

        // Set up navigation buttons
        Button btnHourly = findViewById(R.id.btnHourly);
        Button btnDaily = findViewById(R.id.btnDaily);
        Button btnPrediction = findViewById(R.id.btnPrediction);

        btnHourly.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                replaceFragment(hourlyFragment);
            }
        });

        btnDaily.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                replaceFragment(dailyFragment);
            }
        });

        btnPrediction.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                replaceFragment(predictionFragment);
            }
        });

        // Build the MQTT client
        String clientId = "AndroidClient_" + System.currentTimeMillis();
        mqttAndroidClient = new MqttAndroidClient(
                getApplicationContext(),
                MQTT_BROKER_URL,
                clientId
        );

        // Connect to MQTT broker
        connectMQTTBroker();
    }

    private void connectMQTTBroker() {
        try {
            IMqttToken token = mqttAndroidClient.connect();
            token.setActionCallback(new IMqttActionListener() {
                @Override
                public void onSuccess(IMqttToken asyncActionToken) {
                    Log.d(TAG, "Connected to MQTT broker");
                    subscribeToTopic();
                }

                @Override
                public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
                    Log.e(TAG, "Failed to connect to MQTT broker", exception);
                }
            });
        } catch (MqttException e) {
            e.printStackTrace();
        }

        // Callback for receiving messages
        mqttAndroidClient.setCallback(new MqttCallback() {
            @Override
            public void connectionLost(Throwable cause) {
                Log.e(TAG, "MQTT connection lost!", cause);
            }

            @Override
            public void messageArrived(String topic, MqttMessage message) {
                String payload = new String(message.getPayload());
                Log.d(TAG, "Message arrived on topic: " + topic + "\nPayload:\n" + payload);

                // Make sure we handle UI updates on the main thread
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        // Each fragment will parse the JSON chunk it needs
                        hourlyFragment.updateData(payload);
                        dailyFragment.updateData(payload);
                        predictionFragment.updateData(payload);
                    }
                });
            }

            @Override
            public void deliveryComplete(IMqttDeliveryToken token) {
                // Not used in this subscriber-only scenario
            }
        });
    }

    private void subscribeToTopic() {
        try {
            mqttAndroidClient.subscribe(MQTT_TOPIC, 0);
            Log.d(TAG, "Subscribed to topic: " + MQTT_TOPIC);
        } catch (MqttException e) {
            Log.e(TAG, "Exception subscribing to topic!", e);
        }
    }

    private void replaceFragment(Fragment fragment) {
        FragmentManager manager = getSupportFragmentManager();
        manager.beginTransaction()
                .replace(R.id.fragment_container, fragment)
                .commit();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        // Gracefully disconnect & close the client to avoid resource leaks
        try {
            if (mqttAndroidClient != null) {
                mqttAndroidClient.disconnect();
                mqttAndroidClient.close();
            }
        } catch (MqttException e) {
            e.printStackTrace();
        }
    }
}
