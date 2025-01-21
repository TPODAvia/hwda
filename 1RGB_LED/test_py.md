import RPi.GPIO as GPIO
from time import sleep

# Initialize the state for the buttons
REDpressed = False
GREENpressed = False
BLUEpressed = False

# Set up GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering

# Set up LEDs
GPIO.setup(35, GPIO.OUT, initial=GPIO.LOW)  # Red LED on pin 35
GPIO.setup(36, GPIO.OUT, initial=GPIO.LOW)  # Green LED on pin 36
GPIO.setup(37, GPIO.OUT, initial=GPIO.LOW)  # Blue LED on pin 37

# Set up buttons
GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)   # Red button on pin 7
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Green button on pin 11
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Blue button on pin 13

# Callback function for the red button
def REDcallback(channel):
    if GPIO.input(7) == GPIO.HIGH:  # Ensure callback is triggered by the correct button press
        global REDpressed
        REDpressed = not REDpressed
        GPIO.output(35, REDpressed)
        GPIO.output(36, 0)
        GPIO.output(37, 0)
        print('RED LED ' + ('ON' if REDpressed else 'OFF'))

# Callback function for the green button
def GREENcallback(channel):
    if GPIO.input(11) == GPIO.HIGH:  # Ensure callback is triggered by the correct button press
        global GREENpressed
        GREENpressed = not GREENpressed
        GPIO.output(36, GREENpressed)
        GPIO.output(35, 0)
        GPIO.output(37, 0)
        print('GREEN LED ' + ('ON' if GREENpressed else 'OFF'))

# Callback function for the blue button
def BLUEcallback(channel):
    if GPIO.input(13) == GPIO.HIGH:  # Ensure callback is triggered by the correct button press
        global BLUEpressed
        BLUEpressed = not BLUEpressed
        GPIO.output(37, BLUEpressed)
        GPIO.output(35, 0)
        GPIO.output(36, 0)
        print('BLUE LED ' + ('ON' if BLUEpressed else 'OFF'))

# Set up event detection for the buttons
GPIO.add_event_detect(7, GPIO.RISING, callback=REDcallback, bouncetime=300)
GPIO.add_event_detect(11, GPIO.RISING, callback=GREENcallback, bouncetime=300)
GPIO.add_event_detect(13, GPIO.RISING, callback=BLUEcallback, bouncetime=300)

# Main loop
try:
    while True:
        sleep(0.01)  # Small delay to prevent high CPU usage
except KeyboardInterrupt:
    print("\nExiting program...")

finally:
    # Clean up GPIO resources
    GPIO.cleanup()