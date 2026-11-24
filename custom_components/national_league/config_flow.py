"""Assistant : choix de l'équipe à suivre."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import SelectOptionDict, SelectSelector, SelectSelectorConfig

from .api import NationalLeagueApi, NationalLeagueError
from .const import CONF_TEAM_ID, CONF_TEAM_NAME, DOMAIN


class NationalLeagueConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._teams: dict[str, str] = {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if not self._teams:
            try:
                teams = await NationalLeagueApi(async_get_clientsession(self.hass)).teams()
                self._teams = {str(t["teamId"]): t["name"] for t in sorted(teams, key=lambda t: t["name"])}
            except NationalLeagueError:
                errors["base"] = "cannot_connect"

        if user_input is not None and self._teams:
            team_id = user_input[CONF_TEAM_ID]
            await self.async_set_unique_id(team_id)
            self._abort_if_unique_id_configured()
            name = self._teams[team_id]
            return self.async_create_entry(title=name, data={CONF_TEAM_ID: team_id, CONF_TEAM_NAME: name})

        options = [SelectOptionDict(value=k, label=v) for k, v in self._teams.items()]
        default = "103138" if "103138" in self._teams else vol.UNDEFINED
        schema = vol.Schema(
            {vol.Required(CONF_TEAM_ID, default=default): SelectSelector(SelectSelectorConfig(options=options))}
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
