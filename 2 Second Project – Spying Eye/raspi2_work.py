import PySimpleGUI as sg
import RPi.GPIO as GPIO
from time import sleep
from picamera2 import Picamera2, PreviewConfiguration
import os

servo_angle = 0
step = 10
min_angle = 0
max_angle = 160

# Initialize Picamera2
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (800, 600)})
picam2.configure(config)
picam2.start()

layout = [[sg.Image(size=(800, 600), key='-image-', pad=((5,5),(5,5)), background_color='white', expand_x=True)],
        [sg.Button('LEFT', key='-left-', size=(4,1), enable_events=True, expand_x=True, font=('Calibri', 48)), 
         sg.Button('TAKE PICTURE', key='-pic-', size=(12,1), enable_events=True, expand_x=True, font=('Calibri', 48)),
         sg.Button('RIGHT', key='-right-', size=(5,1), enable_events=True, expand_x=True, font=('Calibri', 48))]]

window = sg.Window('Spying Eye', layout, size=(1280,800), finalize=True)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD) # Use BOARD numbering scheme
GPIO.setup(12, GPIO.OUT)
servo = GPIO.PWM(12, 50) # Open pin 12 for PWM at 50Hz
servo.start(7.5) # Neutral position (90 degrees)

def set_angle(servo1, angle):
    duty = angle / 18 + 2
    GPIO.output(servo1, True)
    servo.ChangeDutyCycle(duty)
    sleep(1)
    GPIO.output(servo1, False)
    servo.ChangeDutyCycle(0)

try:
    while True:
        event, values = window.read(timeout=10)
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        
        if event == '-left-':
            servo_angle -= step
            if servo_angle < min_angle:
                servo_angle = min_angle
            set_angle(12, servo_angle)
        elif event == '-right-':
            servo_angle += step
            if servo_angle > max_angle:
                servo_angle = max_angle
            set_angle(12, servo_angle)
        elif event == '-pic-':
            # Capture image using Picamera2
            try:
                filename = os.path.join('./', 'image.jpg')
                picam2.capture_file(filename)
                window['-image-'].update(filename=filename)
                window.refresh()
            except Exception as E:
                print(f'** Error {E} **')
                pass

except KeyboardInterrupt:
    pass

# Cleanup resources
window.close()
picam2.stop()
picam2.close()
servo.stop()
GPIO.cleanup()
