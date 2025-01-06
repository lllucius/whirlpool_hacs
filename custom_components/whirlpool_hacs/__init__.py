"""The Whirlpool Appliances integration."""

from dataclasses import dataclass
import asyncio
import os

from aiohttp import ClientError
from .whirlpool_api.appliancesmanager import AppliancesManager
from .whirlpool_api.auth import Auth
from .whirlpool_api.backendselector import BackendSelector
from .whirlpool_api.types import ApplianceKind

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_REGION, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_BRAND, CONF_BRANDS_MAP, CONF_REGIONS_MAP, DOMAIN
from .entity import entity_type
from .device import (
    WhirlpoolAirconDevice,
    WhirlpoolDryerDevice,
    WhirlpoolOvenDevice,
    WhirlpoolWasherDevice,
    WhirlpoolWasherDryerDevice
)

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.SWITCH,
#    Platform.LIGHT,
    Platform.SELECT,
    Platform.SENSOR,
]

type WhirlpoolConfigEntry = ConfigEntry[WhirlpoolData]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Whirlpool Appliances from a config entry."""

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {}

    session = async_get_clientsession(hass)
    region = CONF_REGIONS_MAP[entry.data.get(CONF_REGION, "EU")]
    brand = CONF_BRANDS_MAP[entry.data.get(CONF_BRAND, "Whirlpool")]
    backend_selector = BackendSelector(brand, region)
    auth = Auth(
        backend_selector,
        entry.data[CONF_USERNAME],
        entry.data[CONF_PASSWORD],
        session,
    )

    try:
        await auth.do_auth(store=False)
    except (ClientError, TimeoutError) as err:
        raise ConfigEntryNotReady("Unable to connect to Whirlpool") from err

    if not auth.is_access_token_valid():
        raise ConfigEntryAuthFailed("Incorrect password")

    appliances_manager = AppliancesManager(backend_selector, auth, session)
    if not await appliances_manager.fetch_appliances():
        raise ConfigEntryNotReady("Unable to fetch appliances from Whirlpool")

    await appliances_manager.connect()

    hass.data[DOMAIN][entry.entry_id] = {}
    for app in appliances_manager.get_appliances():
        match app.Kind:
            case ApplianceKind.AirCon:
                device = WhirlpoolAirconDevice(
                    hass, appliances_manager, app
                )
            case ApplianceKind.Dryer:
                device = WhirlpoolDryerDevice(
                    hass, appliances_manager, app
                )
            case ApplianceKind.Oven:
                device = WhirlpoolOvenDevice(
                    hass, appliances_manager, app
                )
            case ApplianceKind.Washer:
                device = WhirlpoolWasherDevice(
                    hass, appliances_manager, app
                )
            case ApplianceKind.WasherDryer:
                device = WhirlpoolWasherDryerDevice(
                    hass, appliances_manager, app
                )
        
        hass.data[DOMAIN][entry.entry_id][
            app.said
        ] = device

    entry.runtime_data = WhirlpoolData(appliances_manager, auth, backend_selector)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    if "GEN_WHIRLPOOL_STRINGS" in os.environ:
        write_strings(appliances_manager)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

@dataclass
class WhirlpoolData:
    """Whirlpool integaration shared data."""

    manager: AppliancesManager
    auth: Auth
    backend: BackendSelector
