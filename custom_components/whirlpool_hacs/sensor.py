"""Sensor sensors for Whirlpool Appliances."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorEntity,
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
    "XCat_ConfigSetMaxCustomCycles",
    "XCat_WifiStatusRssiAntennaDiversity",
]

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

        self.entity_description = SensorEntityDescription(
            key=self.m2m_attr,
            entity_registry_enabled_default=False if self.m2m_attr in DISABLED else True,
            entity_registry_visible_default=False if self.m2m_attr in HIDDEN else True,
        )

    @property
    def native_value(self) -> str:
        """Return true if the sensor set."""
        if "Integer" in self.model["DataType"]:
            return self.appliance.get_value(self.m2m_attr)
        return self.appliance.get_enum(self.m2m_attr)

    @property
    def options(self) -> list[str]:
        """Return true if the sensor set."""
        if "Integer" in self.model["DataType"]:
            return [self.native_value]
        return self.appliance.get_enum_values(self.m2m_attr)


