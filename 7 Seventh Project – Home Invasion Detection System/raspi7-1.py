import PySimpleGUI as sg
import RPi.GPIO as GPIO
from time import sleep
from picamera import PiCamera 
import os

Movement_detected = False
camera = PiCamera(resolution=(800,600))
camera.shutter_speed = 60000 #выдержка, или скорость затвора в микросекундах
camera.iso = 200 #яркость снимка

layout = [[sg.Image(size=(800, 600), key='-image-', pad=((5,5),(5,5)), background_color='white', expand_x=True)],
        [sg.Text('', key='-movement-', size=(20,1), expand_x=True, font=('Calibri', 48), justification='center')]]

window = sg.Window('Home Invasion Detection', layout, size=(1280,800), finalize=True)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD) #по простому номеру пина, от 1 до 40 
GPIO.setup(7, GPIO.IN)

def DetectedCallback(channel):
    global Movement_detected
    Movement_detected = True
    print('Movement detected!') 
    
    
GPIO.add_event_detect(7, GPIO.RISING, callback=DetectedCallback)

try:
    while True:
        if not Movement_detected:
            window['-movement-'].update('Waiting for movement…', text_color='white')
            window.refresh()
        if Movement_detected:            
#работа с камерой
            try:
                filename = os.path.join('image.png')
                camera.capture(filename)
                window['-image-'].update(filename = filename)
    window['-movement-'].update('Movement detected!',    text_color='red')
                window.refresh()
                sleep(5)
            except Exception as E:
                print(f'** Error {E} **')
                pass        # что-то пошло не так
Movement_detected = False
#работа с Firebase
            #... пока нет
        
        sleep(0.1)

except KeyboardInterrupt:
    window.close()
    camera.close()
    GPIO.cleanup()


# закрываем окно и освобождаем используемые ресурсы
window.close()
camera.close()
GPIO.cleanup()
