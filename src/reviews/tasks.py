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


@shared_task()
def send_review_link():
    reviews = Review.objects.filter(order__is_complete=True, is_sent_to_user=False)

    for review in reviews:
        subject, from_email, to = 'Your feedback is important for LittleLight.store', settings.DEFAULT_FROM_EMAIL, review.author.email

        bungie_user = BungieID.objects.filter(owner=review.author).first()

        if bungie_user:
            username = bungie_user.username
        else:
            username = review.author.email

        review_link = review.make_review_link()

        text_content = _build_feedback_msg(username, review_link)
        html_content = render_to_string('reviews/leave_review.html', {
            'username': username,
            'review_link': review_link,
            'hide_unsubscribe': False
        })

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        review.is_sent_to_user = True
        review.save()
