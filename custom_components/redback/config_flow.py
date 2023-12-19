"""Config flow for redback integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import (HomeAssistantError, ConfigEntryAuthFailed)
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
        LOGGER.debug(f"Redback API error: {e}")
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

    VERSION = 2

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
            await self.async_set_unique_id(user_input["site_id"])
            self._abort_if_unique_id_configured()
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

    async def async_step_reauth(self, entry_data: Mapping[str, Any]) -> FlowResult:
        """Handle configuration by re-auth."""
        self.reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle reauth confirmation."""
        assert self.reauth_entry is not None
        errors: dict[str, str] | None = {}

        # step 2. form completed, update with new details
        if user_input is not None:
            new = {**self.reauth_entry.data}
            new["client_id"] = user_input["client_id"]
            new["auth"] = user_input["auth"]

            # check new credentials actually work
            # (TODO: should really call validate_input() but would need to untangle some of the setup stuff)
            clientsession = async_get_clientsession(self.hass)

            if TEST_MODE:
                redback = TestRedbackInverter(
                    auth=new["auth"], auth_id=new["client_id"], apimethod=new.get("apimethod","public"), session=clientsession, site_index=new["site_index"]
                )
            else:
                redback = RedbackInverter(
                    auth=new["auth"], auth_id=new["client_id"], apimethod=new.get("apimethod","public"), session=clientsession, site_index=new["site_index"]
                )

            try:
                result = await redback.testConnection()
                assert result == True
                # it works - update the config entry and notify the user
                self.hass.config_entries.async_update_entry(self.reauth_entry, data=new)
                await self.hass.config_entries.async_reload(self.reauth_entry.entry_id)
                return self.async_abort(reason="reauth_successful")

            except (RedbackError, RedbackConnectionError) as e:
                # connection error, bail out
                LOGGER.debug(f"Connection error: {e}")
                raise CannotConnect from e

            except RedbackAPIError as e:
                # credential error, fall thru to the form to try again
                LOGGER.debug(f"Redback API error: {e}")
                errors["base"] = "invalid_auth"


        # step 1. display form to user to gather new credentials
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({
                vol.Required("client_id"): str,
                vol.Required("auth"): str
            }),
            errors=errors,
        )

class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""

class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
