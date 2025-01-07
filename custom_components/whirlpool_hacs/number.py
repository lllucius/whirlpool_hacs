"""Number numbers for Whirlpool Appliances."""

from __future__ import annotations

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntityDescription,
    NumberEntity,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .device import WhirlpoolDevice
from .entity import WhirlpoolEntity, setup_entities


DISABLED: list[str] = [
]

HIDDEN: list[str] = [
    "Cavity_CycleSetDownloadAndGo",
]

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Whirlpool Appliances numbers from config entry."""

    entities = await setup_entities(
        hass, config_entry, Platform.NUMBER, WhirlpoolNumber,
    )

    async_add_entities(entities)

class WhirlpoolNumber(WhirlpoolEntity, NumberEntity):
    """State of a number."""

    def __init__(self, device: WhirlpoolDevice, model: str) -> None:
        """Initialize the number."""
        super().__init__(device, model)

        self.entity_description = NumberEntityDescription(
            key=self.m2m_attr,
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False if self.m2m_attr in DISABLED else True,
            entity_registry_visible_default=False if self.m2m_attr in HIDDEN else True,
            native_max_value=self.model["RangeValues"]["Max"],
            native_min_value=self.model["RangeValues"]["Min"],
            native_step=self.model["RangeValues"]["StepSize"],
        )

    @property
    def native_value(self) -> float | None:
        """Return the value reported by the number."""
        return float(self.appliance.get_value(self.m2m_attr))

    def set_native_value(self, value: float) -> None:
        """Update the current value."""
        self.appliance.set_value(self.m2m_attr, str(value))

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        await self.appliance.set_value(self.m2m_attr, str(value))

