# Client for connecting to the wifi network and server
import client

# For talking to the WS2811/WS2812(b) style RGB LED controllers:
from neopixel import NeoPixel

# Periodic tasks
from machine import Timer, Pin

# The LEDs are controlled by one data wire on Pin 15
# and there are 2 of them connected in the string:
LED_CONTROL_PIN = Pin(15)
NUM_LEDS = 2
LEDS = NeoPixel(LED_CONTROL_PIN, NUM_LEDS)

# Websocket URI to connect to
WS_URI = 'ws://pyleds.ngrok.io:80/socket'

# ESSID/Password for the wifi network
ESSID = 'ssid'
PASSWORD = 'password'

# Write some RGB values to the LEDs
def write_leds(rgb_vals):
    for index, (r, g, b) in enumerate(rgb_vals):
        LEDS[index] = (g, r, b) # pixels are defined in G R B order
    LEDS.write()

# Task to run on receiving data
def task(data):
    print(data)
    if 'leds' in data:
        write_leds(data['leds'])

def update(timer):
    client.send('update')

# Request updates every 5 seconds, just in case
timer = Timer(-1)
timer.init(period=5000, mode=Timer.PERIODIC, callback=update)

# Start the client
client.start(ESSID, PASSWORD, WS_URI, task)
