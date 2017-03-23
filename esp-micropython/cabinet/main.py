# Client for connecting to the wifi network and server
import client

# Pin IO and Periodic tasks
from machine import Pin, Timer, unique_id

# Websocket URI to connect to
WS_URI = 'ws://f7461512.ngrok.io:80/socket'

# ESSID/Password for the wifi network
ESSID = 'ssid'
PASSWORD = 'password'

# Mapping of internal pin number to labels
D3 = 0
D4 = 2
D8 = 15

# Lock is connected to D3
LOCK = Pin(D3, Pin.OUT)
LOCK.low()

# Indicator is connected to D4
INDICATOR = Pin(D4, Pin.OUT)
INDICATOR.low()

# Button is connected to D8
BUTTON = Pin(D8, Pin.IN, Pin.PULL_UP)

# Interval at which the timer task runs (millis)
TIMER_INTERVAL = 100

# Number of ticks to wait with the lock open
# (OPEN_DELAY * TIMER_INTERVAL / 1000) seconds
OPEN_DELAY = 20

PRESSED = 1

# Program global state
is_button_down     = False
is_open            = False
is_request_pending = False
ticks_until_locked = 0

# Task to run on receiving data
def receive(data):
    global is_request_pending, is_open, ticks_until_locked
    print('RECEIVED', data)

    if data == 'unlock':
        # Unlock signal received
        is_open = True
        ticks_until_locked = OPEN_DELAY
    elif data == 'request':
        # Turn on the indicator
        is_request_pending = True
        print('Request Pending', is_request_pending)


def update(timer):
    global is_button_down, is_open, ticks_until_locked, is_request_pending

    button_state = BUTTON.value()

    if button_state == PRESSED:
        # button is currently down
        if not is_button_down:
            print('Button Pressed')
            # button wasn't down: change event
            # send the button signal to the server
            is_button_down = True
            client.send('button')

            # turn on the indicator (momentarily)
            # while the button is down
            INDICATOR.high()
    else:
        # button is currently up
        if is_button_down:
            print('Button Released')
            # button was down: change event
            is_button_down = False
            is_request_pending = False
            INDICATOR.low()

    if is_open:
        LOCK.high()

        # Lock is open, the timer will close it
        if ticks_until_locked == 0:
            is_open = False
            LOCK.low() # lock the cabinet
        else:
            ticks_until_locked -= 1

    if is_request_pending:
        INDICATOR.high()

# Perform updates every TIMER_INTERVAL millis
timer = Timer(-1)
timer.init(period=TIMER_INTERVAL, mode=Timer.PERIODIC, callback=update)

# Start the client
client.start(ESSID, PASSWORD, WS_URI, receive)
