"""Binary sensors for Whirlpool Appliances."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntityDescription,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .device import WhirlpoolDevice
from .entity import WhirlpoolEntity, setup_entities

DISABLED: list[str] = [
]

HIDDEN: list[str] = [
]

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

        self.entity_description = BinarySensorEntityDescription(
            key=self.m2m_attr,
            entity_registry_enabled_default=False if self.m2m_attr in DISABLED else True,
            entity_registry_visible_default=False if self.m2m_attr in HIDDEN else True,
        )

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor set."""
        return self.appliance.get_boolean(self.m2m_attr)

