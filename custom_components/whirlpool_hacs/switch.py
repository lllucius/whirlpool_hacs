"""Switch sensors for Whirlpool Appliances."""

from __future__ import annotations

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .device import WhirlpoolDevice
from .entity import WhirlpoolEntity, setup_entities


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Whirlpool Appliances switches from config entry."""

    entities = await setup_entities(
        hass, config_entry, Platform.SWITCH, WhirlpoolSwitch
    )

    async_add_entities(entities)

class WhirlpoolSwitch(WhirlpoolEntity, SwitchEntity):
    """State of a switch."""

    def __init__(self, device: WhirlpoolDevice, model: str) -> None:
        """Initialize the switch."""
        super().__init__(device, model)

    @property
    def is_on(self) -> bool:
        """Return true if the switch set."""
        return self.appliance.get_boolean(self.attr_name)

    def turn_on(self, **kwargs) -> None:
        """Turn the entity on."""
        manager = self.appliance._app_manager
        manager.send_attributes(self.appliance, {self.attr_name, "1"})

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        manager = self.appliance._app_manager
        await manager.send_attributes(self.appliance, {self.attr_name, "1"})

    def turn_off(self, **kwargs):
        """Turn the entity off."""
        manager = self.appliance._app_manager
        manager.send_attributes(self.appliance, {self.attr_name: "0"})

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        manager = self.appliance._app_manager
        await manager.send_attributes(self.appliance, {self.attr_name: "0"})

