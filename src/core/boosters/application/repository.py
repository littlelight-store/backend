import typing as t
import abc

from core.boosters.domain.entities import Booster
from core.domain.object_values import ClientId


class BoostersRepository(abc.ABC):

    @abc.abstractmethod
    def list_by_client_orders(self, client_id: ClientId) -> t.List[Booster]:
        pass
