package com.example.weathermqttapp;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Bundle;
import android.util.Base64;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

import org.json.JSONArray;
import org.json.JSONObject;

public class HourlyFragment extends Fragment {

    private ImageView imgHourlyTemp, imgHourlyHum, imgHourlyVpd;
    private TextView tvHourlyData;

    public HourlyFragment() {
        // Required empty constructor
    }

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater,
                             @Nullable ViewGroup container,
                             @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_hourly, container, false);
        imgHourlyTemp = view.findViewById(R.id.imgHourlyTemp);
        imgHourlyHum = view.findViewById(R.id.imgHourlyHum);
        imgHourlyVpd = view.findViewById(R.id.imgHourlyVpd);
        tvHourlyData = view.findViewById(R.id.tvHourlyData);
        return view;
    }

    /**
     * Called by MainActivity when MQTT data arrives.
     */
    public void updateData(String jsonPayload) {
        if (jsonPayload == null || jsonPayload.isEmpty()) {
            tvHourlyData.setText("No Hourly data received.");
            return;
        }

        try {
            JSONObject root = new JSONObject(jsonPayload);

            // 1) Get the "hourly_data" array
            JSONArray hourlyDataArr = root.optJSONArray("hourly_data");

            // 2) Get "hourly_plots" object
            JSONObject hourlyPlots = root.optJSONObject("hourly_plots");
            if (hourlyPlots != null) {
                // Temperature chart
                String tempBase64 = hourlyPlots.optString("temperature", "");
                Bitmap bmpTemp = decodeBase64ToBitmap(tempBase64);
                if (bmpTemp != null) {
                    imgHourlyTemp.setImageBitmap(bmpTemp);
                }

                // Humidity chart
                String humBase64 = hourlyPlots.optString("humidity", "");
                Bitmap bmpHum = decodeBase64ToBitmap(humBase64);
                if (bmpHum != null) {
                    imgHourlyHum.setImageBitmap(bmpHum);
                }

                // VPD chart
                String vpdBase64 = hourlyPlots.optString("vpd", "");
                Bitmap bmpVpd = decodeBase64ToBitmap(vpdBase64);
                if (bmpVpd != null) {
                    imgHourlyVpd.setImageBitmap(bmpVpd);
                }
            }

            // Build a text summary
            StringBuilder sb = new StringBuilder();
            sb.append("HOURLY DATA:\n\n");
            if (hourlyDataArr != null) {
                for (int i = 0; i < hourlyDataArr.length(); i++) {
                    JSONObject obj = hourlyDataArr.getJSONObject(i);
                    String time = obj.optString("time", "");
                    double temperature = obj.optDouble("temperature", 0.0);
                    double humidity = obj.optDouble("humidity", 0.0);
                    double vpd = obj.optDouble("vpd_kPa", 0.0);

                    sb.append("Time: ").append(time).append("\n")
                            .append("  Temperature: ").append(temperature).append(" °C\n")
                            .append("  Humidity: ").append(humidity).append(" %\n")
                            .append("  VPD: ").append(vpd).append(" kPa\n\n");
                }
            } else {
                sb.append("No hourly_data found in JSON.\n");
            }

            tvHourlyData.setText(sb.toString());

        } catch (Exception e) {
            e.printStackTrace();
            tvHourlyData.setText("Error parsing hourly data:\n" + e.getMessage());
        }
    }

    /**
     * Helper for Base64 -> Bitmap decoding
     */
    private Bitmap decodeBase64ToBitmap(String base64Str) {
        if (base64Str == null || base64Str.isEmpty()) return null;
        try {
            byte[] decodedBytes = Base64.decode(base64Str, Base64.DEFAULT);
            return BitmapFactory.decodeByteArray(decodedBytes, 0, decodedBytes.length);
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }
}
