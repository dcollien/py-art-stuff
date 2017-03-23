import asyncio

from sanic import Sanic
from sanic.response import file, json, HTTPResponse

from websockets.protocol import CLOSED

from ujson import loads, dumps
from uuid import uuid4 as random_id

app = Sanic(__name__)

# Globals for state (for a proof of concept)
# We will make classes for this stuff later
LEDS = [(255, 255, 0), (255, 0, 255)]
connections = {}

def _process_data(data):
    global LEDS

    did_change = False
    if isinstance(data, dict) and 'set' in data:
        setter = data['set']
        for key, val in setter.items():
            LEDS[int(key)] = val
        did_change = True

    return did_change

def _send_to_all(data):
    closed_socket_ids = []
    tasks = []
    for ws_id, open_ws in connections.items():
        if open_ws.state == CLOSED:
            closed_socket_ids.append(ws_id)
        else:
            print('to', ws_id)
            tasks.append(open_ws.send(dumps(data)))

    for closed_ws_id in closed_socket_ids:
        del connections[closed_ws_id]

    return asyncio.gather(*tasks)

app.static('/static', './static')

@app.route('/')
async def index(request):
    return await file('./static/index.html')

@app.route('/ajax', methods=['POST'])
async def ajax(request):
    data = request.json
    _process_data(data)
    return json({'leds': LEDS})

@app.websocket('/socket')
async def socket(request, ws):
    socket_id = random_id()
    connections[socket_id] = ws

    print('Opened: ', socket_id)

    # Send LEDs immediately
    data = {'leds': LEDS}
    await ws.send(dumps(data))

    while True:
        raw_data = await ws.recv()
        data = loads(raw_data)
        print('Received: ', socket_id, data)
        did_change = _process_data(data)

        data = {'leds': LEDS}
        print('Sending: ', socket_id, data)

        if did_change:
            await _send_to_all(data)
        else:
            await ws.send(dumps(data))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8001)
