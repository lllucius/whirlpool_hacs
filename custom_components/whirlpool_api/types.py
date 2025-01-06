from dataclasses import dataclass
from enum import Enum
from typing import TypedDict


class CredentialsDict(TypedDict):
    client_id: str
    client_secret: str


class Brand(Enum):
    Whirlpool = 0
    Maytag = 1
    KitchenAid = 2


class Region(Enum):
    EU = 0
    US = 1


class ApplianceKind(Enum):
    AirCon = 0
    Dryer = 1
    Oven = 2
    Washer = 3
    WasherDryer = 4


@dataclass
class ApplianceData:
    said: str
    name: str
    model_key: str
    category: str
    model_number: str
    serial_number: str
    
