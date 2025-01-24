#!/usr/bin/env python3
import PySimpleGUI as sg
import RPi.GPIO as GPIO
from time import sleep
from picamera2 import Picamera2 
import os

Movement_detected = False
camera = Picamera2()
camera_config = camera.create_preview_configuration(main={"size": (800, 600)})
camera.configure(camera_config)
camera.start()

layout = [
    [sg.Image(size=(800, 600), key='-image-', pad=((5,5),(5,5)), background_color='white', expand_x=True)],
    [sg.Text('', key='-movement-', size=(20,1), expand_x=True, font=('Calibri', 48), justification='center')]
]

window = sg.Window('Home Invasion Detection', layout, size=(1280,800), finalize=True)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)  # по простому номеру пина, от 1 до 40
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
            # работа с камерой
            try:
                directory = '/home/pi/hwda/7Home_Invasion_Detection_System'
                os.makedirs(directory, exist_ok=True)
                filename = os.path.join(directory, 'image.png')
                camera.capture_file(filename)
                print(f'Image saved to: {filename}')
                sleep(0.1)  # Ensure the file is fully written
                window['-image-'].update(filename=filename)
                window['-movement-'].update('Movement detected!', text_color='red')
                window.refresh()
                sleep(5)
            except Exception as E:
                print(f'** Error {E} **')
                pass  # что-то пошло не так
            Movement_detected = False  # Reset movement detection
        sleep(0.1)

except KeyboardInterrupt:
    window.close()
    camera.close()
    GPIO.cleanup()

# закрываем окно и освобождаем используемые ресурсы
window.close()
camera.close()
GPIO.cleanup()
