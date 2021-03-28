import logging
from dataclasses import dataclass

from pydantic import BaseModel

from core.application.repositories.exceptions import ClientTokenIsInvalid
from core.application.repositories.notifications import WebPushNotificationDTO, WebPushNotifications
from core.clients.application.repository import ClientNotificationTokensRepository
from core.clients.domain.client import NotificationTokenPurpose

logger = logging.getLogger(__name__)


class SendWebPushDTORequest(BaseModel):
    client_id: int
    purpose: NotificationTokenPurpose
    body: str
    title: str
    click_action: str


class SendWebPushUseCase:
    def __init__(
        self,
        client_notification_tokens_repository: ClientNotificationTokensRepository,
        push_service: WebPushNotifications
    ):
        self.push_service = push_service
        self.client_notification_tokens_repository = client_notification_tokens_repository

    @staticmethod
    def create_web_push_message(dto: SendWebPushDTORequest):
        return WebPushNotificationDTO(
            body=dto.body,
            title=dto.title,
            click_action=dto.click_action
        )

    def execute(self, dto: SendWebPushDTORequest):
        client_tokens = self.client_notification_tokens_repository.list_active_by_client_and_purpose(
            dto.client_id,
            dto.purpose
        )

        if not len(client_tokens):
            logger.info(f'No tokens found for {dto.client_id} exiting')

        logger.info(f'Found {len(client_tokens)} for user: {dto.client_id}')

        for token in client_tokens:
            try:
                self.push_service.send_push(token, self.create_web_push_message(dto))
            except ClientTokenIsInvalid:
                token.deactivate()
                self.client_notification_tokens_repository.save(token)
            except Exception:
                logger.warning("Error while sending push notification", extra={
                    'token': token.token
                }, exc_info=True)
