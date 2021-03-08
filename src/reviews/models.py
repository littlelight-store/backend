import datetime as dt
import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from orders.orm_models import ORMClientOrder


def create_edit_token() -> str:
    return uuid.uuid4().hex


class Review(models.Model):
    author = models.ForeignKey(
        'profiles.User',
        on_delete=models.CASCADE,
        related_name='authors',
        related_query_name='authors',
        blank=True, null=True
    )

    author_string = models.CharField(max_length=128, blank=True, null=True)

    order = models.OneToOneField(
        'orders.ParentOrder',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    client_order = models.OneToOneField(
        ORMClientOrder,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='review',
        related_query_name='review'
    )

    services = models.ManyToManyField(
        'services.Service',
        related_name='reviews',
        related_query_name='reviews'
    )

    rate = models.IntegerField(
        validators=[
            MaxValueValidator(5),
            MinValueValidator(1)
        ],
        help_text='From 1 to 5',
        blank=True, null=True
    )
    text = models.TextField(default='', blank=True)

    edit_token = models.CharField(max_length=128, default=create_edit_token)

    created_at = models.DateTimeField(default=dt.datetime.now)
    last_edited = models.DateTimeField(auto_now=True, editable=True)

    is_posted = models.BooleanField(default=False)
    is_sent_to_user = models.BooleanField(default=False)
    is_anonymous = models.BooleanField(default=False)

    def make_review_link(self):
        if self.order:
            return f'https://littlelight.store/review/{self.order.id}/?access_token={self.edit_token}'
        else:
            return 'https://littlelight.store/'

    def __str__(self):
        return f'{self.author_string} — {self.created_at}'
