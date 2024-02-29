from uuid import uuid4

session = {}

class Client:
    def __init__(self, sid) -> None:
        self.sid = sid

class SessionManager:
    @staticmethod
    def create_session():
        session_id = str(uuid4())
        session[session_id] = Client(session_id)
        return session_id
    
    @staticmethod
    def get_session(sid):
        return session.get(sid)
    
    @staticmethod
    def remove_session(sid):
        session.pop(sid)

    