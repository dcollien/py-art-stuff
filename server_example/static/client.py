from browser import document as doc
from browser import ajax, console, timer, window
import json
from datetime import datetime

try:
  from browser import websocket
  USE_WEBSOCKETS = websocket.supported
except ImportError:
  USE_WEBSOCKETS = False


""" Constants """
# How to connect to the server
HTTP_URL = 'http://localhost:8000/leds-api'
WS_URL = 'ws://localhost:8000/leds'

# Start with this colour before connecting
INIT_COLOUR = (255, 255, 255)


class ColourChooserClient(object):
  def __init__(self):
    # If using a websocket, this is where it's stored
    self.socket = None

    # Currently displayed colours on the screen
    self.current_colours = [INIT_COLOUR, INIT_COLOUR]

    # The colours last received from the server
    self.last_received_colours = [INIT_COLOUR, INIT_COLOUR]

    def picker_change(event):
      """ Update the current colour state data when inputs are changed """

      hex_value = event.srcElement.value
      index = int(event.srcElement.id.replace('picker', ''))
      self.set_colour_hex(index, hex_value)

    # Bind change events to the colour pickers
    doc['picker0'].bind('change', picker_change)
    doc['picker1'].bind('change', picker_change)

  def connect(self):
    if USE_WEBSOCKETS:
      # Set up websockets
      self.try_ws_connect()
    else:
      # Poll every second if websockets aren't supported
      console.log('No websockets. Polling via AJAX.')
      self.send('update')
      timer.set_interval(lambda: self.send('update'), 1000)

  def try_ws_connect(self):
    def on_message(event):
      self.recv(json.loads(event.data))

    def on_open(event):
      console.log('connected.')
      self.send('update')

    def wait_retry(event):
      console.log('waiting 5s...')
      timer.set_timeout(attempt, 5000)

    def attempt():
      console.log('connecting...')
      self.socket = websocket.WebSocket(WS_URL)
      self.socket.bind('message', on_message)
      self.socket.bind('open', on_open)
      self.socket.bind('close', wait_retry)
      self.socket.bind('error', lambda event: console.log(event))

    attempt()

  def update_picker(self, index, colour):
    """ Update the selected colour of a colour picker """

    picker = doc['picker' + str(index)]
    picker.style.backgroundColor = '#%02x%02x%02x' % colour

  def recv(self, data):
    """ Receive data from the server """

    if 'leds' in data:
      # Update the colours with data sent from the server
      colours = data['leds']

      # Keep only the colours which are different to
      # the last time colours were received, to prevent
      # any changed (but not saved) colours from resetting
      new_colours = {
        i: (r, g, b)
        for i, (r, g, b) in enumerate(colours)
        if self.last_received_colours[i] != (r, g, b)
      }

      # Update these colours in both the UI and the state
      for i, colour in new_colours.items():
        self.update_picker(i, colour)
        self.current_colours[i] = colour

      self.last_received_colours = [tuple(colour) for colour in colours]

  def send(self, data):
    """ Send data to the server (via websocket or AJAX) """

    if USE_WEBSOCKETS:
      self.socket.send(json.dumps(data))
    else:
      req = ajax.Ajax(HTTP_URL, method='POST')

      @req.complete
      def success():
        if req.status == 200 or req.status == 0:
          data = json.loads(req.text)
          self.recv(data)

      req.set_header('content-type', 'application/json')
      req.send(json.dumps(data))

  def send_colours(self):
    """ Package up the current colours and send them to the server """

    colours_to_set = {
      str(i): colour
      for i, colour in enumerate(self.current_colours)
      if colour != self.last_received_colours[i]
    }

    if len(colours_to_set) > 0:
      self.send({'set': colours_to_set})

  def set_colour_hex(self, index, hex_value):
    """ Set a colour and send it to the server """

    _, r0, r1, g0, g1, b0, b1 = hex_value
    r = int(r0 + r1, 16)
    g = int(g0 + g1, 16)
    b = int(b0 + b1, 16)

    self.current_colours[index] = (r, g, b)

    self.send_colours()

client = ColourChooserClient()
client.connect()
