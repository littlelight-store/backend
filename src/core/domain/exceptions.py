class BaseOrderException(Exception):
    pass


class OrderAlreadyClosed(BaseOrderException):
    pass


class BasePromoException(BaseException):
    pass


class PromoNotFoundException(BaseException):
    pass


class OrderNotExists(BaseOrderException):
    pass


class BaseBoosterException(BaseException):
    pass


class BoosterNotExists(BaseBoosterException):
    pass
