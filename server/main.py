import asyncio
from websockets.server import serve
from os import environ

from core import Router
from session import SessionManager


HOST = environ.get("HOST", "localhost")
PORT = environ.get("PORT", 8765)

async def handler(websocket):
    sid = SessionManager.create_session()
    print(f"Client {sid} connected")
    async for message in websocket:
        response = Router.handle(sid, message)
        await websocket.send(response)
    
    print(f"Client {sid} disconnected")
    SessionManager.remove_session(sid)

async def main():
    async with serve(handler, HOST, PORT):
        await asyncio.Future() 

asyncio.run(main())

