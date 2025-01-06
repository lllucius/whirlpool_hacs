from abc import ABC, abstractmethod
import json
import logging
import typing
from typing import Any

import aiohttp
import async_timeout

from .eventsocket import EventSocket

from .appliance import Appliance
from .auth import Auth
from .backendselector import BackendSelector
from .types import ApplianceData, ApplianceKind

if typing.TYPE_CHECKING:
    from .appliance import Appliance


LOGGER = logging.getLogger(__name__)
REQUEST_RETRY_COUNT = 3

class AppliancesManager:
    def __init__(
        self,
        backend_selector: BackendSelector,
        auth: Auth,
        session: aiohttp.ClientSession,
    ):
        self._backend_selector = backend_selector
        self._auth = auth
        self._session: aiohttp.ClientSession = session
        self._event_socket: EventSocket = None
        self._app_dict: dict[str, Any] = {}

    def _create_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._auth.get_access_token()}",
            "Content-Type": "application/json",
            "User-Agent": "okhttp/3.12.0",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache"
        }

    async def _add_appliance(self, appliance: dict[str, Any]) -> None:
        app_data = ApplianceData(
            said=appliance["SAID"],
            name=appliance["APPLIANCE_NAME"],
            model_key=appliance["DATA_MODEL_KEY"],
            category=appliance["CATEGORY_NAME"],
            model_number=appliance.get("MODEL_NO"),
            serial_number=appliance.get("SERIAL"),
        )

        app = None
        for handler in Appliance.handlers:
            if handler.wants(app_data):
                app = handler(self, app_data)
                break

        if app is None:            
            LOGGER.warning("Unsupported appliance data model %s", app_data.data_model)
            return

        await self.fetch_appliance_data_model(app)
        data_model = app.data_model[app_data.said]
        """
        with open("./dryer_model.json", "r") as dm:
            data_model = json.load(dm)[app_data.said]
        """
        attrs = {}
        for attr in data_model["dataModel"]["attributes"]:
            if attr["Instance"]:
                attrs[attr["MappedAttributeName"]] = attr
        
        app.data_attrs = attrs

        self._app_dict[app_data.said] = app

    async def _get_owned_appliances(self, account_id: str) -> bool:
        async with self._session.get(
            f"{self._backend_selector.get_owned_appliances_url}/{account_id}",
            headers=self._create_headers(),
        ) as r:
            if r.status != 200:
                LOGGER.error(f"Failed to get appliances: {r.status}")
                return False

            data = await r.json()
            locations: dict[str, Any] = data[str(account_id)]
            for appliances in locations.values():
                for appliance in appliances:
                    await self._add_appliance(appliance)

            return True

    async def _get_shared_appliances(self) -> bool:
        headers = self._create_headers()
        headers["WP-CLIENT-BRAND"] = self._backend_selector.brand.name

        async with self._session.get(
            self._backend_selector.get_shared_appliances_url, headers=headers
        ) as r:
            if r.status != 200:
                LOGGER.error(f"Failed to get shared appliances: {r.status}")
                return False

            data = await r.json()
            locations: list[dict[str, Any]] = data["sharedAppliances"]
            for appliances in locations:
                for appliance in appliances["appliances"]:
                    await self._add_appliance(appliance)

            return True

    async def _get_account_id(self):
        """Returns the accountId from the auth object, or fetches it from the backend if not present."""
        if self._auth.get_account_id():
            return self._auth.get_account_id()

        async with self._session.get(
            self._backend_selector.get_user_data_url, headers=self._create_headers()
        ) as r:
            if r.status != 200:
                LOGGER.error(f"Failed to get account id: {r.status}")
                return False
            data = await r.json()
            return data["accountId"]

    def get_appliances(self, kind: ApplianceKind = None) -> list["Appliance"]:
        if not kind:
            return list(self._app_dict.values())
        return [app for app in self._app_dict.values() if app.Kind == kind]

    def get_appliance(self, said: str) -> Appliance:
        return self._app_dict.get(said, None)

    async def fetch_appliances(self):
        account_id = await self._get_account_id()
        success_owned = await self._get_owned_appliances(account_id)
        success_shared = await self._get_shared_appliances()

        return success_owned or success_shared

    async def fetch_appliance_data(self, appliance: Appliance) -> bool:
        """Fetch appliance data from web api"""
        if not self._session:
            LOGGER.error("Session not started")
            return False
        uri = f"{self._backend_selector.get_appliance_data_url}/{appliance.said}"
        for _ in range(REQUEST_RETRY_COUNT):
            async with async_timeout.timeout(30):
                async with self._session.get(uri, headers=self._create_headers()) as r:
                    if r.status == 200:
                        appliance.data = json.loads(await r.text())
                        return True
                    elif r.status == 401:
                        LOGGER.error(
                            "Fetching data failed (%s). Doing reauth", r.status
                        )
                        await self._auth.do_auth()
                    else:
                        LOGGER.error("Fetching data failed (%s)", r.status)
        return False

    async def fetch_appliance_data_model(self, appliance: Appliance) -> bool:
        headers = self._create_headers()
        headers["WP-CLIENT-COUNTRY"] = self._backend_selector.region.name
        headers["WP-CLIENT-BRAND"] = self._backend_selector.brand.name
        data={"saIdList": [appliance.said]}
        url=f"{self._backend_selector.get_data_model_url}"

        """Fetch appliance data from web api"""
        if not self._session:
            LOGGER.error("Session not started")
            return False
        for _ in range(REQUEST_RETRY_COUNT):
            async with async_timeout.timeout(30):
                async with self._session.post(url, json=data, headers=headers) as r:
                    if r.status == 200:
                        appliance.data_model = json.loads(await r.text())
                        return True
                    elif r.status == 403:
                        LOGGER.error(
                            "Fetching data failed (%s). Doing reauth", r.status
                        )
                        return False
                    elif r.status == 401:
                        LOGGER.error(
                            "Fetching data failed (%s). Doing reauth", r.status
                        )
                        await self._auth.do_auth()
                    else:
                        LOGGER.error("Fetching data failed (%s)", r.status)
        return False

    async def send_attributes(
        self,
        appliance: Appliance,
        attributes: dict[str, str]
    ) -> bool:
        """Send attributes to appliance api"""
        if not self._session:
            LOGGER.error("Session not started")
            return False

        print("SEND ATTR", attributes)

        LOGGER.info(f"Sending attributes: {attributes}")

        cmd_data = {
            "body": attributes,
            "header": {"said": appliance.said, "command": "setAttributes"},
        }
        for _ in range(REQUEST_RETRY_COUNT):
            async with async_timeout.timeout(30):
                async with self._session.post(
                    self._backend_selector.post_appliance_command_url,
                    json=cmd_data,
                    headers=self._create_headers(),
                ) as r:
                    LOGGER.debug(f"Reply: {await r.text()}")
                    if r.status == 200:
                        return True
                    elif r.status == 401:
                        await self._auth.do_auth()
                        continue
                    LOGGER.error(f"Sending attributes failed ({r.status})")
        return False

    async def connect(self):
        """Connect to appliance event listener"""
        await self.start_event_listener()

    async def disconnect(self):
        """Disconnect from appliance event listener"""
        await self.stop_event_listener()

    async def start_event_listener(self):
        """Start the appliance event listener"""
        await self.fetch_all_data()
        if self._event_socket is not None:
            LOGGER.warning("Event socket not None when starting event listener")

        self._event_socket = EventSocket(
            await self._getWebsocketUrl(),
            self._auth,
            list(self._app_dict.keys()),
            self._event_socket_callback,
            self.fetch_all_data,
            self._session,
        )
        self._event_socket.start()

    async def stop_event_listener(self):
        """Stop the appliance event listener"""
        await self._event_socket.stop()
        self._event_socket = None

    async def fetch_all_data(self):
        for appliance in self._app_dict.values():
            await self.fetch_appliance_data(appliance)

    def _event_socket_callback(self, msg: str):
        LOGGER.debug(f"Manager event socket message: {msg}")
        json_msg = json.loads(msg)
        said = json_msg["said"]
        app = self._app_dict.get(said)
        if app is None:
            LOGGER.error(f"Received message for unknown appliance {said}")
            return

        app._set_attributes(json_msg["attributeMap"].items(), json_msg["timestamp"])

    async def _getWebsocketUrl(self) -> str:
        DEFAULT_WS_URL = "wss://ws.emeaprod.aws.whrcloud.com/appliance/websocket"
        async with self._session.get(
            self._backend_selector.ws_url, headers=self._create_headers()
        ) as r:
            if r.status != 200:
                LOGGER.error(f"Failed to get websocket url: {r.status}")
                return DEFAULT_WS_URL
            try:
                return json.loads(await r.text())["url"]
            except KeyError:
                LOGGER.error(f"Failed to get websocket url: {r.status}")
                return DEFAULT_WS_URL
