from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from io import BytesIO
import smbus2
import bme280
import neopixel
import board
import random

port = 1
address = 0x76  # BME280 or BMP280 I2C address
bus = smbus2.SMBus(port)
calibration_params = bme280.load_calibration_params(bus, address)

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
            data = bme280.sample(bus, address, calibration_params)
            body = str(round(data.temperature))
        elif 'pressure' in body:
            data = bme280.sample(bus, address, calibration_params)
            # Convert hPa to mmHg -> 1hPa ~ 1.33322 mmHg
            body = str(round(data.pressure / 1.33322387415))
        elif 'humidity' in body:
            data = bme280.sample(bus, address, calibration_params)
            body = str(round(data.humidity))
        elif 'weather' in body:
            data = bme280.sample(bus, address, calibration_params)
            if data.pressure >= lvl1:
                weather_forecast = 'the weather will be stable'
            elif data.pressure >= lvl2 and data.pressure < lvl1:
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
    server_address = ('192.168.x.y', 8000)  # <--- Change IP and port
    httpd = server_class(server_address, handler_class)
    try:
        print("Server running at http://192.168.x.y:8000/ ...")
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()

run()
