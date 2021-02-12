import logging
import typing as t

from django.contrib.postgres.fields import JSONField
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models

from orders.enum import OrderStatus
from orders.parse_product_options import (
    TemplateRepresentation, parse_options_from_layout_options,
    LAYOUT_TYPES,
)
from profiles.constants import CharacterClasses

from .orm_models import ChatMessage, ORMShoppingCart, ORMShoppingCartItem, ORMOrderObjective

logger = logging.getLogger(__name__)


class ParentOrder(models.Model):
    class Meta:
        app_label = "orders"

    site = models.ForeignKey(
        Site,
        blank=True,
        null=True,
        db_index=True,
        on_delete=models.SET_NULL,
        related_name="parent_orders",
    )

    payment_id = models.CharField(max_length=1024, default="", db_index=True)
    payment_status = models.CharField(max_length=128, blank=True, null=True)

    invoice_number = models.CharField(
        max_length=128, blank=True, null=True, db_index=True
    )

    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, db_index=True
    )
    platform = models.ForeignKey(
        "profiles.BungiePlatform", null=True, blank=True, on_delete=models.SET_NULL
    )

    raw_data = JSONField(null=True, blank=True)

    is_complete = models.BooleanField(default=False)
    is_payed = models.BooleanField(default=False)
    is_seen = models.BooleanField(
        default=False, help_text="Set to False to receive tg notification"
    )

    credentials = models.ForeignKey(
        "profiles.ProfileCredentials", on_delete=models.SET_NULL, null=True, blank=True
    )

    on_site = CurrentSiteManager()
    objects = models.Manager()


class Order(models.Model):
    class Meta:
        app_label = "orders"

    __original_status = None

    def __init__(self, *args, **kwargs):
        super(Order, self).__init__(*args, **kwargs)
        self.__original_status = self.status

    site = models.ForeignKey(
        Site,
        blank=True,
        null=True,
        db_index=True,
        on_delete=models.SET_NULL,
        related_name="orders",
    )

    parent_order = models.ForeignKey(
        "orders.ParentOrder",
        on_delete=models.CASCADE,
        related_name="orders",
        null=True,
        blank=True,
    )

    service = models.ForeignKey(
        "services.Service", on_delete=models.SET_NULL, related_name="orders", null=True
    )
    service_config = models.ManyToManyField(
        "services.ServiceConfig", null=True, blank=True
    )
    bungie_profile = models.ForeignKey(
        "profiles.BungieID", on_delete=models.SET_NULL, blank=True, null=True
    )
    character = models.ForeignKey(
        "profiles.UserCharacter", on_delete=models.SET_NULL, null=True, blank=True
    )

    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, db_index=True
    )
    booster_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, db_index=True, default=0
    )

    payment_id = models.CharField(
        max_length=1024, default="", db_index=True, blank=True, null=True
    )
    payment_status = models.CharField(max_length=128, blank=True, null=True)

    invoice_number = models.CharField(
        max_length=128, blank=True, null=True, db_index=True
    )

    status = models.CharField(
        max_length=28,
        db_index=True,
        blank=True,
        choices=[(tag.value, tag.name) for tag in OrderStatus],
        default=OrderStatus.is_checking_payment.value,
    )

    is_order_complete = models.BooleanField(default=False)
    is_payed = models.BooleanField(default=False)
    is_posted = models.BooleanField(default=False)

    complete_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    taken_at = models.DateTimeField(null=True, blank=True)
    posted_at = models.DateTimeField(null=True, blank=True)

    comment = models.TextField(default="", blank=True, null=True)
    promo = models.ForeignKey(
        "services.PromoCode", null=True, blank=True, on_delete=models.SET_NULL,
    )
    pvp_config = models.OneToOneField(
        "orders.PvpConfigOrder",
        related_name="order",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    booster_user = models.ForeignKey(
        "profiles.User",
        related_name="booster_orders",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="Booster set for current order",
    )

    message_sent_to_booster = models.BooleanField(default=False)
    message_sent_to_client = models.BooleanField(default=False)

    layout_options = JSONField(null=True, blank=True)
    raw_data = JSONField(null=True, blank=True)

    is_faked = models.BooleanField(default=False)

    on_site = CurrentSiteManager()
    objects = models.Manager()

    def order_info(self):
        layout_type = self.service.option_type  # type: LAYOUT_TYPES

        option: t.Optional[TemplateRepresentation] = None
        options: t.Optional[
            t.List[TemplateRepresentation]
        ] = parse_options_from_layout_options(self.layout_options, layout_type)

        if type(options) != list:
            option = options
            options = []

        return {
            "title": self.service.title,
            "price": self.total_price,
            "promo": self.promo.code if self.promo else None,
            "option": dict(option) if option else None,
            "options": [dict(option) for option in options],
            "link": f"https://littlelight.store/product/{self.service.slug}",
            "character_class": CharacterClasses(
                int(self.character.character_class)
            ).name
            if self.character
            else "",
        }

    def __str__(self):
        service_title = self.service.title if self.service else ""

        return (
            f'Created: {self.created_at.strftime("%d-%m-%Y %H-%M")} | '
            f"payed: {self.is_payed} | "
            f"{service_title} | "
            f"${self.total_price} | "
            f"Payment status: {self.payment_status} "
        )


class PvpConfigOrder(models.Model):
    from_points = models.IntegerField()
    to_points = models.IntegerField()
    from_label = models.CharField(max_length=64)
    to_label = models.CharField(max_length=64)


