import PySimpleGUI as sg
import RPi.GPIO as GPIO
from time import sleep
from picamera import PiCamera 
import os

servo_angle = 0
step = 10
min_angle = 0
max_angle = 160
camera = PiCamera(resolution=(800,600))
camera.shutter_speed = 60000 #выдержка, или скорость затвора в микросекундах
camera.iso = 200 #яркость снимка

layout = [[sg.Image(size=(800, 600), key='-image-', pad=((5,5),(5,5)), background_color='white', expand_x=True)],
        [sg.Button('LEFT', key='-left-', size=(4,1), enable_events=True, expand_x=True, font=('Calibri', 48)), 
         sg.Button('TAKE PICTURE', key='-pic-', size=(12,1), enable_events=True, expand_x=True, font=('Calibri', 48)),
         sg.Button('RIGHT', key='-right-', size=(5,1), enable_events=True, expand_x=True, font=('Calibri', 48))]]

window = sg.Window('Spying Eye', layout, size=(1280,800), finalize=True)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD) #по простому номеру пина, от 1 до 40 
GPIO.setup(12, GPIO.OUT)
servo = GPIO.PWM(12, 100) #открыли 12 пин для ШИМ с частотой 100Гц
servo.start(50) #duty cycle = 50%
servo.ChangeFrequency(50) #поменяли частоту на 50 Гц
servo.ChangeDutyCycle(75) #а duty cycle на 75%

def set_angle(servo1, angle):
    global servo
    duty = angle / 18 + 2
    GPIO.output(servo1, True)
    servo.ChangeDutyCycle(duty)
    sleep(1)
    GPIO.output(servo1, False)
    servo.ChangeDutyCycle(0)
    
try:
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        # на всякий случай
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        #нажата кнопка LEFT 
        if event == '-left-':
            servo_angle = servo_angle - step
            if servo_angle < min_angle:
                servo_angle = min_angle
            set_angle(12, servo_angle)
        #нажата кнопка RIGHT
        elif event == '-right-':
            servo_angle = servo_angle + step
            if servo_angle > max_angle:
                servo_angle = max_angle
            set_angle(12, servo_angle)
        elif event == '-pic-':
            #работа с камерой
            try:
                filename = os.path.join('./', 'image.png')
                camera.capture(filename)
                window['-image-'].update(filename = filename)
                window.refresh()
            except Exception as E:
                print(f'** Error {E} **')
                pass        # что-то пошло не так
        
        sleep(0.1)

except KeyboardInterrupt:
    window.close()
    camera.close()
    servo.stop()
    GPIO.cleanup()    
    
# закрываем окно и освобождаем используемые ресурсы
window.close()
camera.close()
servo.stop()
GPIO.cleanup()
