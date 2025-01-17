package com.example.rgbcontroller;  // <-- your package name

import androidx.appcompat.app.AppCompatActivity;
import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import yuku.ambilwarna.AmbilWarnaDialog;

import android.graphics.Color;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.CompoundButton;
import android.widget.SeekBar;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;

import java.io.IOException;

public class MainActivity extends AppCompatActivity {
    private static final String TAG = "MainActivity";

    private int red, green, blue, direction, func;
    private String delVal;
    private int mDefaultColor;
    private OkHttpClient client;

    // Replace with your Arduino device IP address or domain
    private static final String baseUrl = "http://192.168.1.7/"; //some_ip_address

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        red = green = blue = direction = func = -1;

        Button btSetColor = findViewById(R.id.setColor);
        Button btClear = findViewById(R.id.clear);
        Button btRainbow = findViewById(R.id.rainbow);
        Button btSelectColor = findViewById(R.id.selectColor);
        SeekBar delay = findViewById(R.id.delay);
        Switch forwardBack = findViewById(R.id.fwdbckwd);
        TextView delayValue = findViewById(R.id.delaylbl);

        // If the user doesn't change anything - init default values
        delVal = String.valueOf(delay.getProgress());
        delayValue.setText("delay: " + delVal);

        // Set default direction
        if (forwardBack.isChecked()) {
            forwardBack.setText(forwardBack.getTextOn().toString());
            direction = 1;
        } else {
            forwardBack.setText(forwardBack.getTextOff().toString());
            direction = 2;
        }

        // Init OkHTTP client
        client = new OkHttpClient();

        // Switch OnCheckedChangeListener
        forwardBack.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton compoundButton, boolean isChecked) {
                if (isChecked) {
                    forwardBack.setText(forwardBack.getTextOn().toString());
                    direction = 1;
                } else {
                    forwardBack.setText(forwardBack.getTextOff().toString());
                    direction = 2;
                }
            }
        });

        // SeekBar OnSeekBarChangeListener
        delay.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int i, boolean b) {
                delVal = String.valueOf(i);
                delayValue.setText("delay: " + delVal);
            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) { }

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) { }
        });

        // Button: Set Color
        btSetColor.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                func = 0; // fill
                initCall();
            }
        });

        // Button: Clear
        btClear.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                func = 1; // clear
                initCall();
            }
        });

        // Button: Rainbow
        btRainbow.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                func = 2; // rainbow
                initCall();
            }
        });

        // Button: Select Color
        btSelectColor.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                mDefaultColor = 0;
                final AmbilWarnaDialog colorPickerDialogue = new AmbilWarnaDialog(
                        MainActivity.this,
                        mDefaultColor,
                        new AmbilWarnaDialog.OnAmbilWarnaListener() {
                            @Override
                            public void onCancel(AmbilWarnaDialog dialog) {
                                // do nothing
                            }

                            @Override
                            public void onOk(AmbilWarnaDialog dialog, int color) {
                                mDefaultColor = color;
                                red = Color.red(color);
                                green = Color.green(color);
                                blue = Color.blue(color);
                                // change the picked color button background
                                btSelectColor.setBackgroundColor(mDefaultColor);
                            }
                        }
                );
                colorPickerDialogue.show();
            }
        });
    }

    // Method to initiate the HTTP call
    public void initCall() {
        // If color hasn’t been set yet, show a Toast and exit
        if (red == -1 || green == -1 || blue == -1) {
            Toast.makeText(this, "Color is not set, please select a color", Toast.LENGTH_SHORT).show();
            return;
        }

        Log.d(TAG, "Func [" + func + "] - Red [" + red + "] - Green [" + green + "] - Blue [" + blue
                + "] - Dir [" + direction + "] - Delay [" + delVal + "]");

        // Convert the color to a hex string (e.g. FF00FF)
        String hexColor = getHex(red) + getHex(green) + getHex(blue);

        // Ensure the delay is two digits
        String delayTwoDigits = (Integer.valueOf(delVal) < 10) ? "0" + delVal : delVal;

        // Create the params string (example: 100ff000990)
        String params = Integer.toString(direction) + hexColor + delayTwoDigits + func;
        Log.d(TAG, "Params [" + params + "]");

        // Determine the function path
        String url = baseUrl;
        switch (func) {
            case 0:
                url += "fill";
                break;
            case 1:
                url += "clear";
                break;
            case 2:
                url += "rainbow";
                break;
        }

        // Build the final URL with query params
        String finalUrl = url + "?params=" + params;
        Log.d(TAG, "URL [" + finalUrl + "]");

        // Build and enqueue the request
        Request req = new Request.Builder().url(finalUrl).build();
        client.newCall(req).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                Log.e(TAG, "Error");
                e.printStackTrace();
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                Log.i(TAG, "Response: " + response.body().string());
            }
        });
    }

    // Helper method for converting integer color to hex
    private String getHex(int val) {
        String hex = Integer.toHexString(val);
        if (hex.length() < 2) {
            hex = "0" + hex;
        }
        return hex;
    }
}
