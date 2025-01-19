package com.example.smarthomevoice;

import androidx.appcompat.app.AppCompatActivity;
import android.content.Intent;
import android.os.Bundle;
import android.speech.RecognizerIntent;
import android.speech.tts.TextToSpeech;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.Toast;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

import java.io.IOException;
import java.util.List;
import java.util.Locale;

import static java.lang.Thread.sleep;

public class MainActivity extends AppCompatActivity {

    private TextToSpeech TTS;
    boolean ttsEnabled;
    private OkHttpClient client;
    private static final String baseUrl = "http://192.168.172.122:8000/"; // Pi server IP & port
    String request2raspberry;
    String responsefromraspberry;

    Button button;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        button = findViewById(R.id.button);

        // Initialize OkHttp client
        client = new OkHttpClient();

        // Initialize TTS
        TTS = new TextToSpeech(this, new TextToSpeech.OnInitListener() {
            @Override
            public void onInit(int initStatus) {
                if (initStatus == TextToSpeech.SUCCESS) {
                    TTS.setLanguage(Locale.US);
                    TTS.setPitch(1.3f);
                    TTS.setSpeechRate(0.7f);
                    ttsEnabled = true;
                } else {
                    Toast.makeText(MainActivity.this,
                            "TTS initialization failed", Toast.LENGTH_LONG).show();
                    ttsEnabled = false;
                }
            }
        });

        // Button click: start speech recognition
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
                intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                        RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
                intent.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1);
                intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.ENGLISH);
                intent.putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_MINIMUM_LENGTH_MILLIS,
                        3000L);
                startActivityForResult(intent, 1);
            }
        });
    }

    // Handle results from voice recognition
    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == 1 && resultCode == RESULT_OK) {
            List<String> results = data.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS);
            String spokenText = results.get(0).toLowerCase();
            Toast.makeText(MainActivity.this, spokenText, Toast.LENGTH_LONG).show();

            // Check for sensor data queries
            if (spokenText.contains("temperature")) {
                sendRequest("temperature");
                delay(1);
            }
            if (spokenText.contains("pressure")) {
                sendRequest("pressure");
                delay(1);
            }
            if (spokenText.contains("humidity")) {
                sendRequest("humidity");
                delay(1);
            }
            if (spokenText.contains("sensor data")) {
                sendRequest("temperature");
                delay(1);
                sendRequest("pressure");
                delay(1);
                sendRequest("humidity");
                delay(1);
            }
            if (spokenText.contains("weather")) {
                sendRequest("weather");
                delay(1);
            }

            // Check for light control
            if (spokenText.contains("light")) {
                if (spokenText.contains("switch on") || spokenText.contains("turn on")
                        || spokenText.contains("on")) {
                    // specific color?
                    if (spokenText.contains("color")) {
                        if (spokenText.contains("red")) {
                            setColor("FF0000");
                        } else if (spokenText.contains("green")) {
                            setColor("00FF00");
                        } else if (spokenText.contains("blue")) {
                            setColor("0000FF");
                        } else if (spokenText.contains("yellow")) {
                            setColor("FFFF00");
                        } else if (spokenText.contains("purple")) {
                            setColor("FF00FF");
                        } else if (spokenText.contains("random")) {
                            setColor("random");
                        } else {
                            setColor("FFFFFF");
                        }
                    } else {
                        setColor("FFFFFF"); // default white
                    }
                }
                if (spokenText.contains("switch off") || spokenText.contains("turn off")
                        || spokenText.contains("off")) {
                    setColor("000000");
                }
            }
        }
        super.onActivityResult(requestCode, resultCode, data);
    }

    // Send a request for sensor data
    private void sendRequest(String request) {
        Toast.makeText(MainActivity.this, request, Toast.LENGTH_LONG).show();
        if (!ttsEnabled) return;

        String utteranceId = this.hashCode() + "";
        String url = baseUrl;
        request2raspberry = request;

        Request req1 = new Request.Builder()
                .url(url + request)
                .build();

        client.newCall(req1).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                TTS.speak("There was an error: " + e.toString(),
                        TextToSpeech.QUEUE_ADD, null, utteranceId);
                Log.e("sendRequest", "Error", e);
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                responsefromraspberry = response.body().string();
                switch (request2raspberry) {
                    case "temperature":
                        TTS.speak("Current temperature is " + responsefromraspberry
                                        + " degrees of Celsius",
                                TextToSpeech.QUEUE_ADD, null, utteranceId);
                        break;
                    case "pressure":
                        TTS.speak("Current pressure is " + responsefromraspberry
                                        + " millimeters of mercury",
                                TextToSpeech.QUEUE_ADD, null, utteranceId);
                        break;
                    case "humidity":
                        TTS.speak("Current humidity is " + responsefromraspberry
                                        + " percent",
                                TextToSpeech.QUEUE_ADD, null, utteranceId);
                        break;
                    case "weather":
                        TTS.speak("Current weather forecast is: "
                                        + responsefromraspberry,
                                TextToSpeech.QUEUE_ADD, null, utteranceId);
                        break;
                }
                Log.i("sendRequest", "Response: " + responsefromraspberry);
            }
        });
    }

    // Send a request to set the LED color
    private void setColor(String color) {
        Toast.makeText(MainActivity.this, color, Toast.LENGTH_LONG).show();
        String utteranceId = this.hashCode() + "";
        String url = baseUrl;
        String LEDstripcolor = color;

        Request req1 = new Request.Builder()
                .url(url + color)  // e.g. "http://192.168.x.y:8000/FF0000"
                .build();

        client.newCall(req1).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                TTS.speak("There was an error: " + e.toString(),
                        TextToSpeech.QUEUE_ADD, null, utteranceId);
                Log.e("setColor", "Error", e);
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                responsefromraspberry = response.body().string();
                switch (LEDstripcolor) {
                    case "FF0000":
                        TTS.speak("The color is set to red",
                                TextToSpeech.QUEUE_ADD, null, utteranceId);
                        break;
                    case "00FF00":
                        TTS.speak("The color is set to green",
                                TextToSpeech.QUEUE_ADD, null, utteranceId);
                        break;
                    case "0000FF":
                        TTS.speak("The color is set to blue",
                                TextToSpeech.QUEUE_ADD, null, utteranceId);
                        break;
                    case "FFFF00":
                        TTS.speak("The color is set to yellow",
                                TextToSpeech.QUEUE_ADD, null, utteranceId);
                        break;
                    case "FF00FF":
                        TTS.speak("The color is set to purple",
                                TextToSpeech.QUEUE_ADD, null, utteranceId);
                        break;
                    case "FFFFFF":
                        TTS.speak("The color is set to white",
                                TextToSpeech.QUEUE_ADD, null, utteranceId);
                        break;
                    case "000000":
                        TTS.speak("The lights are off",
                                TextToSpeech.QUEUE_ADD, null, utteranceId);
                        break;
                    case "random":
                        TTS.speak("The color is set to a random color",
                                TextToSpeech.QUEUE_ADD, null, utteranceId);
                        break;
                }
                Log.i("setColor", "Response: " + responsefromraspberry);
            }
        });
    }

    // Simple delay method to reduce TTS collisions between queries
    private void delay(int seconds) {
        try {
            sleep(seconds * 1000L);
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
    }
}
