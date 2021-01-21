from enum import Enum


class CharacterClasses(int, Enum):
    titan = 0
    hunter = 1
    warlock = 2


class Membership(int, Enum):
    Xbox = 1
    PS4 = 2
    Steam = 3
    BattleNET = 4
