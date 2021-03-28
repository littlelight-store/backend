from pydantic import BaseModel, SecretStr

from core.clients.application.dashboard.list_client_dashboard_use_case import ProfilePlatformCredential
from core.clients.application.repository import ClientCredentialsRepository
from core.clients.domain.client import ClientCredential
from profiles.constants import Membership


class SetMembershipCredentialsDTOInput(BaseModel):
    platform: Membership
    client_id: int
    credentials_value: SecretStr
    credentials_name: SecretStr
    has_second_factor: bool


class SetMembershipCredentialsUseCase:
    def __init__(
        self,
        client_credentials_repository: ClientCredentialsRepository
    ):
        self.client_credentials_repository = client_credentials_repository

    def execute(self, dto: SetMembershipCredentialsDTOInput) -> ProfilePlatformCredential:
        credential = ClientCredential(
            platform=dto.platform,
            owner_id=dto.client_id,
            account_password=dto.credentials_value.get_secret_value(),
            account_name=dto.credentials_name.get_secret_value(),
            is_expired=False,
            has_second_factor=dto.has_second_factor
        )

        self.client_credentials_repository.save(credential)

        return ProfilePlatformCredential(
            is_set=True,
            must_be_set=False,
            platform=credential.platform,
            owner_id=credential.owner_id,
            account_name=credential.account_name,
            has_second_factor=credential.has_second_factor
        )
