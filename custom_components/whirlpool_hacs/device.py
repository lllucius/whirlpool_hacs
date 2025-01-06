"""Device data for the Whirpool Appliances integration."""

from __future__ import annotations

from datetime import datetime, timedelta

from aiohttp import ClientSession

from .whirlpool_api.appliancesmanager import AppliancesManager
from .whirlpool_api.auth import Auth
from .whirlpool_api.backendselector import BackendSelector
from .whirlpool_api.dryer import Dryer
from .whirlpool_api.oven import Cavity, Oven

from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    BRAND_KITCHENAID,
    BRAND_MAYTAG,
    BRAND_WHIRLPOOL,
    DOMAIN,
    LOGGER,
)


def get_brand_from_model(model_number: str) -> str:
    """Get the brand name from the model number."""
    if model_number[0] == "W":
        return BRAND_WHIRLPOOL
    elif model_number[0] == "M":
        return BRAND_MAYTAG
    elif model_number[0] == "K":
        return BRAND_KITCHENAID
    else:
        return BRAND_WHIRLPOOL


class WhirlpoolDevice(DataUpdateCoordinator):
    """Base device."""

    def __init__(
        self,
        hass: HomeAssistant,
        manager: AppliancesManager,
        appliance: Appliance
    ) -> None:
        """Initialize the device."""
        self.hass: HomeAssistant = hass
        self.manager: ApplicancesManager = manager
        self.appliance: Appliance = appliance

        self._attr_name = appliance.name
        self.attr_name = appliance.name
        self.name = appliance.name
        print("appliancme", appliance.name)

        # Register for the updates provided by the Whirlpool API
        self.appliance.register_attr_callback(self.on_update)

        # Create a periodic keep-alive call to prevent the API connection from going stale
        async_track_time_interval(self.hass, self.keep_alive, timedelta(minutes=5))

        super().__init__(
            hass,
            LOGGER,
            name=f"{DOMAIN}-{self.appliance.said}",
        )

    def on_update(self) -> None:
        """Handle device data update callbacks."""
        LOGGER.debug(f"Data for {self.appliance.name} has been updated")

    async def keep_alive(self, trigger: datetime) -> None:
        """Listen for device events."""
        LOGGER.debug("Keeping the API connection alive")
        await self.appliance.fetch_data()

    def register_callback(self, fn: callable):
        """Register a callback for oven updates."""
        self.appliance.register_attr_callback(fn)

    def unregister_callback(self, fn: callable):
        """Unregister a callback for oven updates."""
        self.appliance.unregister_attr_callback(fn)

    @property
    def is_online(self) -> bool:
        """Return the online status of the oven."""
        return self.appliance.get_online() | False

class WhirlpoolOvenDevice(WhirlpoolDevice):
    pass

class WhirlpoolDryerDevice(WhirlpoolDevice):
    pass

class WhirlpoolAirconDevice(WhirlpoolDevice):
    pass

class WhirlpoolWasherDevice(WhirlpoolDevice):
    pass

class WhirlpoolWasherDryerDevice(WhirlpoolDevice):
    pass

