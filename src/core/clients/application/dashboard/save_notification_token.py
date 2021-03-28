import typing as t

from pydantic import BaseModel

from core.clients.application.repository import ClientNotificationTokensRepository
from core.clients.domain.client import ClientNotificationToken, NotificationTokenPurpose, NotificationTokenType
from core.clients.domain.exceptions import ClientNotificationTokenNotFound


class SaveNotificationTokenDTORequest(BaseModel):
    client_id: int
    token: str
    source: NotificationTokenType
    purposes: t.List[NotificationTokenPurpose]


class SaveNotificationTokenUseCase:
    def __init__(
        self,
        notification_tokens_repository: ClientNotificationTokensRepository
    ):
        self.notifications_tokens_repository = notification_tokens_repository

    def _get_or_create_token(self, dto: SaveNotificationTokenDTORequest) -> ClientNotificationToken:
        try:
            token = self.notifications_tokens_repository.get_by_user_and_token(
                user_id=dto.client_id,
                token=dto.token
            )
        except ClientNotificationTokenNotFound:
            token = ClientNotificationToken.create(
                client_id=dto.client_id,
                token=dto.token,
                source=dto.source,
                purposes=dto.purposes
            )
        return token

    def execute(self, dto: SaveNotificationTokenDTORequest):
        token = self._get_or_create_token(dto)
        token.touch()
        self.notifications_tokens_repository.save(token)
