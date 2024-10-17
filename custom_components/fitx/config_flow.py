import voluptuous as vol
from homeassistant.config_entries import ConfigFlow
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from aiohttp import ClientError, ClientResponseError, ClientSession
import json

from homeassistant.helpers.selector import selector

from homeassistant.const import (
    CONF_LOCATION,
    CONF_ID,
    CONF_NAME
)

from .const import DOMAIN

class FitxConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovered_studios: dict[str, str] = {}

    async def async_step_user(self, formdata):
        if formdata is not None:
            websession = async_get_clientsession(self.hass)
            self._location = formdata[CONF_LOCATION]

            data = {}
            data['lat'] = formdata[CONF_LOCATION]['latitude']
            data['lon'] = formdata[CONF_LOCATION]['longitude']
            try:
                async with websession.post('https://www.fitx.de/studios/by-coordinates', data=data) as response:
                    response.raise_for_status()
                    response_json = await response.json()
                    for studio in response_json['result']:
                        studio_data = json.loads(studio)
                        name = studio_data['name']
                        branchId = studio_data['branchId']
                        self._discovered_studios[branchId] = name
                    return await self.async_step_studio(None)
            except ClientResponseError as exc:
                return self.async_abort(reason="authentication")
            except ClientError as exc:
                return self.async_abort(reason="connenction")

        data_schema = {}
        data_schema[CONF_LOCATION] = selector({
            "location": {}
        })
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(data_schema)
        )

    async def async_step_studio(self, formdata):
        if formdata is not None:
            studioid = formdata[CONF_ID]
            await self.async_set_unique_id(f"fitx-{studioid}", raise_on_progress=False)
            self._abort_if_unique_id_configured()
            data = {}
            data[CONF_ID] = studioid
            data[CONF_NAME] = self._discovered_studios[studioid]
            return self.async_create_entry(title=f"FitX {self._discovered_studios[studioid]}", data=data)
        
        if not self._discovered_studios:
            return self.async_abort(reason="no_studios_found")
        
        return self.async_show_form(
            step_id="studio", data_schema=vol.Schema(
                {vol.Required(CONF_ID): vol.In(self._discovered_studios)}
            ),
        )
