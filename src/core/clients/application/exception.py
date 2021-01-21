from core.exceptions import BaseNotExistsException


class ProfileCredentialsNotFound(BaseNotExistsException):
    pass


class UserNotFound(BaseNotExistsException):
    pass
