"""Base entity class for Whirlpool Appliances entities."""

from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import DOMAIN
from .device import WhirlpoolOvenDevice, get_brand_from_model

def entity_type(model: dict[str, str]) -> Platform:
    if model["DataType"] == "Boolean":
        if model["DeviceIO"] == "RO":
            return Platform.BINARY_SENSOR
        if model["DeviceIO"] == "RW":
            return Platform.SWITCH
        if model["DeviceIO"] == "WO":
            return Platform.BUTTON
    elif model["DataType"] == "enum":
        if model["DeviceIO"] == "RO":
            return Platform.SENSOR
        if model["DeviceIO"] == "RW":
            return Platform.SELECT
    return None

async def setup_entities(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    platform: Platform,
    entity_class: WhirlpoolEntity,
    excludes: list[str] = []
) -> list[WhirlpoolEntity]:
    """ Common entity creator """

    entities = []
    for device in hass.data[DOMAIN][config_entry.entry_id].values():
        device: WhirlpoolDevice

        attrs = device.appliance.data_attrs
        for model in attrs.values():
            if model["AttributeName"] not in excludes:
                if entity_type(model) == platform:
                   entities.extend([entity_class(device, model)])
    return entities

class WhirlpoolEntity(Entity):
    """A base class for Whirlpool Appliances entities."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_force_update = False

    def __init__(self, device: WhirlpoolDevice, model: str, **kwargs) -> None:
        """Initialize the Whirlpool entity."""
        self.device: list[WhirlpoolDevice] = device
        self.appliance: Appliance = self.device.appliance
        self.model: str = model
        self.m2m_attr = self.model["M2MAttributeName"]

        self.translation_key = self.m2m_attr
        self._attr_unique_id = f"{self.device.config_entry.unique_id}-{self.m2m_attr}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return a device description for device registry."""

        return DeviceInfo(
            identifiers={(DOMAIN, self.appliance.said)},
            name=self.appliance.name.title(),
            manufacturer=get_brand_from_model(
                self.appliance.model_number,
            ),
            model=self.appliance.model_number,
            serial_number=self.appliance.serial_number
        )

    async def async_added_to_hass(self) -> None:
        """Register for device state updates."""
        self.appliance.register_attr_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        """Unegister from device state updates."""
        self.appliance.unregister_attr_callback(self.async_write_ha_state)

    @property
    def available(self) -> bool:
        """Return True if device is available."""
        return self.appliance.get_online()

