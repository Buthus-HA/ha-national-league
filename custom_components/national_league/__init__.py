"""National League (hockey sur glace suisse)."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import NationalLeagueCoordinator

PLATFORMS = [Platform.SENSOR]

type NationalLeagueConfigEntry = ConfigEntry[NationalLeagueCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: NationalLeagueConfigEntry) -> bool:
    coordinator = NationalLeagueCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: NationalLeagueConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
