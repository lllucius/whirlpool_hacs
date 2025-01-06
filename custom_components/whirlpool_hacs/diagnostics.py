"""Diagnostics support for Whirlpool."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from . import WhirlpoolConfigEntry

TO_REDACT = {
    "SERIAL_NUMBER",
    "macaddress",
    "username",
    "password",
    "title",
    "token",
    "unique_id",
    "SAID",
    "_id",
    "applianceId",
    "XCat_ApplianceInfoSetSerialNumber",
    "XCat_PersistentInfoSaid",
    "XCat_PersistentInfoMacAddress",
    "MAC_Address",
    "SerialNumber"
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    config_entry: WhirlpoolConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    whirlpool = config_entry.runtime_data
    diagnostics_data = whirlpool.manager.get_appliances()

    ndx = 0
    data = {}
    for app in whirlpool.manager.get_appliances():
        data[ndx] = {
            "kind": app.Kind,
            "data": app.data,
            "model": app.data_model
        }
        ndx = ndx + 1

    return {
        "appliances": async_redact_data(data, TO_REDACT)
    }

async def async_get_device_diagnostics(
    hass: HomeAssistant,
    config_entry: WhirlpoolConfigEntry,
    device: DeviceEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    whirlpool = config_entry.runtime_data
    diagnostics_data = whirlpool.manager.get_appliances()
    said = list(list(device.identifiers)[0])[1]
    appliance = whirlpool.manager.get_appliance(said)

    return {
        "data_dict": async_redact_data(appliance.data, TO_REDACT),
        "data_model": async_redact_data(appliance.data_model, TO_REDACT),
    }
