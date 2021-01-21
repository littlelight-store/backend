import typing as t
from decimal import Decimal

from core.exceptions import BaseNotExistsException


class PromoCodeDoesNotExists(BaseNotExistsException):
    pass


class PromoCode:
    def __init__(
        self,
        code: str,
        service_slugs: t.List[str],
        comment: str,
        usage_limit: int,
        first_by_only: bool,
        discount: int
    ):
        self.discount = discount
        self.first_by_only = first_by_only
        self.usage_limit = usage_limit
        self.comment = comment
        self.service_slugs = service_slugs
        self.code = code

    @property
    def id(self):
        return self.code

    def includes_service(self, service_slug: str):
        return service_slug in self.service_slugs

    def price_discount(self, price: Decimal) -> Decimal:
        discount = price * (Decimal(self.discount) / 100)
        return price - discount
