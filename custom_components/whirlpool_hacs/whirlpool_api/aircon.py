import logging
from enum import Enum

from .appliance import Appliance
from .types import ApplianceData, ApplianceKind

LOGGER = logging.getLogger(__name__)

ATTR_MODE = "Cavity_OpStatusMode"
ATTR_DISPLAY_TEMP = "Sys_OpStatusDisplayTemp"
ATTR_DISPLAY_HUMID = "Sys_OpStatusDisplayHumidity"

SETTING_REBOOT_WIFI = "XCat_WifiSetRebootWifiCommModule"
SETTING_POWER = "Sys_OpSetPowerOn"
SETTING_TEMP = "Sys_OpSetTargetTemp"
SETTING_HUMIDITY = "Sys_OpSetTargetHumidity"
SETTING_SLEEP_MODE = "Sys_OpSetSleepMode"
SETTING_HORZ_LOUVER_SWING = "Cavity_OpSetHorzLouverSwing"
SETTING_MODE = "Cavity_OpSetMode"
SETTING_FAN_SPEED = "Cavity_OpSetFanSpeed"
SETTING_TURBO_MODE = "Cavity_OpSetTurboMode"
SETTING_ECO_MODE = "Sys_OpSetEcoModeEnabled"
SETTING_QUIET_MODE = "Sys_OpSetQuietModeEnabled"
SETTING_DISPLAY_BRIGHTNESS = "Sys_DisplaySetBrightness"

ATTRVAL_MODE_COOL = "1"
ATTRVAL_MODE_FAN = "2"
ATTRVAL_MODE_HEAT = "3"
ATTRVAL_MODE_SIXTH_SENSE_AIR = "5"
ATTRVAL_MODE_SIXTH_SENSE_HEAT = "6"
ATTRVAL_MODE_SIXTH_SENSE_COOL = "7"

SETVAL_MODE_COOL = "1"
SETVAL_MODE_FAN = "2"
SETVAL_MODE_HEAT = "3"
SETVAL_MODE_SIXTH_SENSE = "4"
SETVAL_FAN_SPEED_OFF = "0"
SETVAL_FAN_SPEED_AUTO = "1"
SETVAL_FAN_SPEED_LOW = "2"
SETVAL_FAN_SPEED_MEDIUM = "4"
SETVAL_FAN_SPEED_HIGH = "6"
SETVAL_DISPLAY_BRIGHTNESS_OFF = "0"
SETVAL_DISPLAY_BRIGHTNESS_ON = "4"
SETVAL_SLEEP_MODE_OFF = "0"
SETVAL_SLEEP_MODE_ADULTS = "1"
SETVAL_SLEEP_MODE_ELDERLY = "2"
SETVAL_SLEEP_MODE_TEENS = "3"
SETVAL_SLEEP_MODE_CHILDREN = "4"


class Mode(Enum):
    Cool = 1
    Heat = 2
    Fan = 3
    SixthSense = 4


class FanSpeed(Enum):
    Off = 0
    Auto = 1
    Low = 2
    Medium = 3
    High = 4


MODES_MAP = {
    Mode.Cool: SETVAL_MODE_COOL,
    Mode.Heat: SETVAL_MODE_HEAT,
    Mode.Fan: SETVAL_MODE_FAN,
    Mode.SixthSense: SETVAL_MODE_SIXTH_SENSE,
}

FANSPEED_MAP = {
    FanSpeed.Off: SETVAL_FAN_SPEED_OFF,
    FanSpeed.Auto: SETVAL_FAN_SPEED_AUTO,
    FanSpeed.Low: SETVAL_FAN_SPEED_LOW,
    FanSpeed.Medium: SETVAL_FAN_SPEED_MEDIUM,
    FanSpeed.High: SETVAL_FAN_SPEED_HIGH,
}


class Aircon(Appliance):
    Kind = ApplianceKind.AirCon

    @staticmethod
    def wants(appliance_data: ApplianceData):
        return "airconditioner" in appliance_data.model_key.lower()

    def get_current_temp(self):
        return int(self.get_value(ATTR_DISPLAY_TEMP)) / 10

    def get_current_humidity(self):
        return int(self.get_value(ATTR_DISPLAY_HUMID))

    def get_power_on(self):
        return self.get_boolean(SETTING_POWER)

    async def set_power_on(self, on: bool):
        await self.set_boolean(SETTING_POWER, on)

    def get_temp(self):
        return int(self.get_value(SETTING_TEMP)) / 10

    async def set_temp(self, temp: float):
        tempint = int(temp * 10)
        await self.set_value(SETTING_TEMP, str(tempint))

    def get_humidity(self):
        return int(self.get_value(SETTING_HUMIDITY))

    async def set_humidity(self, temp: int):
        await self.set_value(SETTING_HUMIDITY, str(temp))

    def get_mode(self):
        mode_raw = self.get_value(ATTR_MODE)
        if mode_raw in [ATTRVAL_MODE_COOL, ATTRVAL_MODE_SIXTH_SENSE_COOL]:
            return Mode.Cool
        if mode_raw in [ATTRVAL_MODE_HEAT, ATTRVAL_MODE_SIXTH_SENSE_HEAT]:
            return Mode.Heat
        if mode_raw in [ATTRVAL_MODE_FAN, ATTRVAL_MODE_SIXTH_SENSE_AIR]:
            return Mode.Fan

    def get_sixthsense_mode(self):
        return self.get_value(SETTING_MODE) == SETVAL_MODE_SIXTH_SENSE

    async def set_mode(self, mode: Mode):
        if mode not in MODES_MAP:
            LOGGER.error("Invalid mode")
        await self.set_value(SETTING_MODE, MODES_MAP[mode])

    def get_fanspeed(self):
        fanspeed_raw = self.get_value(SETTING_FAN_SPEED)
        for k, v in FANSPEED_MAP.items():
            if v == fanspeed_raw:
                return k
        return None

    async def set_fanspeed(self, speed: FanSpeed):
        if speed not in FANSPEED_MAP:
            LOGGER.error("Invalid fan speed")
        await self.set_value(SETTING_FAN_SPEED, FANSPEED_MAP[speed])

    def get_h_louver_swing(self):
        return self.get_boolean(SETTING_HORZ_LOUVER_SWING)

    async def set_h_louver_swing(self, swing: bool):
        await self.set_boolean(SETTING_HORZ_LOUVER_SWING, swing)

    def get_turbo_mode(self):
        return self.get_boolean(SETTING_TURBO_MODE)

    async def set_turbo_mode(self, turbo: bool):
        await self.set_boolean(SETTING_TURBO_MODE, turbo)

    def get_eco_mode(self):
        return self.get_boolean(SETTING_ECO_MODE)

    async def set_eco_mode(self, eco: bool):
        await self.set_boolean(SETTING_ECO_MODE, eco)

    def get_quiet_mode(self):
        return self.get_boolean(SETTING_QUIET_MODE)

    async def set_quiet_mode(self, quiet: bool):
        await self.set_boolean(SETTING_QUIET_MODE, quiet)

    def get_display_on(self):
        return (
            self.get_value(SETTING_DISPLAY_BRIGHTNESS)
            == SETVAL_DISPLAY_BRIGHTNESS_ON
        )

    async def set_display_on(self, on: bool):
        bri = SETVAL_DISPLAY_BRIGHTNESS_ON if on else SETVAL_DISPLAY_BRIGHTNESS_OFF
        await self.set_value(SETTING_DISPLAY_BRIGHTNESS, bri)

