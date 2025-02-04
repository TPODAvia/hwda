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

public class PredictionFragment extends Fragment {

    private ImageView imgPredictionPlot;
    private TextView tvPredictionData;

    public PredictionFragment() {
        // Required empty constructor
    }

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater,
                             @Nullable ViewGroup container,
                             @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_prediction, container, false);
        imgPredictionPlot = view.findViewById(R.id.imgPredictionPlot);
        tvPredictionData = view.findViewById(R.id.tvPredictionData);
        return view;
    }

    public void updateData(String jsonPayload) {
        if (jsonPayload == null || jsonPayload.isEmpty()) {
            tvPredictionData.setText("No Prediction data received.");
            return;
        }

        try {
            JSONObject root = new JSONObject(jsonPayload);

            // prediction_data array
            JSONArray predictionDataArr = root.optJSONArray("prediction_data");
            // prediction_plot
            String predictionPlotBase64 = root.optString("prediction_plot", "");

            // Decode plot
            if (!predictionPlotBase64.isEmpty()) {
                Bitmap bmpPred = decodeBase64ToBitmap(predictionPlotBase64);
                if (bmpPred != null) {
                    imgPredictionPlot.setImageBitmap(bmpPred);
                }
            }

            // Build summary
            StringBuilder sb = new StringBuilder();
            sb.append("PREDICTION DATA (Next 12 Hours):\n\n");
            if (predictionDataArr != null) {
                for (int i = 0; i < predictionDataArr.length(); i++) {
                    JSONObject obj = predictionDataArr.getJSONObject(i);
                    String time = obj.optString("time", "");
                    double predTemp = obj.optDouble("predicted_temperature", 0.0);

                    sb.append("Time: ").append(time).append("\n")
                            .append("  Predicted Temp: ").append(predTemp).append(" °C\n\n");
                }
            } else {
                sb.append("No prediction_data found in JSON.\n");
            }

            tvPredictionData.setText(sb.toString());

        } catch (Exception e) {
            e.printStackTrace();
            tvPredictionData.setText("Error parsing prediction data:\n" + e.getMessage());
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
