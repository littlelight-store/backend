import typing as t
import abc

from core.domain.entities.service import ServiceGroupTag, ShortServiceInfo


class MainPageServicesRepository(abc.ABC):
    @abc.abstractmethod
    def list_main_page_goods(self) -> t.Dict[ServiceGroupTag, t.List[ShortServiceInfo]]:
        pass
