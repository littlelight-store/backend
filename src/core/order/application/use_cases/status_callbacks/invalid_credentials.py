from pydantic import BaseModel

from core.boosters.application.repository import BoostersRepository
from core.clients.application.repository import ClientCredentialsRepository, ClientsRepository
from core.order.application.repository import OrderObjectiveRepository, ClientOrderRepository
from notificators.new_email import DjangoEmailNotificator


class InvalidCredentialsDTORequest(BaseModel):
    order_objective_id: str
    client_id: int


class InvalidCredentialsUseCase:
    def __init__(
        self,
        email_notificator: DjangoEmailNotificator,
        order_objectives_repository: OrderObjectiveRepository,
        clients_repository: ClientsRepository,
        boosters_repository: BoostersRepository,
        client_order_repository: ClientOrderRepository,
        client_credentials_repository: ClientCredentialsRepository,
    ):
        self.boosters_repository = boosters_repository
        self.clients_repository = clients_repository
        self.order_objectives_repository = order_objectives_repository
        self.email_notificator = email_notificator
        self.client_order_repository = client_order_repository
        self.client_credentials_repository = client_credentials_repository

    def execute(self, dto: InvalidCredentialsDTORequest):
        client = self.clients_repository.get_by_id(dto.client_id)
        client_order = self.client_order_repository.get_by_order_objective(dto.order_objective_id)
        credential = self.client_credentials_repository.get_by_user_id_and_platform(
            platform=client_order.platform,
            user_id=client.id
        )
        credential.set_expired()

        self.client_credentials_repository.save(credential)

        self.email_notificator.invalid_credentials(client.email)
