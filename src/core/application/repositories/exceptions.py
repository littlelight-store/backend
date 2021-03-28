class ServiceNotExists(BaseException):
    pass


class ClientTokenIsInvalid(Exception):
    pass


class ErrorWhileSendingToken(Exception):
    def __init__(self, msg: str):
        self.msg = msg
