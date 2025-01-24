#!/usr/bin/env python3
import PySimpleGUI as sg
import RPi.GPIO as GPIO
from time import sleep
from picamera2 import Picamera2
import os
import json
import requests
import google.auth.transport.requests
from google.oauth2 import service_account
import pyrebase
from myenv import apiKey # Create the myenv.py yourself
# ------------------------
# Global Variables
# ------------------------
Movement_detected = False

# Initialize Picamera2
camera = Picamera2()
camera_config = camera.create_preview_configuration(main={"size": (800, 600)})
camera.configure(camera_config)
camera.start()
sleep(2)                      # Give some time for the camera to adjust

# ------------------------
# PySimpleGUI Layout
# ------------------------
layout = [
    [sg.Image(size=(800, 600), key='-image-', pad=((5,5),(5,5)), background_color='white', expand_x=True)],
    [sg.Text('', key='-movement-', size=(20,1), expand_x=True, font=('Calibri', 48), justification='center')]
]

window = sg.Window('Home Invasion Detection', layout, size=(1280,800), finalize=True)

# ------------------------
# GPIO Setup
# ------------------------
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)  # по простому номеру пина, от 1 до 40
GPIO.setup(7, GPIO.IN)

def DetectedCallback(channel):
    global Movement_detected
    Movement_detected = True
    print('Movement detected!')

GPIO.add_event_detect(7, GPIO.RISING, callback=DetectedCallback)

# ------------------------
# Firebase Messaging Setup
# ------------------------
PROJECT_ID = 'yet-another-motion-detec-fef1e'
BASE_URL = 'https://fcm.googleapis.com'
FCM_ENDPOINT = f'v1/projects/{PROJECT_ID}/messages:send'
FCM_URL = BASE_URL + '/' + FCM_ENDPOINT
# SCOPES = ['https://www.googleapis.com/auth/firebase.messaging'] this is deprecarted url
SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
def _get_access_token():
    credentials = service_account.Credentials.from_service_account_file(
        '/home/pi/hwda/7Home_Invasion_Detection_System/service-account.json', scopes=SCOPES
    )
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    return credentials.token

def _send_fcm_message(fcm_message):
    print("Access Token:", _get_access_token)
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

# ------------------------
# Firebase Storage Setup
# ------------------------
firebaseConfig = {
    'apiKey': apiKey,
    'authDomain': "yet-another-motion-detec-fef1e.firebaseapp.com",
    'databaseURL': "https://yet-another-motion-detec-fef1e-default-rtdb.firebaseio.com",
    'projectId': "yet-another-motion-detec-fef1e",
    'storageBucket': "yet-another-motion-detec-fef1e.firebasestorage.app",
    'messagingSenderId': "580803193118",
    'appId': "1:580803193118:web:604699e6a3f777b1d4010f",
}

firebase = pyrebase.initialize_app(firebaseConfig)
storage = firebase.storage()

# ------------------------
# Main Loop
# ------------------------
try:
    while True:
        # If no movement, just show a waiting message
        if not Movement_detected:
            window['-movement-'].update('Waiting for movement…', text_color='white')
            window.refresh()

        # If movement is detected, capture image, update GUI, upload to Firebase, etc.
        if Movement_detected:
            # Reset the flag immediately to avoid re-triggering in the same cycle
            Movement_detected = False

            try:
                # Create directory for storing images if it doesn't exist
                directory = '/home/pi/hwda/7Home_Invasion_Detection_System'
                os.makedirs(directory, exist_ok=True)

                # Capture file
                filename = os.path.join(directory, 'image.png')
                print("Capturing image...")
                camera.capture_file(filename)
                print(f'Image saved to: {filename}')

                # Update PySimpleGUI window with the captured image
                window['-image-'].update(filename=filename)
                window['-movement-'].update('Movement detected!', text_color='red')
                window.refresh()

                # Upload to Firebase Storage
                storage.child(os.path.basename(filename)).put(filename)
                print(filename + ' sent to Firebase storage')

                # Send FCM message
                common_message = _build_common_message()
                print('FCM request body for message using common notification object:')
                print(json.dumps(common_message, indent=2))
                _send_fcm_message(common_message)

                # Delay so we don’t spam too many captures/notifications
                sleep(30)

            except Exception as E:
                print(f'** Error {E} **')
                pass

        sleep(1)

except KeyboardInterrupt:
    print("Terminating program...")

finally:
    camera.stop_preview()  # Stop camera preview if you started it
    camera.close()
    window.close()
    GPIO.cleanup()
