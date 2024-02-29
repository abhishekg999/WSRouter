#!/usr/bin/env python

import asyncio
from websockets.sync.client import connect

from core import PacketType, Packet, serialize, unserialize, ROUTER

def hello():
    with connect("ws://localhost:8765") as websocket:
        data = Packet(PacketType.HELLO, "00000000-0000-0000-0000-000000000000", ROUTER, {})
        websocket.send(serialize(data))
        message = websocket.recv()
        print(unserialize(message))

hello()