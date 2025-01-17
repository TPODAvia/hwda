import PySimpleGUI as sg
import RPi.GPIO as GPIO
from time import sleep
from picamera import PiCamera 
import os
import json
import requests
import google.auth.transport.requests
from google.oauth2 import service_account
import pyrebase

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

PROJECT_ID = 'yet-another-motion-detector' #<YOUR-PROJECT-ID>
BASE_URL = 'https://fcm.googleapis.com'
FCM_ENDPOINT = 'v1/projects/' + PROJECT_ID + '/messages:send'
FCM_URL = BASE_URL + '/' + FCM_ENDPOINT
SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']

def _get_access_token():
  credentials = service_account.Credentials.from_service_account_file(
    'service-account.json', scopes=SCOPES)
  request = google.auth.transport.requests.Request()
  credentials.refresh(request)
  return credentials.token

def _send_fcm_message(fcm_message):
  headers = {
    'Authorization': 'Bearer ' + _get_access_token(),
    'Content-Type': 'application/json; UTF-8',
  }
  resp = requests.post(FCM_URL, data=json.dumps(fcm_message), headers=headers)
  if resp.status_code == 200:
    print('Message sent to Firebase for delivery, response:')
    print(resp.text)
  else:
    print('Unable to send message to Firebase')
    print(resp.text)

def _build_common_message():
  return {
    'message': {
      'topic': 'alarm',
      'data': {
        'message': 'Alarm! Someone is at home!'        
      }
    }
  }

firebaseConfig = {
  'apiKey': "your_api_key",
  'authDomain': "your_projectId.firebaseapp.com",
  'databaseURL': "your_database_url",
  'projectId': "your_projectId",
  'storageBucket': "your_projectId.appspot.com",
  'messagingSenderId': "your_sender_id",
  'appId': "your_app_id",
  'measurementId': "your_measurement_id"
}

firebase = pyrebase.initialize_app(firebaseConfig)
storage = firebase.storage()

try:
    while True:
        if not Movement_detected:
            window['-movement-'].update('Waiting for movement…', text_color='white')
            window.refresh()
        if Movement_detected:          
            Movement_detected = False
            try:
                #работа с камерой
                filename = os.path.join('image.png')
                camera.capture(filename)
                window['-image-'].update(filename = filename)
                window['-movement-'].update('Movement detected!',    text_color='red')
                window.refresh()
                #работа с Firebase
                storage.child(filename).put(filename)
                print(filename + ' sent to firebase storage')
                common_message = _build_common_message()
                print('FCM request body for message using common notification object:')
                print(json.dumps(common_message, indent=2))
                _send_fcm_message(common_message)
                sleep(30)
                
            except Exception as E:
                print(f'** Error {E} **')
                pass        # что-то пошло не так
        
        sleep(1)

except KeyboardInterrupt:
    camera.close()
    window.close()
    GPIO.cleanup()

# закрываем окно и освобождаем используемые ресурсы
camera.close()
window.close()
GPIO.cleanup()