# For manipulating pins and the timer on the chip:
from machine import Pin

# For sleeping
import time

# For talking to the WS2811/WS2812 style RGB LED controllers:
from neopixel import NeoPixel

# For connecting to wifi:
import network

# For serialising data to send and receive
import json

# For connecting to a websocket
from websocketclient import connect as connect_to_websocket

# The LEDs are controlled by one signal wire on Pin 15
# and there are 2 of them connected in the string:
LED_CONTROL_PIN = Pin(15)
NUM_LEDS = 2
LEDS = NeoPixel(LED_CONTROL_PIN, NUM_LEDS)

# URI to connect to
WS_URI = 'ws://5e2c5840.ngrok.io:80/leds'

# ESSID/Password for the wifi network
ESSID = 'openlearning.com'
PASSWORD = 'AbsurdCyclicDungeonPipe'

# Write some RGB values to the LEDs
def write_leds(rgb_vals):
    for index, (r, g, b) in enumerate(rgb_vals):
        LEDS[index] = (g, r, b)
    LEDS.write()

# Connect to the wifi network access point
def connect_to_wifi(essid, password):
    wifi = network.WLAN(network.STA_IF)
    if not wifi.isconnected():
        print('Connecting to network...')
        wifi.active(True)
        wifi.connect(essid, password)
        while not wifi.isconnected():
            pass
    a, b, c, d = wifi.ifconfig()
    print(a ,b, c, d)

    # Set the DNS Server
    wifi.ifconfig((a, b, c, '8.8.8.8'))
    print('Connected to', essid)

    return wifi

# Send some data to the server
def send(websocket, data):
    websocket.send(json.dumps(data))

# Receive some data from the server
def recv(websocket):
    return json.loads(websocket.recv())

# Run this to start everything going
def start():
    wifi = None

    while True:
        # Connect to wifi
        if wifi is None or not wifi.isconnected():
            wifi = connect_to_wifi(ESSID, PASSWORD)

        try:
            # connect to websocket
            ws = connect_to_websocket(WS_URI)
            is_open = True
        except Exception as err:
            print('Unable to connect', err)
            is_open = False

        while is_open:
            try:
                data = recv(ws)
            except Exception as err:
                print('Unable to recv', err)
                is_open = False
                data = {}

            print(data)
            if 'leds' in data:
                write_leds(data['leds'])

        try:
            ws.close()
        except Exception as err:
            print('Unable to close', err)


start()
