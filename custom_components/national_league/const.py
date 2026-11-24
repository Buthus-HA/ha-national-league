"""Constantes de l'intégration National League."""
from __future__ import annotations

import json
from datetime import timedelta
from pathlib import Path

DOMAIN = "national_league"
VERSION: str = json.loads((Path(__file__).parent / "manifest.json").read_text(encoding="utf-8"))["version"]

API_BASE = "https://www.nationalleague.ch/api"
API_LANG = "de-CH"
# Logos hébergés par le site officiel (référencés, jamais copiés dans le dépôt)
CARD_URL = "/national_league/national-league-card.js"
LOGO_URL = API_BASE + "/teams/{team_id}/logo"

CONF_TEAM_ID = "team_id"
CONF_TEAM_NAME = "team_name"

# Rythme volontairement modéré : API interne du site, à ménager.
INTERVAL_IDLE = timedelta(hours=1)      # hors jours de match
INTERVAL_MATCHDAY = timedelta(minutes=15)  # le jour d'un match, avant le coup d'envoi
INTERVAL_LIVE = timedelta(minutes=3)    # pendant la fenêtre du match
LIVE_WINDOW_BEFORE = timedelta(minutes=10)
LIVE_WINDOW_AFTER = timedelta(hours=3, minutes=30)

UPCOMING_COUNT = 5
RESULTS_COUNT = 5

EVENT_GAME_FINISHED = "national_league_game_finished"
ATTRIBUTION = "Données : nationalleague.ch"
