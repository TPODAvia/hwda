import PySimpleGUI as sg
import RPi.GPIO as GPIO
from time import sleep
import smbus2
import bme280

port = 1
address = 0x76
bus = smbus2.SMBus(port)
calibration_params = bme280.load_calibration_params(bus, address)

lvl1 = 1022.69 #Паскалей, или 767.2 мм.рт.ст.
lvl2 = 1009.14 #Паскалей, или 756.92 мм.рт.ст.
tempmeltinglvl = 30

layout = [[sg.Text('temperature:', size=(None, None), key='-temp-', auto_size_text=True, pad=((5,5),(200,0)), expand_x=True, font=('Calibri', 48), text_color = 'green', justification='center')],
[sg.Text('pressure:', size=(None, None), key='-press-', auto_size_text=True, pad=((5,5),(0,0)), expand_x=True, font=('Calibri', 48), text_color = 'violet', justification='center')],
[sg.Text('weather:', size=(None, None), key='-weather-', auto_size_text=True, pad=((5,5),(0,0)), expand_x=True, font=('Calibri', 48), text_color = 'orange', justification='center')]]

window = sg.Window('Temperature+Humidity+Pressure Sensor', layout, size=(1280,800), finalize=True)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD) #по простому номеру пина, от 1 до 40 
GPIO.setup(31, GPIO.OUT, initial=GPIO.LOW) #red led
GPIO.setup(35, GPIO.OUT, initial=GPIO.LOW) #green led
GPIO.setup(37, GPIO.OUT, initial=GPIO.LOW) #blue led
GPIO.setup(29, GPIO.OUT, initial=GPIO.LOW) #red alarm led

try:
    while True:
        #считываем данные
        data = bme280.sample(bus, address, calibration_params)
        #отображаем их в интерфейсе 
        window['-temp-'].update('temperature: ' + str(round(data.temperature)) + ' C')
        window['-press-'].update('pressure: ' + str(round(data.pressure)) + ' mb')
        #и на светодиодах
        if data.temperature >= tempmeltinglvl:
            GPIO.output(29, GPIO.HIGH)
            print('HOT')   
        else:
            GPIO.output(29, GPIO.LOW)
        if data.pressure >= lvl1:
            weather_forecast = 'the weather will be stable'
            #красный + зелёный = жёлтый
            GPIO.output(31, GPIO.HIGH)
            GPIO.output(35, GPIO.HIGH)
            GPIO.output(37, GPIO.LOW)
        elif data.pressure >= lvl2 and data.pressure < lvl1:
            weather_forecast = 'the weather will be cloudy'
            #белый для облачной погоды, облака белые обычно
            GPIO.output(31, GPIO.HIGH)
            GPIO.output(35, GPIO.HIGH)
            GPIO.output(37, GPIO.HIGH)
        else:
            weather_forecast = 'the weather will be rainy'
            #синий для дождливой погоды
            GPIO.output(31, GPIO.LOW)
            GPIO.output(35, GPIO.LOW)
            GPIO.output(37, GPIO.HIGH)
        window['-weather-'].update('weather: ' + weather_forecast)
        window.refresh()
        #и в консоли
        print(data.temperature)
        print(data.pressure)
        print(weather_forecast)
        sleep(1)

except Exception as E:
    print(f'** Error {E} **')
    pass
        
# закрываем окно и освобождаем используемые ресурсы
window.close()
GPIO.cleanup()
