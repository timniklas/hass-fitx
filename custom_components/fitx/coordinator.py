from dataclasses import dataclass
from datetime import timedelta
import logging

import re

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_ID,
    CONF_NAME
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import API
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass
class FitxAPIData:
    """Class to hold api data."""

    workload_percentage: int


class FitxCoordinator(DataUpdateCoordinator):
    """My coordinator."""

    data: FitxAPIData

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize coordinator."""

        # Set variables from values entered in config flow setup
        self.studio_name = config_entry.data[CONF_NAME]
        self.studio_id = config_entry.data[CONF_ID]

        # Initialise DataUpdateCoordinator
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} ({config_entry.unique_id})",
            # Method to call on every update interval.
            update_method=self.async_update_data,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=60),
        )

        # Initialise your api here
        self.api = API(hass, studioid=self.studio_id)

    async def async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            workload_percentage = await self.api.getWorkloadPercentage()
            return FitxAPIData(workload_percentage=workload_percentage)
        except Exception as err:
            # This will show entities as unavailable by raising UpdateFailed exception
            raise UpdateFailed(f"Error communicating with API: {err}") from err
