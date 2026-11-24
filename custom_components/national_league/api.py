"""Accès à l'API du site nationalleague.ch."""
from __future__ import annotations

from typing import Any

from aiohttp import ClientError, ClientSession, ClientTimeout

from .const import API_BASE, API_LANG, VERSION


class NationalLeagueError(Exception):
    """Erreur de communication avec l'API."""


class NationalLeagueApi:
    def __init__(self, session: ClientSession) -> None:
        self._session = session

    async def _get(self, path: str) -> Any:
        try:
            async with self._session.get(
                f"{API_BASE}/{path}",
                params={"lang": API_LANG},
                headers={"User-Agent": f"HomeAssistant-NationalLeague/{VERSION} (usage personnel)"},
                timeout=ClientTimeout(total=20),
            ) as resp:
                resp.raise_for_status()
                data = await resp.json(content_type=None)
        except (ClientError, TimeoutError, ValueError) as err:
            raise NationalLeagueError(str(err)) from err
        if not isinstance(data, list):
            raise NationalLeagueError(f"Réponse inattendue pour {path}")
        return data

    async def teams(self) -> list[dict[str, Any]]:
        return await self._get("teams")

    async def team_games(self, team_id: str) -> list[dict[str, Any]]:
        return await self._get(f"games/team/{team_id}")
