from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from boosting import settings
from profiles.models import BungieID
from reviews.models import Review


def _build_feedback_msg(username, review_link):
    text = (
        f'Hi, {username}\n'
        'Your order has been completed!\n'
        'Thank you for using our services. Please let us know what you think about the purchase.Your feedback is highly appreciated, as it will help us serve you better.\n'
        'If you are willing, you can follow to leave your feedback for us.It will only take 3 minutes, and your review will help us make LittleLight.store even better for you and other clients.\n'
        'The review will be published on the services page.\n'

        'Thanks in advance for your time! \n'

    )

    text += f'<a href="{review_link}">leave review</a>'

    text += f'Thank you for your purchase from littlelight.store\n\n'
    return text
