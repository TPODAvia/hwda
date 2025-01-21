import RPi.GPIO as GPIO
import time

# Set up GPIO mode
GPIO.setmode(GPIO.BOARD)

# Setup LEDs as output with initial state as LOW (off)
GPIO.setup(31, GPIO.OUT, initial=GPIO.LOW) # red led
GPIO.setup(35, GPIO.OUT, initial=GPIO.LOW) # green led
GPIO.setup(37, GPIO.OUT, initial=GPIO.LOW) # blue led
GPIO.setup(29, GPIO.OUT, initial=GPIO.LOW) # red alarm led

try:
    while True:
        # Turn on red LED
        GPIO.output(31, GPIO.HIGH)
        print("Red LED is ON")
        time.sleep(1)  # Wait for 1 second
        GPIO.output(31, GPIO.LOW)
        print("Red LED is OFF")
        time.sleep(0.5)  # Wait for half a second

        # Turn on green LED
        GPIO.output(35, GPIO.HIGH)
        print("Green LED is ON")
        time.sleep(1)  # Wait for 1 second
        GPIO.output(35, GPIO.LOW)
        print("Green LED is OFF")
        time.sleep(0.5)  # Wait for half a second

        # Turn on blue LED
        GPIO.output(37, GPIO.HIGH)
        print("Blue LED is ON")
        time.sleep(1)  # Wait for 1 second
        GPIO.output(37, GPIO.LOW)
        print("Blue LED is OFF")
        time.sleep(0.5)  # Wait for half a second

        # Turn on red alarm LED
        GPIO.output(29, GPIO.HIGH)
        print("Red Alarm LED is ON")
        time.sleep(1)  # Wait for 1 second
        GPIO.output(29, GPIO.LOW)
        print("Red Alarm LED is OFF")
        time.sleep(0.5)  # Wait for half a second

except KeyboardInterrupt:
    # Clean up GPIO settings before exiting
    GPIO.cleanup()
    print("GPIO cleaned up. Exiting program.")