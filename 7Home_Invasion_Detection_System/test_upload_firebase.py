#!/usr/bin/env python3
import os
import pyrebase
from myenv import apiKey

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
# Testing Firebase Storage Upload
# ------------------------
try:
    # Create directory for storing images if it doesn't exist
    directory = '/home/pi/hwda/7Home_Invasion_Detection_System'
    os.makedirs(directory, exist_ok=True)

    # Simulate an image file (you can replace this with an actual image file path)
    filename = os.path.join(directory, 'image.png')
    
    # Create a dummy image file for testing
    with open(filename, 'wb') as f:
        f.write(os.urandom(1024))  # Create a random binary file to simulate an image
    
    print(f"Test image created: {filename}")

    # Upload to Firebase Storage
    storage.child(os.path.basename(filename)).put(filename)
    print(f"{filename} uploaded to Firebase storage.")

    # Retrieve the download URL
    file_url = storage.child(os.path.basename(filename)).get_url(None)
    print(f"Downloadable URL: {file_url}")

except Exception as E:
    print(f"** Error {E} **")
