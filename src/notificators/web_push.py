import logging
import typing as t

import requests
from pydantic import BaseModel

from core.application.repositories.exceptions import ClientTokenIsInvalid, ErrorWhileSendingToken
from core.application.repositories.notifications import WebPushNotificationDTO, WebPushNotifications
from core.clients.domain.client import ClientNotificationToken

logger = logging.getLogger(__name__)


class GoogleFCMNotification(BaseModel):
    title: t.Optional[str] = None
    body: t.Optional[str] = None
    icon: t.Optional[str] = None
    click_action: t.Optional[str] = None


class GoogleFCMRequestParams(BaseModel):
    """
     notification: {
        "title": "Stas poshel nahui",
        "body": "5 to 1",
        "icon": "firebase-logo.png",
        "click_action": "http://localhost:8081"
      },
      to: string
    """
    to: str
    notification: GoogleFCMNotification
    dry_run: bool = False


class GoogleWebPushNotifications(WebPushNotifications):
    def __init__(self, token: str, dry_run: bool = False):
        self.token = token
        self.dry_run = dry_run

    def _get_headers(self):
        return {
            'Authorization': f'key={self.token}',
            'Content-Type': 'Application/json'
        }

    def send_push(self, token: ClientNotificationToken, dto: WebPushNotificationDTO):
        request = GoogleFCMRequestParams(
            to=token.token,
            notification=GoogleFCMNotification(
                title=dto.title,
                body=dto.body,
                click_action=dto.click_action
            ),
            dry_run=self.dry_run
        )
        connect_timeout, read_timeout = 5.0, 30.0

        result = requests.post(
            "https://fcm.googleapis.com/fcm/send", json=request.dict(), headers=self._get_headers(),
            timeout=(connect_timeout, read_timeout)
        )

        if not result.ok:
            logger.info(result.text)
            raise ErrorWhileSendingToken(msg=result.text)
        else:
            data = result.json()
            if data['failure'] > 0:
                raise ClientTokenIsInvalid()
            logger.info(data)
            logger.info("Successfully sent web push message")

