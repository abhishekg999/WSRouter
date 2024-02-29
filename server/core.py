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
from typing import Literal
from enum import Enum
from dataclasses import dataclass
from uuid import UUID
import json

from ChannelManager import ChannelManager
from SessionManager import SessionManager

ROUTER = str(UUID("00000000-0000-4000-8000-000000000000"))
ChannelManager.create_channel()


class PacketType(Enum):
    # The first connection to the WS Router, perform Key Exchange and give session id
    HELLO = 0
    # The last message to the WS Router, close the connection
    GOODBYE = 1
    # Connect to a specific channel
    CONNECT = 2
    # Disconnect from a specific channel
    DISCONNECT = 3

    # Get available channels
    CHANNELS = 5

    # Create channel
    CREATE = 10
    # Delete channel
    DELETE = 11

    # 100 Range - Router specific while connected to channel
    # Get information about who is in the current channel
    WHO = 30

    # Send a message to a specific channel
    MESSAGE = 50
    # Broadcast a message to all users in a channel
    BROADCAST = 51


    # Incoming message from user in channel
    IN_MESSAGE = 100
    # Incoming broadcast from user in channel
    IN_BROADCAST = 101

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

    _type = PacketType(int.from_bytes(_type, byteorder="big"))
    _sender = load_raw_UUID4(_sender)
    _reciever = load_raw_UUID4(_reciever)
    _data = json.loads(_data)
    return Packet(_type, _sender, _reciever, _data)


from packet_utils import p_create, p_server_error_response
from utils import explode, ExplodeError, Err, T


# TODO: Make Managers return data, err response data
class Router:
    @staticmethod
    def handle(sid: str, data: bytes) -> bytes | None:
        packet = unserialize(data)
        if packet is None:
            return b""
        return Router._handle(sid, packet)

    @staticmethod
    def _handle(sid: str, packet: Packet) -> bytes | None:
        # Sender is handled by WS itself, overwrite this value.
        packet.sender = sid

        print("Recieved: ", packet)

        """
        Assumptions:
            - The packet is well formed
            - The sender is a valid session
        """
        match (packet.type):
            case PacketType.HELLO:
                return Router._hello(sid, packet)
            case PacketType.CONNECT:
                return Router._connect(sid, packet)
            case PacketType.DISCONNECT:
                return Router._disconnect(sid, packet)
            case PacketType.CHANNELS:
                return Router._channels(sid, packet)
            case PacketType.WHO:
                return Router._who(sid, packet)
            case PacketType.MESSAGE:
                return Router._message(sid, packet)
            case PacketType.BROADCAST:
                return Router._broadcast(sid, packet)
            case PacketType.CREATE:
                return Router._create(sid, packet)
            case PacketType.DELETE:
                return Router._delete(sid, packet)
            case _:
                return b""

    @staticmethod
    def _hello(sid: str, packet: Packet) -> bytes:
        return p_create(PacketType.WELCOME, ROUTER, sid, {"sid": sid})

    @staticmethod
    def _channels(sid: str, packet: Packet) -> bytes:
        return p_create(
            PacketType.OK, ROUTER, sid, {"channels": ChannelManager.get_channels()}
        )

    @staticmethod
    def _connect(sid: str, packet: Packet) -> bytes:
        if packet.receiver != ROUTER:
            return p_server_error_response(sid, "Invalid packet destination")

        cid = packet.data.get("cid")
        success, err = ChannelManager.add_client_to_channel(cid, sid)
        if not success:
            return p_server_error_response(sid, err)

        return p_create(PacketType.OK, ROUTER, sid, {"cid": cid})

    @staticmethod
    def _disconnect(sid: str, packet: Packet) -> bytes:
        if packet.receiver != ROUTER:
            return p_server_error_response(sid, "Invalid packet destination")

        cid = packet.data.get("cid")
        success, err = ChannelManager.remove_client_from_channel(sid, cid)
        if not success:
            return p_server_error_response(sid, err)

        return p_create(PacketType.OK, ROUTER, sid, {"cid": cid})

    @staticmethod
    def _create(sid: str, packet: Packet) -> bytes:
        if packet.receiver != ROUTER:
            return p_server_error_response(sid, "Invalid packet destination")

        password = packet.data.get("password", None)
        cid, deletion_token = ChannelManager.create_channel(password)
        return p_create(
            PacketType.OK, ROUTER, sid, {"cid": cid, "deletion_token": deletion_token}
        )

    @staticmethod
    def _delete(sid: str, packet: Packet) -> bytes:
        if packet.receiver != ROUTER:
            return p_server_error_response(sid, "Invalid packet destination")

        cid = packet.data.get("cid")
        token = packet.data.get("token")
        success, err = ChannelManager.remove_channel(cid, token)
        if not success:
            return p_server_error_response(sid, err)

        return p_create(PacketType.OK, ROUTER, sid, {"cid": cid})

    @staticmethod
    def _who(sid: str, packet: Packet) -> bytes:
        if packet.receiver != ROUTER:
            return p_server_error_response(sid, "Invalid packet destination")

        channel = SessionManager.get_session(sid).cid
        if channel is None:
            return p_server_error_response(sid, "Invalid channel")

        return p_create(
            PacketType.OK,
            ROUTER,
            sid,
            {"clients": list(ChannelManager.get_channel(channel).clients)},
        )

    """
    These packets route directly to a client. 
    """
    @staticmethod
    def _message(sid: str, packet: Packet) -> bytes:
        cid = SessionManager.get_session(sid).cid
        if cid is None:
            return p_server_error_response(sid, "User is not in a channel")
        
        channel = ChannelManager.get_channel(cid)
        if channel is None:
            return p_server_error_response(sid, "Invalid channel")
        
        # Forward the message to the channel
        channel.packet_queue.append(packet)     
        
        # Do not return anything to the client