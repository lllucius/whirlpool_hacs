"""Binary sensors for Whirlpool Appliances."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
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
    """Set up the Whirlpool Appliances binary sensors from config entry."""

    entities = await setup_entities(
        hass, config_entry, Platform.BINARY_SENSOR, WhirlpoolBinarySensor
    )

    async_add_entities(entities)

class WhirlpoolBinarySensor(WhirlpoolEntity, BinarySensorEntity):
    """State of a binary sensor."""

    def __init__(self, device: WhirlpoolDevice, model: str) -> None:
        """Initialize the binary sensor."""
        super().__init__(device, model)

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor set."""
        return self.appliance.get_boolean(self.attr_name)

