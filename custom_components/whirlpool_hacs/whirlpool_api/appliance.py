import logging
import typing
from functools import wraps
from typing import Callable

from .types import ApplianceData, ApplianceKind

if typing.TYPE_CHECKING:
    from .appliancesmanager import AppliancesManager

LOGGER = logging.getLogger(__name__)

ATTR_ONLINE = "Online"

SETVAL_VALUE_OFF = "0"
SETVAL_VALUE_ON = "1"

class Appliance:
    """Whirlpool appliance class"""

    handlers = list()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if not hasattr(cls, "Kind"):
            LOGGER.error("appliance class missing Kind attribute")
            return

        if hasattr(cls, "Model"):
            Appliance.handlers.insert(0, cls)
        else:
            Appliance.handlers.append(cls)

    @staticmethod
    def wants(appliance_data: ApplianceData):
        return False

    def __init__(
        self,
        app_manager: "AppliancesManager",
        appliance_data: ApplianceData,
    ):
        self._app_manager = app_manager
        self._attr_changed: list[Callable] = []
        self._data_dict: dict = {}
        self._data_model: dict = {}
        self._data_attrs: dict = {}
        self._appliance_data = appliance_data

    def __str__(self):
        return str(self._appliance_data)

    @property
    def said(self) -> str:
        """Return Appliance SAID"""
        return self._appliance_data.said

    @property
    def name(self) -> str:
        """Return Appliance name"""
        return self._appliance_data.name

    @property
    def model_number(self) -> str:
        """Return Appliance model number"""
        return self._appliance_data.model_number
 
    @property
    def serial_number(self) -> str:
        """Return Appliance serial number"""
        return self._appliance_data.serial_number
 
    @property
    def data(self) -> dict:
        return self._data_dict

    @data.setter
    def data(self, value):
        self._data_dict = value
        for callback in self._attr_changed:
            callback()

    @property
    def data_model(self) -> dict:
        return self._data_model

    @data_model.setter
    def data_model(self, value):
        self._data_model = value

    @property
    def data_attrs(self) -> dict:
        return self._data_attrs

    @data_attrs.setter
    def data_attrs(self, value):
        self._data_attrs = value

    def get_boolean(self, attr: str) -> bool:
        return self.get_attribute(attr) == "1"

    async def set_boolean(self, attr: str, val: bool) -> None:
        val = SETVAL_VALUE_ON if val else SETVAL_VALUE_OFF
        await self._app_manager.send_attributes(self, {attr: val})

    def get_enum(self, attr: str) -> str | None:
        val = self.get_attribute(attr)
        if not val or attr not in self.data_attrs:
            return None
        return self.data_attrs[attr]["EnumValues"].get(val, None)

    def get_enum_values(self, attr: str) -> list[str] | None:
        return list(self.data_attrs[attr]["EnumValues"].values())

    async def set_enum(self, attr: str, val: str) -> None:
        key = [k for k, v in self.data_attrs[attr]["EnumValues"].items() if v == val][0]
        await self._app_manager.send_attributes(self, {attr: key})

    def get_value(self, attr: str) -> str | None:
        return self.get_attribute(attr)

    async def set_value(self, attr: str, val: str) -> None:
        await self._app_manager.send_attributes(self, {attr: val})

    async def set_values(self, attrs: dict[str, str]) -> bool:
        """Send attributes to appliance api"""
        return await self._app_manager.send_attributes(self, attrs)

    def get_online(self) -> bool | None:
        """Get online state for appliance"""
        return self.get_boolean(ATTR_ONLINE)

    async def fetch_data(self):
        await self._app_manager.fetch_appliance_data(self)

    def register_attr_callback(self, update_callback: Callable):
        """Register Callback function."""
        self._attr_changed.append(update_callback)
        LOGGER.debug("Registered attr callback")

    def unregister_attr_callback(self, update_callback: Callable):
        """Unregister callback function."""
        try:
            self._attr_changed.remove(update_callback)
            LOGGER.debug("Unregistered attr callback")
        except ValueError:
            LOGGER.error("Attr callback not found")

    def has_attribute(self, attribute: str) -> bool:
        """Check for attribute in local data dictionary"""
        if not self.data:
            LOGGER.error("No data available")
            return False
        return attribute in self.data.get("attributes", {})

    def get_attribute(self, attribute: str) -> str | None:
        """Get attribute from local data dictionary"""
        if not self.has_attribute(attribute):
            return None
        return self._data_dict["attributes"][attribute]["value"]

    def _set_attribute(self, attribute: str, value: str, timestamp: int):
        print("SETTING", attribute, "VALUE", value, "TIME", timestamp)

        if self.has_attribute(attribute):
            LOGGER.debug(f"Updating attribute {attribute} with {value} ({timestamp})")
            self._data_dict["attributes"][attribute]["value"] = value
            self._data_dict["attributes"][attribute]["updateTime"] = timestamp

    def _set_attributes(self, attrs: dict, timestamp: str):
        for attr, val in attrs:
            self._set_attribute(attr, str(val), timestamp)

        for callback in self._attr_changed:
            callback()


