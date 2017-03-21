# For manipulating pins and the timer on the chip:
from machine import Pin

# For connecting to wifi:
import network

# For serialising data to send and receive
import json

# For connecting to a websocket
from websocketclient import connect as connect_to_websocket

# Web socket
SOCKET = None

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
def send(data):
    if SOCKET is not None:
        SOCKET.send(json.dumps(data))
    else:
        print("Not yet connected.")

# Receive some data from the server
def _recv():
    return json.loads(SOCKET.recv())

# Run this to start everything going
def start(essid, password, ws_uri, task):
    global SOCKET

    wifi = None

    while True:
        # Connect to wifi
        if wifi is None or not wifi.isconnected():
            wifi = connect_to_wifi(essid, password)

        try:
            # connect to websocket
            SOCKET = connect_to_websocket(ws_uri)
            is_open = True
        except Exception as err:
            print('Unable to connect', err)
            is_open = False

        while is_open:
            try:
                data = _recv()
            except Exception as err:
                print('Unable to recv', err)
                is_open = False
                data = {}

            task(data)

        try:
            SOCKET.close()
        except Exception as err:
            print('Unable to close', err)
