from core.exceptions import BaseNotExistsException


class OrderDoesNotExists(BaseNotExistsException):
    pass


class OrderObjectiveNotExists(BaseNotExistsException):
    pass
