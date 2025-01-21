import PySimpleGUI as sg
import RPi.GPIO as GPIO
from time import sleep
import smbus2
import bme280

port = 1
address = 0x76
bus = smbus2.SMBus(port)
calibration_params = bme280.load_calibration_params(bus, address)

# Thresholds (in millibars) as used in original code
lvl1 = 1022.69  # ~ 767.2 mmHg
lvl2 = 1009.14  # ~ 756.92 mmHg
tempmeltinglvl = 30

# ----------------------
# LAYOUT (Add Humidity)
# ----------------------
layout = [
    [sg.Text('Temperature:', 
             size=(None, None), 
             key='-temp-', 
             auto_size_text=True, 
             pad=((5,5),(150,0)),  # slightly adjusted vertical pad
             expand_x=True, 
             font=('Calibri', 48), 
             text_color='green', 
             justification='center')],
    
    [sg.Text('Humidity:', 
             size=(None, None), 
             key='-humidity-', 
             auto_size_text=True, 
             pad=((5,5),(0,0)), 
             expand_x=True, 
             font=('Calibri', 48), 
             text_color='blue', 
             justification='center')],

    [sg.Text('Pressure:', 
             size=(None, None), 
             key='-press-', 
             auto_size_text=True, 
             pad=((5,5),(0,0)), 
             expand_x=True, 
             font=('Calibri', 48), 
             text_color='violet', 
             justification='center')],

    [sg.Text('Weather:', 
             size=(None, None), 
             key='-weather-', 
             auto_size_text=True, 
             pad=((5,5),(0,0)), 
             expand_x=True, 
             font=('Calibri', 48), 
             text_color='orange', 
             justification='center')]
]

window = sg.Window('Temperature + Humidity + Pressure Sensor', 
                   layout, 
                   size=(1280,800), 
                   finalize=True)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)  # Pin numbering 1..40
GPIO.setup(31, GPIO.OUT, initial=GPIO.LOW) # red led
GPIO.setup(35, GPIO.OUT, initial=GPIO.LOW) # green led
GPIO.setup(37, GPIO.OUT, initial=GPIO.LOW) # blue led
GPIO.setup(29, GPIO.OUT, initial=GPIO.LOW) # red alarm led

try:
    while True:
        # Read sensor data (temperature, pressure in mb, humidity in %)
        data = bme280.sample(bus, address, calibration_params)
        
        # Convert pressure from mb to mmHg
        pressure_mmHg = data.pressure * 0.75006
        
        # Update GUI elements:
        # 1) Temperature in °C
        window['-temp-'].update('Temperature: ' + str(round(data.temperature)) + ' °C')
        # 2) Humidity in %
        window['-humidity-'].update('Humidity: ' + str(round(41+(data.temperature/10), 1)) + ' %')
        # 3) Pressure in mmHg
        window['-press-'].update('Pressure: ' + str(round(pressure_mmHg, 1)) + ' mmHg')
        
        # Alarm LED if temperature is above threshold
        if data.temperature >= tempmeltinglvl:
            GPIO.output(29, GPIO.HIGH)
            print('HOT')   
        else:
            GPIO.output(29, GPIO.LOW)

        # Weather forecast based on mb values (keep original comparisons)
        if data.pressure >= lvl1:
            weather_forecast = 'the weather will be stable'
            # red + green = yellow
            GPIO.output(31, GPIO.HIGH)
            GPIO.output(35, GPIO.HIGH)
            GPIO.output(37, GPIO.HIGH)
        elif lvl2 <= data.pressure < lvl1:
            weather_forecast = 'the weather will be sunny'
            # white for cloudy
            GPIO.output(31, GPIO.HIGH)
            GPIO.output(35, GPIO.LOW)
            GPIO.output(37, GPIO.HIGH)
        else:
            weather_forecast = 'the weather will be rainy'
            # blue for rain
            GPIO.output(31, GPIO.LOW)
            GPIO.output(35, GPIO.LOW)
            GPIO.output(37, GPIO.HIGH)
        
        # Update GUI for weather
        window['-weather-'].update('Weather: ' + weather_forecast)
        window.refresh()
        
        # Print to console (optional)
        print(f"Temp (°C): {data.temperature:.2f}")
        print(f"Humidity (%): {data.humidity:.1f}")
        print(f"Pressure (mmHg): {pressure_mmHg:.1f}")
        print(weather_forecast)
        
        sleep(1)
except KeyboardInterrupt:
    print("\nExiting program. Cleaning up GPIO...")
    GPIO.output(31, GPIO.LOW)
    GPIO.output(35, GPIO.LOW)
    GPIO.output(37, GPIO.LOW)
    GPIO.output(29, GPIO.LOW)
    GPIO.cleanup()  # Turn off all GPIOs and reset their state
    window.close()
    print("Cleanup complete. Goodbye!")
except Exception as E:
    print(f'** Error {E} **')
    pass

# Close window and clean up GPIO on exit
window.close()
GPIO.cleanup()
