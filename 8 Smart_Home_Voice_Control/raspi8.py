from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from io import BytesIO
import smbus2
import bme280
import neopixel
import board
import random

port = 1
address = 0x76
bus = smbus2.SMBus(port)
calibration_params = bme280.load_calibration_params(bus, address)
lvl1 = 1022.69 #Паскалей, или 767.2 мм.рт.ст.
lvl2 = 1009.14 #Паскалей, или 756.92 мм.рт.ст.

num_pixels = 12 #количество лампочек в LED-ленте
pixel_pin = board.D18 #на малине это 12-й пин, или GPIO18 (BCM18)
ORDER = neopixel.GRB
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.1, auto_write=False, pixel_order=ORDER)

def lightsOn(color): # color be like FFFFFF
    global pixels    
    if color == "random":
        r = random.randrange(256)
        g = random.randrange(256)
        b = random.randrange(256)
    else:
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)    
    pixels.fill((r, g, b))
    pixels.show()


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        #self.wfile.write(b'Hello')
        #self.wfile.write(bytes(self.path, "utf-8"))
        body = self.path
        print(body)
        if body.__contains__('temperature'):
            data = bme280.sample(bus, address, calibration_params)
            body = str(round(data.temperature))
        if body.__contains__('pressure'):
            data = bme280.sample(bus, address, calibration_params)
            body = str(round(data.pressure/1.33322387415))
        if body.__contains__('humidity'):
            data = bme280.sample(bus, address, calibration_params)
            body = str(round(data.humidity))
        if body.__contains__('weather'):
            data = bme280.sample(bus, address, calibration_params)
            if data.pressure >= lvl1:
                weather_forecast = 'the weather will be stable'
            elif data.pressure >= lvl2 and data.pressure < lvl1:
                weather_forecast = 'the weather will be cloudy'
            else:
                weather_forecast = 'the weather will be rainy'    
            body = weather_forecast
        if body.__contains__('FF0000'):
            lightsOn('FF0000')
        if body.__contains__('00FF00'):
            lightsOn('00FF00')
        if body.__contains__('0000FF'):
            lightsOn('0000FF')
        if body.__contains__('FFFF00'):
            lightsOn('FFFF00')
        if body.__contains__('FF00FF'):
            lightsOn('FF00FF')
        if body.__contains__('FFFFFF'):
            lightsOn('FFFFFF')
        if body.__contains__('000000'):
            lightsOn('000000')
        if body.__contains__('random'):
            lightsOn('random')
        
        response = BytesIO()
        response.write(bytes(body, "utf-8"))
        self.wfile.write(response.getvalue())
        print(response.getvalue())   
    


def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler):
    server_address = ('X.X.X.X', 8000)
    httpd = server_class(server_address, handler_class)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        
run()