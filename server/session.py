from uuid import uuid4

session = {}

class Client:
    def __init__(self) -> None:
        self.sid = str(uuid4())
        # TODO: Implement deletion token
        self.deletion_token = None

class SessionManager:
    @staticmethod
    def create_session():
        client = Client()
        session[client.sid] = client
        return client.sid
    
    @staticmethod
    def get_session(sid):
        return session.get(sid)
    
    @staticmethod
    def remove_session(sid):
        session.pop(sid)

    def is_valid_session(sid):
        return sid in session


class Channel:
    def __init__(self, password=None) -> None:
        self.cid = str(uuid4())
        self.password = password
        self.clients = set()
    
    def add_client(self, sid):
        self.clients.add(sid)
    
    def remove_client(self, sid):
        self.clients.remove(sid)

channels = {}

class ChannelManager: 
    @staticmethod
    def create_channel(password=None):
        channel = Channel(password)
        channels[channel.cid] = channel
        return channel.cid
    
    @staticmethod
    def get_channel(cid):
        return channels.get(cid)
    
    def get_channels():
        return list(channels.keys())
    
    @staticmethod
    def remove_channel(cid, token=None):
        if token != channels[cid].deletion_token:
            return False
        channels.pop(cid)
        return True
    
    @staticmethod
    def add_client_to_channel(cid, sid):
        if not ChannelManager.is_valid_channel(cid):
            return False
        channel = channels.get(cid)
        channel.add_client(sid)
        return True

    @staticmethod
    def remove_client_from_channel(cid, sid):
        if not ChannelManager.is_valid_channel(cid):
            return False
        channel = channels.get(cid)
        channel.remove_client(sid)
        return True
    
    def is_valid_channel(cid):
        return cid in channels