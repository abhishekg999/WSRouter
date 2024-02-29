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
