from enum import Enum


class ConfigurationType(str, Enum):
    options_select = 'options_select'
    base_price = 'base_price'
    range_select = 'range_select'
    options_steps = 'options_steps'