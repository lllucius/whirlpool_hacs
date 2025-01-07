"""Switch sensors for Whirlpool Appliances."""

from __future__ import annotations

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntityDescription,
    SwitchEntity,
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

        self.entity_description = SwitchEntityDescription(
            key=self.m2m_attr,
            entity_registry_enabled_default=False if self.m2m_attr in DISABLED else True,
            entity_registry_visible_default=False if self.m2m_attr in HIDDEN else True,
        )

    @property
    def is_on(self) -> bool:
        """Return true if the switch set."""
        return self.appliance.get_boolean(self.m2m_attr)

    def turn_on(self, **kwargs) -> None:
        """Turn the entity on."""
        self.appliance.set_boolean(self.m2m_attr, True)

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        await self.appliance.set_boolean(self.m2m_attr, True)

    def turn_off(self, **kwargs):
        """Turn the entity off."""
        self.appliance.set_boolean(self.m2m_attr, False)

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        await self.appliance.set_boolean(self.m2m_attr, False)

