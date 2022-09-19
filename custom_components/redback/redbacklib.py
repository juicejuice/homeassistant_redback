""" Redback Inverter library, for download of cloud portal data """

import aiohttp
import asyncio
from datetime import datetime, timedelta
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import json
from json.decoder import JSONDecodeError


class RedbackError(Exception):
    """Redback Inverter error"""


class RedbackInverter:
    """Gather Redback Inverter data from the cloud API"""

    serial = None
    _apiMethod = "private"
    _apiBaseURL = "https://portal.redbacktech.com/api/v2/"
    _apiCookie = ""
    _apiResponse = "json"
    _inverterInfo = None
    _energyData = None
    _energyDataUpdateInterval = timedelta(minutes=1)
    _energyDataNextUpdate = datetime.now()

    def __init__(self, cookie, serial, apimethod, session):
        """Constructor: needs API auth cookie and inverter serial number"""
        self._session = session
        self.serial = serial
        self._apiSerial = "?SerialNumber=" + serial
        self._apiCookie = cookie
        self._apiMethod = apimethod # stored but ignored, for now

    async def _apiRequest(self, endpoint):
        """Call into Redback cloud API"""

        if endpoint == "energyflowd2":
            # https://portal.redbacktech.com/api/v2/energyflowd2/$SERIAL
            full_url = self._apiBaseURL + endpoint + "/" + self.serial
        else:
            # https://portal.redbacktech.com/api/v2/inverterinfo?SerialNumber=$SERIAL
            full_url = self._apiBaseURL + endpoint + self._apiSerial

        try:
            response = await self._session.get(full_url, headers={"Cookie": self._apiCookie}) 
        except aiohttp.ClientSSLError as e:
            raise RedbackError(
                f"SSL Error. {e.reason}"
            ) from e
        except aiohttp.ClientResponseError as e:
            raise RedbackError(
                f"HTTP Response Error. {e.code} {e.reason} (Has the .AspNet.ApplicationCookie expired?)"
            ) from e
        except HTTPError as e:
            raise RedbackError(
                f"HTTP Error. {e.code} {e.reason} (Has the .AspNet.ApplicationCookie expired?)"
            ) from e
        except URLError as e:
            raise RedbackError(f"URL Error. {e.reason}") from e

        # collect data packet
        try:
            data = await response.json()
        except JSONDecodeError as e:
            raise RedbackError(
                f"JSON Error. {e.msg}. Pos={e.pos} Line={e.lineno} Col={e.colno}"
            ) from e

        return data

    async def getInverterInfo(self):
        """Returns inverter info (static data, updated first use only)"""

        if self._inverterInfo == None:
            self._inverterInfo = await self._apiRequest("inverterinfo")
            bannerInfo = await self._apiRequest("BannerInfo")
            self._inverterInfo["ProductDisplayname"] = bannerInfo["ProductDisplayname"]
            self._inverterInfo["InstalledPvSizeWatts"] = bannerInfo[
                "InstalledPvSizeWatts"
            ]
            self._inverterInfo["BatteryCapacityWattHours"] = bannerInfo[
                "BatteryCapacityWattHours"
            ]

        # keys: Model, Firmware, RossVersion, IsThreePhaseInverter, IsSmartBatteryInverter, IsSinglePhaseInverter, IsGridTieInverter, ProductDisplayname, InstalledPvSizeWatts, BatteryCapacityWattHours
        return self._inverterInfo

    async def getEnergyData(self):
        """Returns energy data (dynamic data, instantaneous with 60s resolution)"""

        # energy data in the cloud data store is only refreshed by the Ouija device every 60s
        if datetime.now() > self._energyDataNextUpdate or self._energyData == None:
            self._energyData = (await self._apiRequest("energyflowd2"))["Data"]["Input"]
            self._energyDataNextUpdate = datetime.now() + self._energyDataUpdateInterval

        # keys: ACLoadW, BackupLoadW, SupportsConnectedPV, PVW, ThirdPartyW, GridStatus, GridNegativeIsImportW, ConfiguredWithBatteries, BatteryNegativeIsChargingW, BatteryStatus, BatterySoC0to100, CtComms
        return self._energyData


class TestRedbackInverter(RedbackInverter):
    """Test class for Redback Inverter integration, returns sample data without any API calls"""

    async def _apiRequest(self, endpoint):
        if endpoint == "inverterinfo":
            return {
                "Model": "ST10000",
                "Firmware": "080819",
                "RossVersion": "2.15.32207.13",
                "IsThreePhaseInverter": True,
                "IsSmartBatteryInverter": False,
                "IsSinglePhaseInverter": False,
                "IsGridTieInverter": False,
            }
        elif endpoint == "BannerInfo":
            return {
                "ProductDisplayname": "Smart Inverter TEST",
                "InstalledPvSizeWatts": 9960.0,
                "BatteryCapacityWattHours": 14200.001,
            }
        elif endpoint == "energyflowd2":
            return {
                "Data": {
                    "Input": {
                        "ACLoadW": 1450.0,
                        "BackupLoadW": 11.0,
                        "SupportsConnectedPV": True,
                        "PVW": 7579.0,
                        "ThirdPartyW": None,
                        "GridStatus": "Export",
                        "GridNegativeIsImportW": 6200.0,
                        "ConfiguredWithBatteries": True,
                        "BatteryNegativeIsChargingW": 0.0,
                        "BatteryStatus": "Idle",
                        "BatterySoC0to100": 98.0,
                        "CtComms": True,
                    }
                }
            }
        else:
            raise RedbackError(f"TestRedbackInverter: unknown API endpoint {endpoint}")
