import enum


class Category(str, enum.Enum):
    pvp = 'pvp'
    pve = 'pve'