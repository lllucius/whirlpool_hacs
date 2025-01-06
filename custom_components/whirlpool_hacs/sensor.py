"""Sensor sensors for Whirlpool Appliances."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
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
    """Set up the Whirlpool Appliances sensors from config entry."""

    entities = await setup_entities(
        hass, config_entry, Platform.SENSOR, WhirlpoolSensor
    )

    async_add_entities(entities)

class WhirlpoolSensor(WhirlpoolEntity, SensorEntity):
    """State of a sensor."""

    _attr_device_class = SensorDeviceClass.ENUM

    def __init__(self, device: WhirlpoolDevice, model: dict(str, str)) -> None:
        """Initialize the sensor."""
        super().__init__(device, model)

    @property
    def native_value(self) -> str:
        """Return true if the sensor set."""
        return self.appliance.get_enum(self.m2m_attr)

    @property
    def options(self) -> list[str]:
        """Return true if the sensor set."""
        return self.appliance.get_enum_values(self.m2m_attr)


