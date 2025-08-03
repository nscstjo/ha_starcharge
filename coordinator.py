"""Data update coordinator for StarCharge."""
from datetime import timedelta
import logging
import json
import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL, CONF_URL, CONF_METHOD, CONF_HEADERS

_LOGGER = logging.getLogger(__name__)

class StarChargeDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching StarCharge data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.config = entry.data
        self.url = self.config[CONF_URL]
        self.method = self.config[CONF_METHOD]
        self.headers = self.config[CONF_HEADERS]

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self):
        """Fetch data from StarCharge API."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=self.method,
                    url=self.url,
                    headers=self.headers,
                ) as response:
                    if response.status != 200:
                        raise UpdateFailed(f"HTTP error: {response.status}")
                    data = await response.json()

                    if data.get("code") != "200":
                        raise UpdateFailed(f"API error: {data.get('code')}")

                    return data["data"]
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}")
        except json.JSONDecodeError as err:
            raise UpdateFailed(f"Invalid JSON response: {err}")