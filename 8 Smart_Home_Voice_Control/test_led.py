import neopixel
import board
import random
import time

# Configuration for NeoPixel
num_pixels = 12  # Number of LEDs in the strip
pixel_pin = board.D18  # GPIO18
ORDER = neopixel.GRB

# Initialize NeoPixel
pixels = neopixel.NeoPixel(pixel_pin, num_pixels,
                           brightness=0.1,
                           auto_write=False,
                           pixel_order=ORDER)

def lightsOn(color):
    """Set the NeoPixel to a specified color."""
    global pixels
    if color == "random":
        r = random.randrange(256)
        g = random.randrange(256)
        b = random.randrange(256)
    else:
        # color is a hex string like 'FF0000'
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
    pixels.fill((r, g, b))
    pixels.show()

# Test loop
try:
    while True:
        # Cycle through a few colors
        lightsOn('FF0000')  # Red
        time.sleep(1)
        lightsOn('00FF00')  # Green
        time.sleep(1)
        lightsOn('0000FF')  # Blue
        time.sleep(1)
        lightsOn('random')  # Random color
        time.sleep(1)
except KeyboardInterrupt:
    # Turn off LEDs on exit
    pixels.fill((0, 0, 0))
    pixels.show()
    print("Exiting and turning off LEDs.")
