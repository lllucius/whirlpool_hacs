"""Button sensors for Whirlpool Appliances."""

from __future__ import annotations

from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
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
    """Set up the Whirlpool Appliances buttones from config entry."""

    entities = await setup_entities(
        hass, config_entry, Platform.BUTTON, WhirlpoolButton
    )

    async_add_entities(entities)

class WhirlpoolButton(WhirlpoolEntity, ButtonEntity):
    """State of a button."""

    def __init__(self, device: WhirlpoolDevice, model: str) -> None:
        """Initialize the button."""
        super().__init__(device, model)

    def press(self, **kwargs) -> None:
        """Handle the button press."""
        elf.appliance.set_boolean(self.m2m_attr, True)

    async def async_press(self, **kwargs):
        """Handle the button press."""
        await elf.appliance.set_boolean(self.m2m_attr, False)


