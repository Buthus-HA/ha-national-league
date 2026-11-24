"""Capteurs : prochain match, dernier résultat, classement."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import NationalLeagueConfigEntry
from . import model
from .const import ATTRIBUTION, CONF_TEAM_NAME, DOMAIN, RESULTS_COUNT, UPCOMING_COUNT
from .coordinator import NationalLeagueCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: NationalLeagueConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    c = entry.runtime_data
    async_add_entities([NextGameSensor(c), LastResultSensor(c), RankSensor(c)])


class _Base(CoordinatorEntity[NationalLeagueCoordinator], SensorEntity):
    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION
    _key = ""

    def __init__(self, coordinator: NationalLeagueCoordinator) -> None:
        super().__init__(coordinator)
        entry = coordinator.config_entry
        self._attr_unique_id = f"{entry.entry_id}_{self._key}"
        self._attr_translation_key = self._key
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.data[CONF_TEAM_NAME],
            manufacturer="National League",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://www.nationalleague.ch/",
        )


class NextGameSensor(_Base):
    _key = "next_game"
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:hockey-sticks"

    @property
    def native_value(self):
        up = self.coordinator.data["upcoming"]
        return model.parse_date(up[0]["date"]) if up else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        up = self.coordinator.data["upcoming"]
        first = up[0] if up else {}
        return {
            "opponent": first.get("opponent"),
            "home": first.get("home"),
            "arena": first.get("arena"),
            "upcoming": [
                {k: g[k] for k in ("date", "opponent", "opponent_short", "home", "arena")} for g in up[:UPCOMING_COUNT]
            ],
        }


class LastResultSensor(_Base):
    _key = "last_result"
    _attr_icon = "mdi:scoreboard-outline"

    @property
    def native_value(self) -> str | None:
        res = self.coordinator.data["results"]
        return f"{res[0]['score']} ({res[0]['result']})" if res else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        res = self.coordinator.data["results"]
        first = res[0] if res else {}
        return {
            "opponent": first.get("opponent"),
            "home": first.get("home"),
            "date": first.get("date"),
            "result": first.get("result"),
            "result_label": first.get("result_label"),
            "win": first.get("win"),
            "results": [
                {k: g[k] for k in ("date", "opponent", "opponent_short", "home", "score", "result", "result_label", "win")}
                for g in res[:RESULTS_COUNT]
            ],
        }


class RankSensor(_Base):
    _key = "rank"
    _attr_icon = "mdi:podium"

    @property
    def native_value(self) -> int | None:
        team = self.coordinator.data["team"]
        return team["rank"] if team else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        team = self.coordinator.data["team"] or {}
        return {
            "points": team.get("points"),
            "games_played": team.get("gp"),
            "goal_diff": team.get("goal_diff"),
            "streak": team.get("streak"),
            "standings": self.coordinator.data["standings"],
        }
