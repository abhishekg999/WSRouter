from uuid import uuid4
from utils import Err

session = {}


class Client:
    def __init__(self) -> None:
        self.sid = str(uuid4())
        self.cid = None


class SessionManager:
    @staticmethod
    def create_session() -> str:
        client = Client()
        session[client.sid] = client
        return client.sid

    @staticmethod
    def get_session(sid) -> Client:
        return session.get(sid)

    @staticmethod
    def remove_session(sid) -> None:
        session.pop(sid)

    @staticmethod
    def is_valid_session(sid) -> bool:
        return sid in session

    @staticmethod
    def set_user_in_channel(sid, cid) -> tuple[bool, Err]:
        if not SessionManager.is_valid_session(sid) or session[sid].cid is not None:
            return False
        session[sid].cid = cid
        return True, ""
