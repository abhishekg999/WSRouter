# WSRouter

Have you ever wanted to host a WS server client side? No? Welp.


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
- Fill for WebSocket https://websockets.spec.whatwg.org/#the-websocket-interface
- Fill for WebSocketServer

Goal is eventually to be able to fill enough so that one can host a Socket.io server over WSRouter.


TODO: alot still

Why? IDK


# Protocol
Sender and reciever Session IDs are generated and maintained server side.
This are completely hidden from the consumer APIs.
```
HELLO:
TYPE [1 byte]
SENDER [16 BYTES]
RECIEVER [16 BYTES]
DATA [... BYTES]
```

Since the protocol is done over a complete websocket implementation anyways, this simplicity is sufficient.

