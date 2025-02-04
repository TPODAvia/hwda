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

public class DailyFragment extends Fragment {

    private ImageView imgDailyPlot;
    private TextView tvDailyData;

    public DailyFragment() {
        // Required empty constructor
    }

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater,
                             @Nullable ViewGroup container,
                             @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_daily, container, false);
        imgDailyPlot = view.findViewById(R.id.imgDailyPlot);
        tvDailyData = view.findViewById(R.id.tvDailyData);
        return view;
    }

    public void updateData(String jsonPayload) {
        if (jsonPayload == null || jsonPayload.isEmpty()) {
            tvDailyData.setText("No Daily data received.");
            return;
        }

        try {
            JSONObject root = new JSONObject(jsonPayload);

            // daily_data array
            JSONArray dailyDataArr = root.optJSONArray("daily_data");
            // daily_plot
            String dailyPlotBase64 = root.optString("daily_plot", "");

            // Decode the daily plot
            if (!dailyPlotBase64.isEmpty()) {
                Bitmap dailyPlot = decodeBase64ToBitmap(dailyPlotBase64);
                if (dailyPlot != null) {
                    imgDailyPlot.setImageBitmap(dailyPlot);
                }
            }

            // Build textual summary
            StringBuilder sb = new StringBuilder();
            sb.append("DAILY DATA:\n\n");
            if (dailyDataArr != null) {
                for (int i = 0; i < dailyDataArr.length(); i++) {
                    JSONObject obj = dailyDataArr.getJSONObject(i);
                    String time = obj.optString("time", "");
                    double tempMax = obj.optDouble("temp_max", 0.0);
                    double tempMin = obj.optDouble("temp_min", 0.0);
                    double tempAvg = obj.optDouble("temp_avg", 0.0);
                    double precip = obj.optDouble("precipitation", 0.0);

                    sb.append("Date: ").append(time).append("\n")
                            .append("  Max: ").append(tempMax).append(" °C\n")
                            .append("  Min: ").append(tempMin).append(" °C\n")
                            .append("  Avg: ").append(tempAvg).append(" °C\n")
                            .append("  Precip: ").append(precip).append(" mm\n\n");
                }
            } else {
                sb.append("No daily_data found in JSON.\n");
            }

            tvDailyData.setText(sb.toString());

        } catch (Exception e) {
            e.printStackTrace();
            tvDailyData.setText("Error parsing daily data:\n" + e.getMessage());
        }
    }

    private Bitmap decodeBase64ToBitmap(String base64Str) {
        if (base64Str.isEmpty()) return null;
        try {
            byte[] decodedBytes = Base64.decode(base64Str, Base64.DEFAULT);
            return BitmapFactory.decodeByteArray(decodedBytes, 0, decodedBytes.length);
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }
}
