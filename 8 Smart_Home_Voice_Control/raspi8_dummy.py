from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from io import BytesIO
import neopixel
import board
import random

# Pressure thresholds for a simple "weather forecast"
lvl1 = 1022.69  # Pa
lvl2 = 1009.14  # Pa

num_pixels = 12  # Number of LEDs in the strip
pixel_pin = board.D18  # GPIO18
ORDER = neopixel.GRB
pixels = neopixel.NeoPixel(pixel_pin, num_pixels,
                           brightness=0.1,
                           auto_write=False,
                           pixel_order=ORDER)

def lightsOn(color):
    global pixels
    if color == "random":
        r = random.randrange(256)
        g = random.randrange(256)
        b = random.randrange(256)
    else:
        # color is a hex string like 'FF0000'
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
    pixels.fill((r, g, b))
    pixels.show()

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        body = self.path  # e.g. '/temperature', '/FF0000', etc.
        print("Request path:", body)

        if 'temperature' in body:
            # Generate dummy temperature data
            temperature = round(random.uniform(20.0, 30.0), 1)  # Random temperature in Celsius
            body = str(temperature)
        elif 'pressure' in body:
            # Generate dummy pressure data
            pressure = round(random.uniform(950.0, 1050.0) / 1.33322387415, 1)  # Convert hPa to mmHg
            body = str(pressure)
        elif 'humidity' in body:
            # Generate dummy humidity data
            humidity = round(random.uniform(30.0, 70.0), 1)  # Random humidity percentage
            body = str(humidity)
        elif 'weather' in body:
            # Generate a dummy "weather forecast"
            pressure = random.uniform(950.0, 1050.0)  # Random pressure in hPa
            if pressure >= lvl1:
                weather_forecast = 'the weather will be stable'
            elif pressure >= lvl2 and pressure < lvl1:
                weather_forecast = 'the weather will be cloudy'
            else:
                weather_forecast = 'the weather will be rainy'
            body = weather_forecast

        # LED strip color patterns
        if 'FF0000' in body:
            lightsOn('FF0000')
        elif '00FF00' in body:
            lightsOn('00FF00')
        elif '0000FF' in body:
            lightsOn('0000FF')
        elif 'FFFF00' in body:
            lightsOn('FFFF00')
        elif 'FF00FF' in body:
            lightsOn('FF00FF')
        elif 'FFFFFF' in body:
            lightsOn('FFFFFF')
        elif '000000' in body:
            lightsOn('000000')
        elif 'random' in body:
            lightsOn('random')

        response = BytesIO()
        response.write(bytes(body, "utf-8"))
        self.wfile.write(response.getvalue())
        print("Response:", response.getvalue())

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler):
    server_address = ('0.0.0.0', 8000)  # <--- Localjost
    httpd = server_class(server_address, handler_class)
    try:
        print("Server running at http://localhost:8000/ ...")
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()

run()
