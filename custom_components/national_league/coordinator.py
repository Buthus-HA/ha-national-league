"""Récupération des données et rythme d'interrogation adaptatif."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from . import model
from .api import NationalLeagueApi, NationalLeagueError
from .const import (
    CONF_TEAM_ID,
    DOMAIN,
    EVENT_GAME_FINISHED,
    INTERVAL_IDLE,
    INTERVAL_LIVE,
    INTERVAL_MATCHDAY,
    LIVE_WINDOW_AFTER,
    LIVE_WINDOW_BEFORE,
)

_LOGGER = logging.getLogger(__name__)


class NationalLeagueCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, _LOGGER, config_entry=entry, name=DOMAIN, update_interval=INTERVAL_IDLE)
        self.team_id: str = str(entry.data[CONF_TEAM_ID])
        self.api = NationalLeagueApi(async_get_clientsession(hass))
        self._finished_ids: set[str] | None = None

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            teams = await self.api.teams()
            games = await self.api.team_games(self.team_id)
        except NationalLeagueError as err:
            raise UpdateFailed(f"nationalleague.ch injoignable : {err}") from err

        upcoming, results = model.split_games(games, self.team_id)
        table = model.standings(teams)
        team = next((t for t in table if t["team_id"] == self.team_id), None)

        self._fire_finished_events(results)
        self.update_interval = self._next_interval(upcoming)

        return {"team": team, "standings": table, "upcoming": upcoming, "results": results}

    def _fire_finished_events(self, results: list[dict[str, Any]]) -> None:
        ids = {g["id"] for g in results}
        if self._finished_ids is not None:
            for game in results:
                if game["id"] not in self._finished_ids:
                    self.hass.bus.async_fire(
                        EVENT_GAME_FINISHED,
                        {k: game[k] for k in ("id", "date", "opponent", "home", "score", "result", "result_label", "win")},
                    )
        self._finished_ids = ids

    def _next_interval(self, upcoming: list[dict[str, Any]]):
        if not upcoming:
            return INTERVAL_IDLE
        now = dt_util.utcnow()
        start = model.parse_date(upcoming[0]["date"])
        if start - LIVE_WINDOW_BEFORE <= now <= start + LIVE_WINDOW_AFTER:
            return INTERVAL_LIVE
        if dt_util.as_local(start).date() == dt_util.as_local(now).date() and now < start:
            return INTERVAL_MATCHDAY
        return INTERVAL_IDLE
