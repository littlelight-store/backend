from celery import shared_task
from django.conf import settings
from django.core import mail

text = '''Hello! Thank you for signing up. ❤️'''


@shared_task
def welcome_email_letter(user_email):

    mail.send_mail(
        'Registration', text, settings.EMAIL_HOST_USER, [user_email]
    )
