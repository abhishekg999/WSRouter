import asyncio
from websockets.exceptions import ConnectionClosed
from websockets.server import serve
from os import environ
import random 

from core import Router
from SessionManager import SessionManager


HOST = environ.get("HOST", "localhost")
PORT = environ.get("PORT", 8765)

websocket_clients = set()

async def handler(websocket):
    websocket_clients.add(websocket)
    sid = SessionManager.create_session()
    print(f"Client {sid} connected")
    try:
        async for message in websocket:
            response = Router.handle(sid, message)
            if response:
                await websocket.send(response)
    except ConnectionClosed:
        pass  
    finally:
        websocket_clients.remove(websocket)
    print(f"Client {sid} disconnected")
    SessionManager.remove_session(sid)


async def foo(loop):
    """foo"""
    while True:
        for c in websocket_clients:
            await c.send("foo")
        await asyncio.sleep(5)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        server = serve(handler, HOST, PORT)  
        loop.run_until_complete(server)
        loop.run_until_complete(foo(loop))
        loop.run_forever()
    finally:
        loop.close()




