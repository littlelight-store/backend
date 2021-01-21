import datetime as dt
import logging
import typing as t

from django.contrib.postgres.fields import JSONField
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models
from django.db.models import Case, Count, Prefetch, Q, Value, When
from django.utils.timezone import now

from orders.enum import OrderStatus
from orders.parse_product_options import (
    TemplateRepresentation, parse_options_from_layout_options,
    LAYOUT_TYPES,
)
from orders.tasks import incorrect_credentials, pending_approval, required_2_fa_code
from profiles.constants import CharacterClasses

from .orm_models import ORMShoppingCart, ORMShoppingCartItem

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

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        super(Order, self).save(force_insert, force_update, *args, **kwargs)

        if self.status != self.__original_status and self.__original_status:
            handle_instance_status_change(self, self.status)

        self.__original_status = self.status

    @classmethod
    def get_order_with_last_unread_messages_later_than(cls, minutes):
        current_time = dt.datetime.now()
        older_than_five = current_time - dt.timedelta(minutes=minutes)

        last_unread_messages = ChatMessage.objects.filter(
            created_at__lte=older_than_five, is_seen=False
        )
        messages = (
            cls.objects.prefetch_related(
                Prefetch("chat_messages", queryset=last_unread_messages)
            )
            .annotate(num_messages=Count("chat_messages"))
            .annotate(
                send_to=Case(
                    When(
                        Q(chat_messages__created_at__lte=older_than_five)
                        & Q(chat_messages__is_seen=False)
                        & (
                            Q(message_sent_to_booster=False)
                            & Q(chat_messages__role="booster")
                        ),
                        then=Value("booster"),
                    ),
                    When(
                        Q(chat_messages__created_at__lte=older_than_five)
                        & Q(chat_messages__is_seen=False)
                        & (
                            Q(message_sent_to_client=False)
                            & Q(chat_messages__role="client")
                        ),
                        then=Value("client"),
                    ),
                    default=Value(None),
                    output_field=models.CharField(null=True),
                )
            )
            .filter((Q(send_to="client") | Q(send_to="booster")), num_messages__gte=1,)
        )

        return messages


class ChatMessage(models.Model):
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.SET_NULL,
        null=True,
        related_name="chat_messages",
    )
    msg = models.TextField()
    created_at = models.DateTimeField()
    username = models.CharField(max_length=200)
    user = models.ForeignKey("profiles.User", on_delete=models.SET_NULL, null=True)
    role = models.CharField(max_length=20)
    is_seen = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]


class PvpConfigOrder(models.Model):
    from_points = models.IntegerField()
    to_points = models.IntegerField()
    from_label = models.CharField(max_length=64)
    to_label = models.CharField(max_length=64)


def handle_instance_status_change(instance, status):
    changes = {}

    if status == OrderStatus.attempt_authorization.value:
        changes["taken_at"] = now()

    if status == OrderStatus.two_factor_code_required.value:
        if instance.bungie_profile:
            username = instance.bungie_profile.username
            email = instance.bungie_profile.owner.email
            required_2_fa_code.delay(email, username)
        else:
            logger.exception("Changing status for user without bungie id")

    if status == OrderStatus.cant_sign_in.value:
        if instance.bungie_profile:
            username = instance.bungie_profile.username
            email = instance.bungie_profile.owner.email
            incorrect_credentials.delay(email, username)
        else:
            logger.exception("Changing status for user without bungie id")

    if status == OrderStatus.pending_approval.value:
        if instance.bungie_profile:
            username = instance.bungie_profile.username
            email = instance.bungie_profile.owner.email
            pending_approval.delay(email, username, instance.order_info())
        else:
            logger.exception("Changing status for user without bungie id")

    if status == OrderStatus.is_complete.value:

        changes["complete_at"] = now()
        changes["is_order_complete"] = True

        if instance.booster_user:
            booster_profile = instance.booster_user.booster_profile

            booster_profile.balance += instance.booster_price
            booster_profile.save()

        if instance.parent_order:
            parent_order_is_complete = True

            for order in instance.parent_order.orders.all():
                if order.status != OrderStatus.is_complete.value:
                    parent_order_is_complete = False

            if parent_order_is_complete:
                instance.parent_order.is_complete = True
                instance.parent_order.save()

    if changes:
        Order.objects.filter(id=instance.id).update(**changes)
