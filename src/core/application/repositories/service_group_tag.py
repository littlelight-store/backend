import typing as t
import abc

from core.domain.entities.service import ServiceGroupTag


class ServiceGroupTagRepository(abc.ABC):
    @abc.abstractmethod
    def list(self) -> t.List[ServiceGroupTag]: ...
