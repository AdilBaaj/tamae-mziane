import enum


class Transmission(enum.Enum):
    manual = 1
    automatic = 2


class Fuel(enum.Enum):
    diesel = 1
    essence = 2
    hybrid = 3


class Origin(enum.Enum):
    morocco = 1
    abroad = 2
