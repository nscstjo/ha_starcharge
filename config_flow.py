"""Config flow for StarCharge integration."""
from __future__ import annotations

import json
import logging
import voluptuous as vol
import aiohttp

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, CONF_URL, CONF_METHOD, CONF_HEADERS

_LOGGER = logging.getLogger(__name__)

class StarChargeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for StarCharge."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                config = await self._validate_input(user_input)
                return self.async_create_entry(
                    title=f"StarCharge API",
                    data=config,
                )
            except InvalidJSON:
                errors["base"] = "invalid_json"
            except InvalidAPIConfig:
                errors["base"] = "invalid_api_config"
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("config_json"): str,
                }
            ),
            errors=errors,
        )

    async def _validate_input(self, user_input):
        """Validate the user input allows us to connect."""
        try:
            config_json = json.loads(user_input["config_json"])
        except json.JSONDecodeError:
            raise InvalidJSON

        # 检查必要字段
        if not all(k in config_json for k in (CONF_URL, CONF_METHOD, CONF_HEADERS)):
            raise InvalidAPIConfig

        # 尝试连接 API
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=config_json[CONF_METHOD],
                    url=config_json[CONF_URL],
                    headers=config_json[CONF_HEADERS],
                ) as response:
                    if response.status != 200:
                        raise CannotConnect
                    data = await response.json()
                    if data.get("code") != "200":
                        raise CannotConnect
        except (aiohttp.ClientError, json.JSONDecodeError):
            raise CannotConnect

        return config_json


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidJSON(HomeAssistantError):
    """Error to indicate the JSON is invalid."""


class InvalidAPIConfig(HomeAssistantError):
    """Error to indicate the API configuration is invalid."""