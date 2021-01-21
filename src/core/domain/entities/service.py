import abc
import typing as t
from decimal import Decimal

from core.domain.entities.constants import ConfigurationType
from core.domain.entities.interfaces import IService, IServiceConfig
from core.shopping_cart.application.use_cases.dto import CartRangeOptionsDTO
from orders.parse_product_options import parse_options_from_layout_options, LAYOUT_TYPES, TemplateRepresentation


class ServicePriceCalculatorStrategy(abc.ABC):

    @staticmethod
    @abc.abstractmethod
    def get_price(
        options: t.List['ServiceConfig'],
        range_options: t.Optional[CartRangeOptionsDTO],
        service_base_price: t.Optional[Decimal]
    ) -> t.Tuple[Decimal, Decimal]:
        pass


class OptionsPriceCalculator(ServicePriceCalculatorStrategy):
    @staticmethod
    def get_price(
        options: t.List['ServiceConfig'],
        range_options: t.Optional[CartRangeOptionsDTO],
        service_base_price: t.Optional[Decimal]
    ) -> t.Tuple[Decimal, Decimal]:
        total_price = total_old_price = service_base_price if service_base_price else 0

        for o in options:
            if o.price:
                total_price += o.price
                if o.old_price:
                    total_old_price += o.old_price
                else:
                    total_old_price += o.price

        return total_price, total_old_price


class RangeOptionsPriceCalculator(ServicePriceCalculatorStrategy):
    @staticmethod
    def get_price(
        options: t.List['ServiceConfig'],
        range_options: t.Optional[CartRangeOptionsDTO],
        service_base_price: t.Optional[Decimal]
    ) -> t.Tuple[Decimal, Decimal]:
        return Decimal(range_options['totalPrice']), Decimal(range_options['totalOldPrice'])


SERVICE_OPTIONS_PRICE_CALCULATOR_STRATEGIES = {
    ConfigurationType.options_steps: OptionsPriceCalculator,
    ConfigurationType.options_select: OptionsPriceCalculator,
    ConfigurationType.base_price: OptionsPriceCalculator,
    ConfigurationType.range_select: RangeOptionsPriceCalculator
}


def service_options_price_calculator(
    service: 'Service',
):
    return SERVICE_OPTIONS_PRICE_CALCULATOR_STRATEGIES[service.configuration_type]


class Service(IService):
    price_resolver: t.Optional[ServicePriceCalculatorStrategy]

    def __init__(
        self,
        title: str,
        slug: str,
        booster_percent: int,
        layout_type: LAYOUT_TYPES,
        category: str,
        at_least_one_option_required: bool = False,
        configuration_type: t.Optional[ConfigurationType] = None,
        base_price: t.Optional[int] = None,
        static_data: t.Optional['ServicePageStaticData'] = None,
        item_image: str = '',
        image_bg: str = '',
        ordering: int = 0,
        layout_options: t.Optional[t.Dict[str, t.Dict[t.Any, t.Any]]] = None,
        configs: t.List['ServiceConfig'] = list,
    ):
        self.static_data = static_data
        self.ordering = ordering
        self.item_image = item_image
        self.category = category
        self.title = title
        self.slug = slug
        self.layout_options = layout_options
        self.configs = configs
        self.booster_percent = booster_percent
        self.layout_type = layout_type
        self.image_bg = image_bg
        self.configuration_type = ConfigurationType[configuration_type] if configuration_type else None
        self.base_price = base_price
        self.at_least_one_option_required = at_least_one_option_required

    @property
    def price(self) -> Decimal:
        if self.layout_options and self.layout_options.get("price"):
            price_obj: dict = self.layout_options["price"]

            if type(price_obj) == dict:
                return Decimal(price_obj["totalPrice"])
            return Decimal(self.layout_options.get("price"))

    @property
    def price_tag(self) -> Decimal:
        price_obj = self.layout_options.get('price')
        return price_obj['amount']

    @property
    def options_ids(self) -> t.List[str]:
        result = []
        for option_id, option in self.layout_options.get("selectedOptions", {}).items():
            if option:
                result.append(option_id)

        for option in self.layout_options.get("customSelectedOptions", []):
            if option:
                result.append(option['id'])

        return result

    @property
    def options_representation(self) -> t.List[TemplateRepresentation]:
        return parse_options_from_layout_options(self.layout_options, self.layout_type)

    @property
    def product_link(self) -> str:
        return f"https://littlelight.store/product/{self.slug}"

    def set_price_resolver(
        self,
        price_resolver: ServicePriceCalculatorStrategy
    ):
        self.price_resolver = price_resolver

    def get_service_price(
        self,
        options: t.List['ServiceConfig'],
        range_options: t.Optional[CartRangeOptionsDTO],
    ):
        if not self.price_resolver:
            raise ValueError()

        base_price = self.base_price

        return self.price_resolver.get_price(
            options=options,
            range_options=range_options,
            service_base_price=base_price
        )


class ServicePageStaticData:
    def __init__(
        self,
        you_will_get_content: t.Optional[str] = None,
        requirements: t.Optional[str] = None,
        description: t.Optional[str] = None,
    ):
        self.description = description
        self.requirements = requirements
        self.you_will_get_content = you_will_get_content


class ServiceConfig(IServiceConfig):
    def __init__(
        self,
        title: str,
        _id: int,
        description: str,
        price: Decimal,
        old_price: Decimal,
        extra_data: dict
    ):
        self.title = title
        self.id = _id
        self.description = description
        self.price = price
        self.old_price = old_price
        self.extra_data = extra_data

    def __str__(self):
        return f"{self.id} {self.title} {self.description}"


class ServiceGroupTag:
    def __init__(
        self,
        name: str,
        value: str
    ):
        self.name = name
        self.value = value


class ServiceStatistics:
    completed_count: int
    feedback_rating: float


class BaseService:
    title: str
    slug: str
    layout_options: t.Optional[t.Dict[str, t.Dict[t.Any, t.Any]]] = None

    @property
    def price_tag(self) -> Decimal:
        price_obj = self.layout_options.get('price')
        return price_obj['amount']

    @property
    def range_options(self) -> t.Optional[dict]:
        return self.layout_options.get('rangeOptions')


class ShortServiceInfo(BaseService):
    def __init__(
        self,
        title: str,
        slug: str,
        image: str,
        is_hot: bool,
        is_new: bool,
        layout_options: t.Optional[t.Dict[str, t.Dict[t.Any, t.Any]]] = None,
    ):
        self.slug = slug
        self.title = title
        self.layout_options = layout_options
        self.is_hot = is_hot
        self.is_new = is_new
        self.image = image


class ServiceDetailedInfo(BaseService, ServiceStatistics):
    def __init__(
        self,
        title: str,
        slug: str,
        image_full: str,
        image_bg: str,
        configuration_type: ConfigurationType,
        base_price: t.Optional[int],
        at_least_one_option_required: bool,
        eta: str,
        feedback_rating: float,
        completed_count: int,
        layout_options: t.Optional[t.Dict[str, t.Dict[t.Any, t.Any]]] = None,
        static_data: t.Optional['ServicePageStaticData'] = None,
    ):
        super().__init__()
        self.feedback_rating = feedback_rating
        self.completed_count = completed_count
        self.title = title
        self.slug = slug
        self.layout_options = layout_options
        self.static_data = static_data
        self.at_least_one_option_required = at_least_one_option_required
        self.base_price = base_price
        self.configuration_type = configuration_type
        self.image_bg = image_bg
        self.image_full = image_full
        self.eta = eta
