import math
import io
import base64
import numpy as np
import json
import requests
import pandas as pd

# Force Matplotlib to use the non-interactive Agg backend.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from flask import Flask, render_template_string

# Import the Paho MQTT client library
import paho.mqtt.client as mqtt

app = Flask(__name__)

# -------------------------
# Helper Functions
# -------------------------
def calculate_vpd(temp, dew_point):
    """
    Calculate the Vapor Pressure Deficit (VPD) in kPa.
    Formula:
      es = 0.6108 * exp(17.27 * T / (T + 237.3))
      VPD = es(T) - es(dew_point)
    (Both T and dew_point are in °C)
    """
    es = 0.6108 * math.exp(17.27 * temp / (temp + 237.3))
    ea = 0.6108 * math.exp(17.27 * dew_point / (dew_point + 237.3))
    return es - ea

def estimate_cloud_type(cloudcover):
    """
    Estimate cloud type based on cloud cover percentage.
    """
    if cloudcover < 20:
        return "Clear"
    elif cloudcover < 50:
        return "Partly Cloudy"
    else:
        return "Cloudy"

def fig_to_base64(fig):
    """Convert a matplotlib figure to a base64-encoded PNG."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    plt.close(fig)
    return img_base64

# -------------------------
# Flask Route
# -------------------------
@app.route("/")
def index():
    # ---------- 1. Current Hourly Forecast ----------
    latitude = 55.75
    longitude = 37.62
    timezone = "Europe/Moscow"
    weather_url = "https://api.open-meteo.com/v1/forecast"
    
    hourly_params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": (
            "temperature_2m,"
            "relativehumidity_2m,"
            "dewpoint_2m,"
            "precipitation_probability,"
            "windspeed_10m,"
            "winddirection_10m,"
            "pressure_msl,"
            "uv_index,"
            "cloudcover"
        ),
        "forecast_days": 1,
        "timezone": timezone
    }
    
    response_hourly = requests.get(weather_url, params=hourly_params)
    if response_hourly.status_code != 200:
        return f"Error fetching hourly weather data: {response_hourly.status_code}"
    
    weather_data = response_hourly.json()
    hourly = weather_data.get("hourly", {})
    if not hourly:
        return "No hourly weather data available."
    
    df_hourly = pd.DataFrame({
        "time": pd.to_datetime(hourly.get("time", [])),
        "temperature": hourly.get("temperature_2m", []),
        "humidity": hourly.get("relativehumidity_2m", []),
        "dew_point": hourly.get("dewpoint_2m", []),
        "precipitation_prob": hourly.get("precipitation_probability", []),
        "wind_speed": hourly.get("windspeed_10m", []),
        "wind_direction": hourly.get("winddirection_10m", []),
        "pressure": hourly.get("pressure_msl", []),
        "uv_index": hourly.get("uv_index", []),
        "cloudcover": hourly.get("cloudcover", [])
    })
    
    # Derived parameters
    df_hourly["vpd_kPa"] = [calculate_vpd(t, d) for t, d in zip(df_hourly["temperature"], df_hourly["dew_point"])]
    df_hourly["cloud_type"] = [estimate_cloud_type(cc) for cc in df_hourly["cloudcover"]]

    # Generate hourly forecast charts
    fig_temp, ax_temp = plt.subplots(figsize=(10, 5))
    ax_temp.plot(df_hourly["time"], df_hourly["temperature"], marker="o", linestyle="-", color="red")
    ax_temp.set_title("Hourly Temperature Forecast")
    ax_temp.set_xlabel("Time")
    ax_temp.set_ylabel("Temperature (°C)")
    ax_temp.grid(True)
    temp_img = fig_to_base64(fig_temp)

    fig_hum, ax_hum = plt.subplots(figsize=(10, 5))
    ax_hum.plot(df_hourly["time"], df_hourly["humidity"], marker="o", linestyle="-", color="blue")
    ax_hum.set_title("Hourly Humidity")
    ax_hum.set_xlabel("Time")
    ax_hum.set_ylabel("Relative Humidity (%)")
    ax_hum.grid(True)
    hum_img = fig_to_base64(fig_hum)

    fig_vpd, ax_vpd = plt.subplots(figsize=(10, 5))
    ax_vpd.plot(df_hourly["time"], df_hourly["vpd_kPa"], marker="o", linestyle="-", color="green")
    ax_vpd.set_title("Hourly Vapor Pressure Deficit")
    ax_vpd.set_xlabel("Time")
    ax_vpd.set_ylabel("VPD (kPa)")
    ax_vpd.grid(True)
    vpd_img = fig_to_base64(fig_vpd)

    # Create an interactive HTML table for hourly data
    hourly_table = df_hourly.to_html(classes="table table-striped table-bordered", index=False, table_id="hourlyTable")

    # ---------- 2. Future 7-Day Forecast ----------
    daily_params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "forecast_days": 7,
        "timezone": timezone
    }
    
    response_daily = requests.get(weather_url, params=daily_params)
    if response_daily.status_code != 200:
        daily_section = f"<p>Error fetching daily forecast data: {response_daily.status_code}</p>"
        daily_table = ""
    else:
        daily_data = response_daily.json().get("daily", {})
        if not daily_data:
            daily_section = "<p>No daily forecast data available.</p>"
            daily_table = ""
        else:
            df_daily = pd.DataFrame({
                "time": pd.to_datetime(daily_data.get("time", [])),
                "temp_max": daily_data.get("temperature_2m_max", []),
                "temp_min": daily_data.get("temperature_2m_min", []),
                "precipitation": daily_data.get("precipitation_sum", [])
            })
            df_daily["temp_avg"] = (df_daily["temp_max"] + df_daily["temp_min"]) / 2

            fig_daily, ax_daily = plt.subplots(figsize=(10, 5))
            ax_daily.plot(df_daily["time"], df_daily["temp_max"], marker="o", linestyle="-", color="red", label="Max Temp")
            ax_daily.plot(df_daily["time"], df_daily["temp_min"], marker="o", linestyle="-", color="blue", label="Min Temp")
            ax_daily.plot(df_daily["time"], df_daily["temp_avg"], marker="o", linestyle="--", color="green", label="Avg Temp")
            ax_daily.set_title("7-Day Temperature Forecast")
            ax_daily.set_xlabel("Date")
            ax_daily.set_ylabel("Temperature (°C)")
            ax_daily.legend()
            ax_daily.grid(True)
            daily_img = fig_to_base64(fig_daily)

            daily_table = df_daily.to_html(classes="table table-striped table-bordered", index=False, table_id="dailyTable")
            daily_section = f"""
             <div class="card shadow mb-4">
                <img src="data:image/png;base64,{daily_img}" class="card-img-top" alt="Daily Forecast Plot">
                <div class="card-body">
                   <h5 class="card-title">7-Day Temperature Forecast</h5>
                   <p class="card-text">Max, Min, and Average temperatures for the next 7 days.</p>
                </div>
             </div>
             <h3>Interactive Future Forecast Data</h3>
             {daily_table}
             """

    # ---------- 3. Short-Term Temperature Prediction (Next 12 Hours) ----------
    # Use the last 6 hours of hourly data for a simple linear regression prediction.
    if len(df_hourly) >= 6:
        df_recent = df_hourly.tail(6).copy()
        # Convert time to numerical values (Unix timestamp)
        df_recent["timestamp"] = df_recent["time"].apply(lambda x: x.timestamp())
        X = df_recent["timestamp"].values
        y = df_recent["temperature"].values
        # Fit a simple linear model: temperature = m * time + b
        m, b = np.polyfit(X, y, 1)
        # Create predictions for the next 12 hours
        last_time = df_hourly["time"].max()
        future_times = [last_time + pd.Timedelta(hours=i) for i in range(1, 13)]
        future_timestamps = [t.timestamp() for t in future_times]
        predicted_temps = [m * ts + b for ts in future_timestamps]
        df_pred = pd.DataFrame({
            "time": future_times,
            "predicted_temperature": predicted_temps
        })
        # Build a prediction chart (showing recent data and prediction)
        fig_pred, ax_pred = plt.subplots(figsize=(10, 5))
        ax_pred.plot(df_recent["time"], df_recent["temperature"], marker="o", linestyle="-", color="black", label="Recent Observations")
        ax_pred.plot(df_pred["time"], df_pred["predicted_temperature"], marker="o", linestyle="--", color="orange", label="Predicted Temperature")
        ax_pred.set_title("Short-Term Temperature Prediction (Next 12 Hours)")
        ax_pred.set_xlabel("Time")
        ax_pred.set_ylabel("Temperature (°C)")
        ax_pred.legend()
        ax_pred.grid(True)
        pred_img = fig_to_base64(fig_pred)
        pred_table = df_pred.to_html(classes="table table-striped table-bordered", index=False, table_id="predTable")
        prediction_section = f"""
            <div class="card shadow mb-4">
               <img src="data:image/png;base64,{pred_img}" class="card-img-top" alt="Prediction Plot">
               <div class="card-body">
                  <h5 class="card-title">Short-Term Temperature Prediction</h5>
                  <p class="card-text">Predicted temperatures for the next 12 hours based on recent trends.</p>
               </div>
            </div>
            <h3>Prediction Data</h3>
            {pred_table}
        """
    else:
        prediction_section = "<p>Not enough data for prediction.</p>"

    # ---------- MQTT PUBLISHING ----------
    # Build a payload dictionary with the key information.
    mqtt_payload = {
        "hourly_data": df_hourly.to_dict(orient="records"),
        "hourly_plots": {
            "temperature": temp_img,
            "humidity": hum_img,
            "vpd": vpd_img
        }
    }
    # Daily data & plot if available
    if 'df_daily' in locals():
        mqtt_payload["daily_data"] = df_daily.to_dict(orient="records")
        mqtt_payload["daily_plot"] = daily_img
    else:
        mqtt_payload["daily_data"] = None
    # Prediction data & plot if available
    if 'df_pred' in locals():
        mqtt_payload["prediction_data"] = df_pred.to_dict(orient="records")
        mqtt_payload["prediction_plot"] = pred_img
    else:
        mqtt_payload["prediction_data"] = None

    # Publish the payload via MQTT to the broker on localhost:1883
    try:
        # Use protocol MQTTv311 to avoid callback API version deprecation warnings.
        client = mqtt.Client(protocol=mqtt.MQTTv311)
        client.connect("localhost", 5050, 60)
        # Use default=str to convert non-serializable objects (e.g. Timestamps) into strings.
        client.publish("weather/data", json.dumps(mqtt_payload, default=str))
        client.disconnect()
    except Exception as e:
        print("Error publishing MQTT message:", e)

    # ---------- RENDER HTML TEMPLATE ----------
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
      <head>
         <meta charset="UTF-8">
         <title>Beautiful Weather Dashboard for Moscow</title>
         <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css">
         <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.21/css/jquery.dataTables.min.css"/>
         <style>
            body { background-color: #f0f2f5; }
            .header {
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 30px;
                text-align: center;
                margin-bottom: 30px;
            }
            .card { margin-bottom: 30px; }
            .card-title { font-size: 1.5rem; }
            .summary {
                white-space: pre-wrap;
                font-family: monospace;
                background: #fff;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0px 2px 10px rgba(0,0,0,0.1);
            }
            footer { text-align: center; margin-top: 40px; padding: 20px; background: #e9ecef; }
         </style>
      </head>
      <body>
         <div class="header">
            <h1>Beautiful Weather Dashboard for Moscow</h1>
            <p>Real-time Weather & Future Forecast Analysis with Predictions</p>
         </div>
         <div class="container">
            <h2>Current Hourly Forecast</h2>
            <div class="row">
               <div class="col-md-4">
                  <div class="card shadow">
                     <img src="data:image/png;base64,{{ temp_img }}" class="card-img-top" alt="Temperature Plot">
                     <div class="card-body">
                        <h5 class="card-title">Temperature Forecast</h5>
                        <p class="card-text">Hourly temperature in °C.</p>
                     </div>
                  </div>
               </div>
               <div class="col-md-4">
                  <div class="card shadow">
                     <img src="data:image/png;base64,{{ hum_img }}" class="card-img-top" alt="Humidity Plot">
                     <div class="card-body">
                        <h5 class="card-title">Humidity Levels</h5>
                        <p class="card-text">Hourly relative humidity in %.</p>
                     </div>
                  </div>
               </div>
               <div class="col-md-4">
                  <div class="card shadow">
                     <img src="data:image/png;base64,{{ vpd_img }}" class="card-img-top" alt="VPD Plot">
                     <div class="card-body">
                        <h5 class="card-title">Vapor Pressure Deficit</h5>
                        <p class="card-text">Hourly VPD in kPa.</p>
                     </div>
                  </div>
               </div>
            </div>
            <h3 class="mb-4">Interactive Hourly Forecast Data</h3>
            <div class="table-responsive">
                {{ hourly_table | safe }}
            </div>
            
            <hr class="my-5">
            
            <h2>Future 7-Day Forecast Analysis</h2>
            {{ daily_section | safe }}
            
            <hr class="my-5">
            
            <h2>Short-Term Temperature Prediction (Next 12 Hours)</h2>
            {{ prediction_section | safe }}
         </div>
         <footer>
            <p>© 2025 Beautiful Weather Dashboard for Moscow</p>
         </footer>
         <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
         <script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.10.21/js/jquery.dataTables.min.js"></script>
         <script>
            $(document).ready(function() {
                $('#hourlyTable').DataTable();
                $('#dailyTable').DataTable();
                $('#predTable').DataTable();
            });
         </script>
         <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/js/bootstrap.bundle.min.js"></script>
      </body>
    </html>
    """

    return render_template_string(html_template,
                                  temp_img=temp_img,
                                  hum_img=hum_img,
                                  vpd_img=vpd_img,
                                  hourly_table=hourly_table,
                                  daily_section=daily_section,
                                  prediction_section=prediction_section)

# -------------------------
# Run Flask App
# -------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5050, use_reloader=False)
