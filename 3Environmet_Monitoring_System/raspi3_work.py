import PySimpleGUI as sg
import RPi.GPIO as GPIO
from time import sleep
import smbus2
from RPi.bme280 import BME280

# Constants
port = 1
address = 0x76
lvl1 = 1022.69  # Pressure level 1 (Pa)
lvl2 = 1009.14  # Pressure level 2 (Pa)
tempmeltinglvl = 30  # Temperature threshold (°C)

# Initialize BME280
bus = smbus2.SMBus(port)
bme280 = BME280(i2c_dev=bus)

# GUI Layout
layout = [
    [sg.Text('temperature:', key='-temp-', font=('Calibri', 48), text_color='green', justification='center')],
    [sg.Text('pressure:', key='-press-', font=('Calibri', 48), text_color='violet', justification='center')],
    [sg.Text('weather:', key='-weather-', font=('Calibri', 48), text_color='orange', justification='center')],
]

window = sg.Window('Temperature+Humidity+Pressure Sensor', layout, size=(1280, 800), finalize=True)

# GPIO setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(31, GPIO.OUT, initial=GPIO.LOW)  # Red LED
GPIO.setup(35, GPIO.OUT, initial=GPIO.LOW)  # Green LED
GPIO.setup(37, GPIO.OUT, initial=GPIO.LOW)  # Blue LED
GPIO.setup(29, GPIO.OUT, initial=GPIO.LOW)  # Alarm LED

try:
    while True:
        # Read sensor data
        temperature = bme280.get_temperature()
        pressure = bme280.get_pressure()

        # Update GUI
        window['-temp-'].update(f'temperature: {round(temperature)} °C')
        window['-press-'].update(f'pressure: {round(pressure)} mb')

        # Update LEDs and Weather Forecast
        if temperature >= tempmeltinglvl:
            GPIO.output(29, GPIO.HIGH)
            print('HOT')
        else:
            GPIO.output(29, GPIO.LOW)

        if pressure >= lvl1:
            weather_forecast = 'the weather will be stable'
            GPIO.output(31, GPIO.HIGH)
            GPIO.output(35, GPIO.HIGH)
            GPIO.output(37, GPIO.LOW)  # Yellow
        elif lvl2 <= pressure < lvl1:
            weather_forecast = 'the weather will be cloudy'
            GPIO.output(31, GPIO.HIGH)
            GPIO.output(35, GPIO.HIGH)
            GPIO.output(37, GPIO.HIGH)  # White
        else:
            weather_forecast = 'the weather will be rainy'
            GPIO.output(31, GPIO.LOW)
            GPIO.output(35, GPIO.LOW)
            GPIO.output(37, GPIO.HIGH)  # Blue

        window['-weather-'].update(f'weather: {weather_forecast}')
        window.refresh()

        # Print to Console
        print(f'Temperature: {temperature} °C')
        print(f'Pressure: {pressure} mb')
        print(f'Forecast: {weather_forecast}')
        sleep(1)

except Exception as e:
    print(f'** Error: {e} **')

finally:
    window.close()
    GPIO.cleanup()
