"""Select selects for Whirlpool Appliances."""

from __future__ import annotations

from homeassistant.components.select import (
    SelectEntityDescription,
    SelectEntity,
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
    """Set up the Whirlpool Appliances selects from config entry."""

    entities = await setup_entities(
        hass, config_entry, Platform.SELECT, WhirlpoolSelect
    )

    async_add_entities(entities)

class WhirlpoolSelect(WhirlpoolEntity, SelectEntity):
    """State of a select."""

    def __init__(self, device: WhirlpoolDevice, model: str) -> None:
        """Initialize the select."""
        super().__init__(device, model)

        self.entity_description = SelectEntityDescription(
            key=self.m2m_attr,
            entity_registry_enabled_default=False if self.m2m_attr in DISABLED else True,
            entity_registry_visible_default=False if self.m2m_attr in HIDDEN else True,
            options=self.appliance.get_enum_values(self.m2m_attr),
        )

    @property
    def current_option(self) -> str:
        """Return true if the sensor set."""
        return self.appliance.get_enum(self.m2m_attr)

    def select_option(self, option: str) -> None:
        """Change the selected option."""
        self.appliance.set_enum(self.m2m_attr, option)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        await self.appliance.set_enum(self.m2m_attr, option)

