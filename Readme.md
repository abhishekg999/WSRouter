# WSRouter

WSRouter intends to be eventually usable as a Websocket Server implementation that can be run on a client.
The WSRouter can be hosted once, and can reliably transfer data between multiple servers.

Backend
---
- Python backend using websockets
- Custom and simple serialization
- Overall processes:
1. On connect to WSRouter, the server will establish an individual connection with the client. 
2. The WSRouter buffer should be flexible enough to send raw data. This means that in this raw data it should be able to send generic websocket packets that are used by SocketIO, etc.


Frontend
---
- Basic JS API
- Fill for WebSocket
- Fill for WebSocketServer

Goal is eventually to be able to fill enough so that one can host a Socket.io server over WSRouter.


TODO: alot still

Why? IDK