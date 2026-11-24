"""Transformation des réponses de l'API (fonctions pures, testables sans HA)."""
from __future__ import annotations

from datetime import datetime
from typing import Any

FINISHED = "finished"
NOT_STARTED = "beforeStartOfPlay"


def parse_date(value: str) -> datetime:
    return datetime.fromisoformat(value)


def outcome(game: dict[str, Any], team_id: str) -> dict[str, Any]:
    """Résultat d'un match terminé vu depuis l'équipe suivie."""
    home = game["homeTeamId"] == team_id
    goals_for = game["homeTeamResult"] if home else game["awayTeamResult"]
    goals_against = game["awayTeamResult"] if home else game["homeTeamResult"]
    win = goals_for > goals_against
    if game.get("isShootout"):
        code, label = ("SOW", "Victoire aux tirs au but") if win else ("SOL", "Défaite aux tirs au but")
    elif game.get("isOvertime"):
        code, label = ("OTW", "Victoire en prolongation") if win else ("OTL", "Défaite en prolongation")
    else:
        code, label = ("W", "Victoire") if win else ("L", "Défaite")
    return {"win": win, "code": code, "label": label, "goals_for": goals_for, "goals_against": goals_against}


def game_view(game: dict[str, Any], team_id: str) -> dict[str, Any]:
    """Vue simplifiée d'un match pour l'équipe suivie."""
    home = game["homeTeamId"] == team_id
    view = {
        "id": game["gameId"],
        "date": game["date"],
        "home": home,
        "opponent": game["awayTeamName"] if home else game["homeTeamName"],
        "opponent_short": game["awayTeamShortName"] if home else game["homeTeamShortName"],
        "arena": game.get("arena"),
        "status": game.get("status"),
        "exhibition": bool(game.get("isExhibition")),
    }
    if game.get("status") == FINISHED:
        res = outcome(game, team_id)
        view |= {
            "result": res["code"],
            "result_label": res["label"],
            "win": res["win"],
            "score": f"{res['goals_for']}-{res['goals_against']}",
            "goals_for": res["goals_for"],
            "goals_against": res["goals_against"],
        }
    return view


def split_games(
    games: list[dict[str, Any]], team_id: str, *, include_exhibition: bool = False
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Retourne (à venir triés par date, terminés du plus récent au plus ancien)."""
    keep = [g for g in games if include_exhibition or not g.get("isExhibition")]
    upcoming = sorted((g for g in keep if g.get("status") != FINISHED), key=lambda g: g["date"])
    finished = sorted((g for g in keep if g.get("status") == FINISHED), key=lambda g: g["date"], reverse=True)
    return [game_view(g, team_id) for g in upcoming], [game_view(g, team_id) for g in finished]


def standings(teams: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Classement compact."""
    rows = []
    for t in sorted(teams, key=lambda t: t.get("rank", 99)):
        rows.append(
            {
                "rank": t.get("rank"),
                "team_id": str(t.get("teamId")),
                "name": t.get("name"),
                "short": t.get("shortName"),
                "gp": t.get("gp"),
                "points": t.get("po"),
                "goals_for": t.get("g"),
                "goals_against": t.get("ga"),
                "goal_diff": t.get("go"),
                # l'API liste la série du plus ancien au plus récent : on garde les 5 derniers
                "streak": list(t.get("streak") or [])[-5:],
            }
        )
    return rows
