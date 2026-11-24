import copy
import json
from pathlib import Path

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_capture_events

from custom_components.national_league.const import API_BASE, DOMAIN, EVENT_GAME_FINISHED

HERE = Path(__file__).parent
TEAMS = json.loads((HERE / "teams.json").read_text(encoding="utf-8"))
GAMES = json.loads((HERE / "games_team.json").read_text(encoding="utf-8"))


def mock_api(aioclient_mock, games=GAMES):
    aioclient_mock.clear_requests()
    aioclient_mock.get(f"{API_BASE}/teams", json=TEAMS)
    aioclient_mock.get(f"{API_BASE}/games/team/103138", json=games)


async def test_config_flow(hass: HomeAssistant, aioclient_mock) -> None:
    mock_api(aioclient_mock)
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {"team_id": "103138"})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Fribourg-Gottéron"
    await hass.async_block_till_done()


async def test_sensors_and_event(hass: HomeAssistant, aioclient_mock) -> None:
    mock_api(aioclient_mock)
    entry = MockConfigEntry(domain=DOMAIN, unique_id="103138",
                            data={"team_id": "103138", "team_name": "Fribourg-Gottéron"})
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    states = {s.entity_id: s for s in hass.states.async_all("sensor")}
    nxt = next(s for e, s in states.items() if "next_game" in e or "prochain" in e)
    last = next(s for e, s in states.items() if "last_result" in e or "dernier" in e)
    rank = next(s for e, s in states.items() if "standing" in e or "classement" in e)
    assert nxt.state.startswith("2026-11-24T18:45")
    assert nxt.attributes["opponent"] == "ZSC Lions" and nxt.attributes["home"] is True
    assert len(nxt.attributes["upcoming"]) == 5
    assert last.state == "1-2 (L)" and last.attributes["opponent"] == "HC Ajoie"
    assert [r["score"] for r in last.attributes["results"][:3]] == ["1-2", "3-0", "2-4"]
    assert rank.state == "8" and rank.attributes["points"] == 31
    assert rank.attributes["entity_picture"].endswith("/teams/103138/logo")
    assert last.attributes["entity_picture"].endswith("/teams/103144/logo")  # HC Ajoie
    assert len(rank.attributes["standings"]) == 14

    # Le prochain match (ZSC) se termine 5-2 -> un événement
    events = async_capture_events(hass, EVENT_GAME_FINISHED)
    games = copy.deepcopy(GAMES)
    g = next(x for x in games if x["gameId"] == "20271105000164")
    g.update(status="finished", baseStatus="finished", homeTeamResult=5, awayTeamResult=2)
    mock_api(aioclient_mock, games)
    await entry.runtime_data.async_refresh()
    await hass.async_block_till_done()
    assert len(events) == 1
    assert events[0].data["opponent"] == "ZSC Lions" and events[0].data["score"] == "5-2" and events[0].data["win"]
    assert hass.states.get(last.entity_id).state == "5-2 (W)"
    # pas de doublon au rafraîchissement suivant
    await entry.runtime_data.async_refresh()
    await hass.async_block_till_done()
    assert len(events) == 1
