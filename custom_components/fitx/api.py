from dataclasses import dataclass
from enum import StrEnum
import logging
from random import choice, randrange

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from aiohttp import ClientError, ClientResponseError, ClientSession
from homeassistant.core import HomeAssistant

import json

_LOGGER = logging.getLogger(__name__)

class API:
    """Class for API."""

    def __init__(self, hass: HomeAssistant, studioid: int) -> None:
        """Initialise."""
        self.studioid = studioid
        self._session = async_get_clientsession(hass)
        self.connected: bool = False

    async def getWorkloadPercentage(self):
        """get map data from api."""

        try:
            async with self._session.get(f"https://www.fitx.de/fitnessstudio/{self.studioid}/workload") as response:
                response.raise_for_status()
                response_text = await response.text()
                response_json = json.loads(response_text)
                studio_json = json.loads(response_json[0])
                self.connected = True
                return studio_json['workload']['percentage']
        except ClientError as exc:
            raise APIConnectionError("Unknown error.")


class APIConnectionError(Exception):
    """Exception class for connection error."""
