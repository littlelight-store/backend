import typing as t
from abc import ABC

from mypy_extensions import TypedDict
from pydantic import BaseModel
from typing_extensions import Literal

LAYOUT_TYPES = Literal[
    "single", "range-calculator", "options", "check-progress", "customize-progress"
]


def get_product_layout_type(jsonData: dict) -> LAYOUT_TYPES:
    return jsonData["layoutType"]


class TemplateRepresentation(BaseModel):
    description: str
    price: str


class SelectedOption(BaseModel):
    title: str
    price: str


_TTemplateRepresentationsList = t.List[TemplateRepresentation]
_buildable_object = t.TypeVar("_buildable_object")


class AbstractController(ABC):
    @classmethod
    def from_json(cls, json: dict, **kwargs) -> _buildable_object:
        raise NotImplementedError

    def get_template_representation(self) -> _TTemplateRepresentationsList:
        raise NotImplementedError()


class BaseOption(BaseModel):
    price: str
    selected_options: t.List[SelectedOption]

    @classmethod
    def from_json(cls, json: dict, **kwargs) -> _buildable_object:
        raise NotImplementedError


TOptionsCalculator = t.TypeVar('TOptionsCalculator', bound='OptionsCalculator')


class OptionsCalculator(BaseOption, AbstractController):
    price: str
    selected_options: t.List[SelectedOption]

    @classmethod
    def from_json(cls, json: dict, **kwargs) -> _buildable_object:
        selected_options = []
        
        for _, option in json['selectedOptions'].items():
            selected_options.append(
                SelectedOption(
                    title=option['title'],
                    price=option["price"]
                )
            )

        return cls(
            price=json["price"]["totalPrice"],
            selected_options=selected_options
        )

    def get_template_representation(self) -> _TTemplateRepresentationsList:
        result = []

        for option in self.selected_options:
            result.append(TemplateRepresentation(
                description=option.title,
                price=option.price,
            ))

        return result


TCustomizeProgressCalculator = t.TypeVar('TCustomizeProgressCalculator', bound='CustomizeProgressCalculator')


class CustomizeProgressCalculator(BaseOption, AbstractController):
    price: str
    selected_preset: t.Optional[str]
    selected_options: t.List[SelectedOption]

    @classmethod
    def from_json(cls, json: dict, **kwargs) -> _buildable_object:
        return cls(
            price=json["price"]["totalPrice"],
            selected_preset=json["selectedPreset"]['description'] if json["selectedPreset"] else None,
            selected_options=[SelectedOption(**data) for data in json['customSelectedOptions']]
        )

    def get_preset_representation(self) -> _TTemplateRepresentationsList:
        return [TemplateRepresentation(
            description=self.selected_preset,
            price=self.price
        )]

    def get_options_representation(self) -> _TTemplateRepresentationsList:
        return [TemplateRepresentation(
            description=option.title,
            price=option.price
        ) for option in self.selected_options
        ]

    def get_template_representation(self) -> _TTemplateRepresentationsList:
        if self.selected_preset:
            return self.get_preset_representation()
        else:
            return self.get_options_representation()


class SingleOptionCalculator(BaseModel, AbstractController):
    price: str
    description: str

    def get_template_representation(self) -> _TTemplateRepresentationsList:
        return [TemplateRepresentation(
            description=self.description,
            price=self.price
        )]

    @classmethod
    def from_json(cls, json: dict, **kwargs) -> _buildable_object:
        return cls(
            price=json.get("price", ''),
            description=json.get("title", '')
        )


TRangeCalculator = t.TypeVar('TRangeCalculator', bound='RangeCalculator')


class RangeCalculator(BaseModel, AbstractController):
    """
      {
      "price": "100.00",
      "pointTo": 1000,
      "oldPrice": "100.00",
      "dimension": "Point",
      "lastLabel": "Brave",
      "pointFrom": 0,
      "pointValue": 50,
      "dimensionPlural": "Points"
      }
    """

    point_from: int
    point_to: int

    dimension: str
    last_label: str
    dimension_plural: str

    price: str
    old_price: str

    @classmethod
    def from_json(cls, json: dict, **kwargs) -> _buildable_object:
        return cls(
            point_from=json["pointFrom"],
            point_to=json["pointTo"],
            dimension=json["dimension"],
            last_label=json["lastLabel"],
            dimension_plural=json["dimensionPlural"],
            price=json["price"],
            old_price=json["oldPrice"]
        )

    def _get_point_dimension(self, point) -> str:
        if point == 1:
            return self.dimension
        else:
            return self.dimension_plural

    def _get_description(self) -> str:

        if self.dimension == "Win":  # Wins representation
            _dimension = self._get_point_dimension(self.point_to)
            return (
                f"{self.point_to} {_dimension.lower()}"
            )
        else:
            _dimension_from = self._get_point_dimension(self.point_from)
            _dimension_to = self._get_point_dimension(self.point_to)

            return (
                f"From {self.point_from} {_dimension_from.lower()} to "
                f"{self.point_to} {_dimension_to.lower()}"
            )

    def get_template_representation(self) -> _TTemplateRepresentationsList:
        return [TemplateRepresentation(
            description=self._get_description(),
            price=self.price
        )]


_optionsMapping = TypedDict("_optionsMapping", {
    "range-calculator": RangeCalculator,
    "customize-progress": CustomizeProgressCalculator,
    "options": OptionsCalculator,
    "check-progress": OptionsCalculator,
    "single": SingleOptionCalculator
})

options_models_mapping = {  # type: _optionsMapping
    "range-calculator": RangeCalculator,
    "customize-progress": CustomizeProgressCalculator,
    "options": OptionsCalculator,
    "check-progress": OptionsCalculator,
    "single": SingleOptionCalculator
}

# noinspection PyTypeHints
_available_models = Literal[RangeCalculator, CustomizeProgressCalculator, OptionsCalculator, SingleOptionCalculator]


def ensure_single_or_list(representations: t.Union[
    TemplateRepresentation, _TTemplateRepresentationsList
]):
    if type(representations) == list and len(representations) == 1:
        return representations[0]
    else:
        return representations


def get_options_model(option_type: LAYOUT_TYPES):
    return options_models_mapping[option_type]


def parse_options_from_layout_options(services, layout_option: LAYOUT_TYPES) -> _TTemplateRepresentationsList:
    model = get_options_model(layout_option)  # type: _available_models

    instance = model.from_json(services)
    return instance.get_template_representation()
