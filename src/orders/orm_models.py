
from django.db import models
from django.utils.timezone import now
from jsonfield import JSONField

from core.order.domain.order import ClientOrderStatus
from core.order.domain.order_states import OrderObjectiveStateMachineMixin, OrderObjectiveStatusSM
from utils import random_guid


class ORMShoppingCart(models.Model):
    class Meta:
        ordering = ["-created_at"]

    id = models.CharField(
        max_length=64,
        primary_key=True
    )
    created_at = models.DateTimeField(default=now)
    fetched_at = models.DateTimeField(default=now)
    is_deleted = models.BooleanField(default=False)

    promo_code = models.ForeignKey('services.PromoCode', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"<ShoppingCart created_at={self.created_at} cart_items={len(self.cart_items.all())}>"


class ORMShoppingCartItem(models.Model):

    class Meta:
        ordering = ["-created_at"]

    bungie_profile = models.ForeignKey(
        "profiles.ORMDestinyBungieProfile",
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    character = models.ForeignKey(
        "profiles.ORMDestinyBungieCharacter",
        on_delete=models.CASCADE,
    )

    id = models.CharField(
        max_length=64,
        primary_key=True
    )

    service = models.ForeignKey('services.Service', on_delete=models.CASCADE)
    selected_options = models.ManyToManyField('services.ServiceConfig', related_name='cart_items', blank=True)
    created_at = models.DateTimeField(default=now)
    range_options = JSONField(null=True, blank=True)

    shopping_cart = models.ForeignKey(
        ORMShoppingCart, on_delete=models.CASCADE,
        related_name='cart_items'
    )

    def __str__(self):
        return f"<ShoppingCartItem created_at={self.created_at} service={self.service} bungie_profile={self.bungie_profile}>"


class ORMClientOrder(models.Model):
    class Meta:
        db_table = "client_orders"

    id = models.CharField(max_length=128, primary_key=True)

    total_price = models.DecimalField(decimal_places=0, default=0, max_digits=6)

    order_id = models.CharField(max_length=128, db_index=True, null=True)
    client = models.ForeignKey('profiles.User', on_delete=models.SET_NULL, null=True, blank=True)
    payment_id = models.CharField(max_length=128, unique=True)
    comment = models.TextField(default='', blank=True, null=True)
    created_at = models.DateTimeField()
    order_status = models.CharField(
        max_length=32,
        default=ClientOrderStatus.AWAIT_PAYMENT.value,
        choices=ClientOrderStatus.choices(),
    )
    order_status_changed_at = models.DateTimeField()
    platform = models.ForeignKey('profiles.BungiePlatform', on_delete=models.SET_NULL, null=True, blank=True)
    promo = models.ForeignKey('services.PromoCode', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"<ClientOrder user={self.client} total_price={self.total_price} created_at={self.created_at}>"


class ORMOrderObjective(OrderObjectiveStateMachineMixin, models.Model):
    class Meta:
        db_table = "order_objective"
        abstract = False

    id = models.CharField(max_length=128, primary_key=True, default=random_guid)
    client_order = models.ForeignKey("ORMClientOrder", on_delete=models.CASCADE, blank=True, null=True)
    service = models.ForeignKey(
        'services.Service', on_delete=models.SET_NULL, null=True,
        related_name='order_objectives',
        related_query_name='order_objectives'
    )

    destiny_profile = models.ForeignKey(
        "profiles.ORMDestinyBungieProfile",
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    destiny_character = models.ForeignKey(
        "profiles.ORMDestinyBungieCharacter",
        on_delete=models.CASCADE,
        null=True, blank=True
    )

    price = models.DecimalField(decimal_places=0, default=0, max_digits=6, blank=True)

    status = models.CharField(
        verbose_name='Order state',
        null=False,
        blank=False,
        default=OrderObjectiveStatusSM.SM_INITIAL_STATE,
        choices=OrderObjectiveStatusSM.STATE_CHOICES,
        max_length=32,
        help_text='Order state',
    )

    selected_options = models.ManyToManyField(
        'services.ServiceConfig',
        related_name='order_objectives',
        blank=True
    )
    range_options = JSONField(null=True, blank=True)
    status_changed_at = models.DateTimeField(blank=True, default=now)
    created_at = models.DateTimeField(blank=True, default=now)
    booster = models.ForeignKey('profiles.BoosterUser', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        service_slug = ''
        if self.service_id:
            service_slug = self.service_id
        return f"OrderObjective: {service_slug} [{self.status}] {self.price}"
