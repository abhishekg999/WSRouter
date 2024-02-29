#!/usr/bin/env python

import asyncio
from websockets.sync.client import connect

from core import *


def hello():
    with connect("ws://localhost:8765") as websocket:
        data = p_create(
            PacketType.HELLO, "00000000-0000-0000-0000-000000000000", ROUTER, {}
        )
        websocket.send(data)
        message = unserialize(websocket.recv())
        sid = message.data["sid"]
        print(sid)

        data = p_create(PacketType.CREATE, sid, ROUTER, {})
        websocket.send(data)
        message = unserialize(websocket.recv())
        print(message)

        cid, deletion_token = message.data["cid"], message.data["deletion_token"]

        data = p_create(PacketType.CHANNELS, sid, ROUTER, {})
        websocket.send(data)
        message = unserialize(websocket.recv())
        print(message)

        channels = message.data["channels"]
        assert cid in channels

        data = p_create(
            PacketType.CONNECT,
            sid,
            ROUTER,
            {"cid": cid},
        )
        websocket.send(data)
        message = websocket.recv()
        print(unserialize(message))

        print(websocket.recv())
        print(websocket.recv())
        print(websocket.recv())


hello()
