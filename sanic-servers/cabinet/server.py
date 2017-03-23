import asyncio

from sanic import Sanic
from sanic.response import file, json, HTTPResponse

from websockets.protocol import CLOSED

from ujson import loads, dumps
from uuid import uuid4 as random_id

app = Sanic(__name__)

connections = dict()
awaiting_unlock = {}

def _list_connections():
    global connections

    closed_socket_ids = [
        ws_id
        for ws_id, open_ws in connections.items()
        if open_ws.state == CLOSED
    ]

    if len(closed_socket_ids) > 0:
        print('Cleaning up', closed_socket_ids)
        for closed_ws_id in closed_socket_ids:
            del connections[closed_ws_id]

    return connections.items()



def _send_to_ids(ids, data):
    print('sending to', ids, data)
    closed_socket_ids = []
    tasks = []
    ids = set(ids)
    for ws_id, open_ws in _list_connections():
        if ws_id in ids:
            print('sending to', ws_id)
            json_data = dumps(data)
            tasks.append(open_ws.send(json_data))

    return asyncio.gather(*tasks)

def _send_to_ws(ws_id, data):
    print('sending to', ws_id)
    open_ws = connections[ws_id]
    return open_ws.send(dumps(data))

async def _process_data(socket_id, data):
    global awaiting_unlock

    if data == 'button':
        print(awaiting_unlock)
        # find all cabinets waiting to be unlocked
        # and unlock them (unless it's this one)
        unlock_ids = [
            ws_id
            for ws_id, ws_sock in _list_connections()
            if awaiting_unlock[ws_id] and ws_id != socket_id
        ]

        if len(unlock_ids) > 0:
            # There's some cabinets waiting, unlock them
            await _send_to_ids(unlock_ids, 'unlock')
            for ws_id in unlock_ids:
                awaiting_unlock[ws_id] = False
        else:
            # No cabinets waiting, send out a request
            awaiting_unlock[socket_id] = True
            other_connections = [
                ws_id
                for ws_id, ws_sock in _list_connections()
                if ws_id != socket_id
            ]
            await _send_to_ids(other_connections, 'request')

    elif data == 'update':
        # Update requested, tell how many are pending
        num_pending = len(ws_id for ws_id, ws_sock in _list_connections() if awaiting_unlock[ws_id])
        await _send_to_ws(socket_id, {
            'pending': num_pending
        })

app.static('/static', './static')

@app.route('/')
async def index(request):
    return await file('./static/index.html')

@app.websocket('/socket')
async def socket(request, ws):
    socket_id = random_id()
    connections[socket_id] = ws
    awaiting_unlock[socket_id] = False

    print('Connected:', socket_id)

    while True:
        raw_data = await ws.recv()
        data = loads(raw_data)
        print('Received: ', socket_id, data)
        await _process_data(socket_id, data)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
