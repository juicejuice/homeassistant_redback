"""Config flow for redback integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import LOGGER, DOMAIN, API_METHODS, TEST_MODE
from .redbacklib import RedbackInverter, TestRedbackInverter, RedbackError, RedbackAPIError, RedbackConnectionError

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Optional("displayname", default="Redback"): str,
        #vol.Required("apimethod", default=API_METHODS[0]): vol.In(API_METHODS),
        vol.Required("client_id"): str,
        vol.Required("auth"): str,
        vol.Required("site_index", default="First"): vol.In(["First", "Second", "Third", "Fourth", "Fifth", "Sixth"]),
    }
)

# Notes:
# 1. for "private" API method, client_id = Redback serial number, auth = authentication cookie
# 2. for "public" API method, client_id = Redback client ID, auth = authentication credential/secret
# *** disabled private API method for now ***

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """

    clientsession = async_get_clientsession(hass)

    # RedbackInverter is the API connection to the Redback cloud portal
    if TEST_MODE:
        redback = TestRedbackInverter(
            auth=data["auth"], auth_id=data["client_id"], apimethod=data.get("apimethod","public"), session=clientsession, site_index=data["site_index"]
        )
    else:
        redback = RedbackInverter(
            auth=data["auth"], auth_id=data["client_id"], apimethod=data.get("apimethod","public"), session=clientsession, site_index=data["site_index"]
        )

    try:
        result = await redback.testConnection()
        assert result == True
    except RedbackAPIError as e:
        LOGGER.debug(f"Validation error: {e}")
        raise InvalidAuth from e
    except (RedbackError, RedbackConnectionError) as e:
        LOGGER.debug(f"Connection error: {e}")
        raise CannotConnect from e

    # Store Redback site ID
    site_id = await redback.getSiteId()
    data["site_id"] = site_id

    # Return display name
    display_name = f"Inverter {data['site_id']}"
    if "displayname" in data and data["displayname"] != "":
        display_name = data["displayname"]
    else:
        data["displayname"] = display_name

    return {"title": display_name}


class RedbackConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for redback."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
