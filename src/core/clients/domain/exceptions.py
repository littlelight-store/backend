from core.exceptions import BaseNotExistsException


class NotEnoughCashback(BaseException):
    pass


class ClientNotificationTokenNotFound(BaseNotExistsException):
    pass
