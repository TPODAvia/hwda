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

    private int red   = -1;
    private int green = -1;
    private int blue  = -1;
    private int direction;  // 1 = forward, 2 = backward
    private int func;       // which button was clicked
    private String delVal;  // raw delay from SeekBar
    private int mDefaultColor;
    private OkHttpClient client;

    // Replace with your Arduino or ESP IP address
    private static final String baseUrl = "http://192.168.172.222";  // no trailing slash

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // ========== Find Views ==========
        Button btSetColor     = findViewById(R.id.setColor);
        Button btClear        = findViewById(R.id.clear);
        Button btRainbow      = findViewById(R.id.rainbow);
        Button btSelectColor  = findViewById(R.id.selectColor);
        SeekBar seekDelay     = findViewById(R.id.delay);
        Switch forwardBack    = findViewById(R.id.fwdbckwd);
        TextView delayLabel   = findViewById(R.id.delaylbl);

        // ========== Initialize Defaults ==========
        client = new OkHttpClient();

        // Default delay
        delVal = String.valueOf(seekDelay.getProgress());
        delayLabel.setText("delay: " + delVal);

        // Default direction
        // (Switch is set to checked=true in XML => "FORWARD")
        direction = forwardBack.isChecked() ? 1 : 2;

        // ========== Listeners ==========

        // Switch OnCheckedChangeListener
        forwardBack.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                direction = isChecked ? 1 : 2;
                forwardBack.setText(isChecked ? forwardBack.getTextOn() : forwardBack.getTextOff());
            }
        });

        // SeekBar OnSeekBarChangeListener
        seekDelay.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                delVal = String.valueOf(progress);
                delayLabel.setText("delay: " + delVal);
            }
            @Override public void onStartTrackingTouch(SeekBar seekBar) { }
            @Override public void onStopTrackingTouch(SeekBar seekBar) { }
        });

        // Button: SELECT A COLOR
        btSelectColor.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                mDefaultColor = 0; // or keep last chosen color
                AmbilWarnaDialog colorPicker = new AmbilWarnaDialog(
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
                                red   = Color.red(color);
                                green = Color.green(color);
                                blue  = Color.blue(color);
                                btSelectColor.setBackgroundColor(mDefaultColor);
                            }
                        }
                );
                colorPicker.show();
            }
        });

        // Button: SET COLOR => fill
        btSetColor.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                func = 0; // we'll define "0" as fill
                callArduino();
            }
        });

        // Button: CLEAR
        btClear.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                func = 1; // "1" = clear
                callArduino();
            }
        });

        // Button: RAINBOW
        btRainbow.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                func = 2; // "2" = rainbow
                callArduino();
            }
        });
    }

    // ========= Core Logic to Build URL and Send Request =========
    private void callArduino() {
        // For fill or rainbow, we need a color. Clear might not strictly need color,
        // but if your Arduino code expects a full param string, we still supply it.
        // If you truly want "clear" to ignore color, remove the check or handle differently.
        if ((func == 0 || func == 2) && (red == -1 || green == -1 || blue == -1)) {
            Toast.makeText(this, "Color not selected!", Toast.LENGTH_SHORT).show();
            return;
        }

        // Convert the chosen color to a 6-digit hex RRGGBB (just like Python: #AABBCC => AABBCC)
        String hexColor = getHex(red) + getHex(green) + getHex(blue);

        // According to your Python code:
        //   CLEAR => /clear?params={dir}{RRGGBB}{delay}1
        //   SET   => /fill?params={dir}{RRGGBB}{delay}0
        //   RAINBOW => /rainbow?params={dir}{RRGGBB}{delay}2
        //
        // Where direction is "1" or "2", RRGGBB is color (without #), delay is raw,
        // and the last digit is the function code: 0=fill, 1=clear, 2=rainbow.

        String path;
        String lastDigit;  // the cycle or function at the end

        switch (func) {
            case 0:  // fill
                path = "/fill";
                lastDigit = "0";
                break;
            case 1:  // clear
                path = "/clear";
                lastDigit = "1";
                break;
            case 2:  // rainbow
                path = "/rainbow";
                lastDigit = "2";
                break;
            default:
                return; // no-op
        }

        // Build param string (no zero-padding on delay, to match Python):
        // direction + colorHex + delay + lastDigit
        String param = direction + hexColor + delVal + lastDigit;

        // Final URL
        String finalUrl = baseUrl + ":" + 80 + path + "?params=" + param;

        Log.d(TAG, "Requesting: " + finalUrl);

        Request request = new Request.Builder().url(finalUrl).build();
        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                Log.e(TAG, "Error in HTTP request", e);
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                final String body = response.body() != null ? response.body().string() : "no body";
                Log.i(TAG, "Response: " + body);
            }
        });
    }

    // Helper: convert int 0-255 to two-hex-digits (e.g. 255 => "ff")
    private String getHex(int val) {
        if (val < 0) val = 0;
        if (val > 255) val = 255;
        String hex = Integer.toHexString(val);
        return (hex.length() == 1) ? "0" + hex : hex;
    }
}
