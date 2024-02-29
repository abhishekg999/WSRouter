"""
With WSRouter, we will have a simple protocol to imitate a LAN-like network.
Clients can connect to a channel and communicate within the channel.
The WSRouter will provide simple messages to get information about who is on the Network

We will keep a simple serialization format for now.

Structure:
[1 byte] PacketType
[16 bytes] Sender
[16 bytes] Receiver
[...] Data

"""

from __future__ import annotations
from enum import Enum
from dataclasses import dataclass
from uuid import UUID
import json

from session import SessionManager

ROUTER = str(UUID("00000000-0000-4000-8000-000000000000"))


class PacketType(Enum):
    # The first connection to the WS Router, perform Key Exchange and give session id
    HELLO = 0
    # The last message to the WS Router, close the connection
    GOODBYE = 1
    # Connect to a specific channel
    CONNECT = 2
    # Disconnect from a specific channel
    DISCONNECT = 3
    # Get information about who is in the current channel
    WHO = 4
    # Send a message to a specific channel
    MESSAGE = 5
    # Broadcast a message to all users in a channel
    BROADCAST = 6

    ## Router to Client
    WELCOME = 250
    OK = 254
    ERROR = 255


@dataclass
class Packet:
    type: PacketType
    sender: str
    receiver: str
    data: dict


def load_raw_UUID4(uuid: bytes) -> str:
    return str(UUID(bytes=uuid, version=4))


def serialize(packet: Packet) -> bytes:
    _type = packet.type.value.to_bytes(1, byteorder="big")
    _sender = UUID(packet.sender, version=4).bytes
    _receiver = UUID(packet.receiver, version=4).bytes
    _data = json.dumps(packet.data).encode("latin-1")
    return _type + _sender + _receiver + _data


def unserialize(data: bytes) -> Packet:
    if len(data) < 33:
        return None

    # 1 Byte
    _type, data = data[:1], data[1:]
    # 16 Bytes
    _sender, data = data[:16], data[16:]
    # 16 Bytes
    _reciever, data = data[:16], data[16:]
    _data = data

    print(f"Type: {_type}")
    print(f"Sender: {_sender}")
    print(f"Receiver: {_reciever}")
    print(f"Data: {_data}")

    _type = PacketType(int.from_bytes(_type, byteorder="big"))
    _sender = load_raw_UUID4(_sender)
    _reciever = load_raw_UUID4(_reciever)
    _data = json.loads(_data)
    return Packet(_type, _sender, _reciever, _data)


class Router:
    @staticmethod
    def handle(data: bytes) -> bytes:
        print(data)
        packet = unserialize(data)
        print(packet)
        if packet is None:
            return b""
        return Router._handle(packet)

    @staticmethod
    def _handle(packet: Packet) -> bytes:
        match (packet.type):
            case PacketType.HELLO:
                return Router._hello(packet)
            case PacketType.GOODBYE:
                return Router._goodbye(packet)
            case PacketType.CONNECT:
                return Router._connect(packet)
            case PacketType.DISCONNECT:
                return Router._disconnect(packet)
            case PacketType.WHO:
                return Router._who(packet)
            case PacketType.MESSAGE:
                return Router._message(packet)
            case PacketType.BROADCAST:
                return Router._broadcast(packet)
            case _:
                return b""

    @staticmethod
    def _hello(packet: Packet) -> bytes:
        """
        Expect:
            PacketType.HELLO
            Sender: Any
            Receiver: ROUTER
            Data: {Any}

        Return:
            PacketType.OK
            Sender: ROUTER
            Receiver: sid
            Data: {sid: str}
        """

        if packet.receiver != ROUTER:
            return b""

        sid = SessionManager.create_session()
        response = Packet(PacketType.WELCOME, ROUTER, sid, {"sid": sid})
        return serialize(response)

