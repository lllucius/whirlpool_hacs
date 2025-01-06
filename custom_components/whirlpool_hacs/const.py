"""Constants for the Whirlpool Appliances integration."""

import logging
from typing import Final

from .whirlpool_api.backendselector import Brand, Region
from .whirlpool_api.oven import CavityState, CookMode

DOMAIN: Final = "whirlpool"

LOGGER = logging.getLogger(__package__)

CONF_BRAND: Final = "brand"
CONF_OVEN: Final = "oven"
CONF_LAUNDRY: Final = "laundry"
CONF_AIRCON: Final = "aircon"


CONF_BRANDS_MAP: Final = {
    "Whirlpool": Brand.Whirlpool,
    "Maytag": Brand.Maytag,
    "KitchenAid": Brand.KitchenAid,
}
CONF_REGIONS_MAP: Final = {
    "EU": Region.EU,
    "US": Region.US,
}

BRAND_WHIRLPOOL: Final = "Whirlpool"
BRAND_MAYTAG: Final = "Maytag"
BRAND_KITCHENAID: Final = "KitchenAid"


# Configuration and options
CONF_ACCOUNTS: Final = "accounts"
CONF_SETTINGS: Final = "settings"
CONF_REFRESH_INTERVAL: Final = "refresh_interval"
CONF_TIMEOUT: Final = "timeout"

# Defaults
DEFAULT_NAME: Final = "My Account"
DEFAULT_REFRESH_INTERVAL: Final = 300  # 5 minutes
DEFAULT_TIMEOUT: Final = 30  # 30 seconds


