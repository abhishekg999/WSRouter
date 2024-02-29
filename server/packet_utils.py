from core import Packet, PacketType, ROUTER, serialize


def p_create(packet_type: PacketType, sender: str, receiver: str, data: dict):
    return serialize(Packet(packet_type, sender, receiver, data))

def p_server_error_response(receiver: str, err: str, data: dict = {}):
    data = data.copy()
    data["error"] = err
    return p_create(PacketType.ERROR, ROUTER, receiver, data)