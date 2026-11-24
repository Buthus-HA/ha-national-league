import json
from pathlib import Path

from custom_components.national_league import model

HERE = Path(__file__).parent
TEAMS = json.loads((HERE / "teams.json").read_text(encoding="utf-8"))
GAMES = json.loads((HERE / "games_team.json").read_text(encoding="utf-8"))
FRI = "103138"


def test_split_and_results():
    upcoming, results = model.split_games(GAMES, FRI)
    # matchs amicaux exclus
    assert all(not g["exhibition"] for g in upcoming + results)
    # 3 derniers résultats, du plus récent au plus ancien
    last3 = [(g["opponent"], g["score"], g["result"]) for g in results[:3]]
    assert last3 == [("HC Ajoie", "1-2", "L"), ("SC Rapperswil-Jona Lakers", "3-0", "W"), ("EHC Kloten", "2-4", "L")]
    # prochain match
    assert upcoming[0]["opponent"] == "ZSC Lions" and upcoming[0]["home"] is True
    assert upcoming[0]["date"] == "2026-11-24T18:45:00+00:00"
    assert upcoming[0]["opponent_logo"] == "https://www.nationalleague.ch/api/teams/101139/logo"


def test_overtime_and_shootout_labels():
    _, results = model.split_games(GAMES, FRI)
    by_opp_date = {(g["opponent"], g["date"][:10]): g for g in results}
    assert by_opp_date[("HC Davos", "2026-09-22")]["result"] == "SOW"      # 2-1 t.a.b. à Davos
    assert by_opp_date[("SC Bern", "2026-11-13")]["result"] == "SOL"       # 3-4 t.a.b.
    assert by_opp_date[("SCL Tigers", "2026-09-26")]["result"] == "OTW"    # 4-3 a.p.
    assert by_opp_date[("ZSC Lions", "2026-10-10")]["result"] == "OTL"     # 4-5 a.p.


def test_standings():
    table = model.standings(TEAMS)
    assert table[0]["name"] == "ZSC Lions" and table[0]["points"] == 55
    assert table[0]["logo"] == "https://www.nationalleague.ch/api/teams/101139/logo"
    fri = next(t for t in table if t["team_id"] == FRI)
    assert fri["rank"] == 8 and fri["points"] == 31 and fri["gp"] == 22
    # 5 derniers matchs, du plus ancien au plus récent (cohérent avec les résultats réels)
    assert fri["streak"] == ["L", "OL", "L", "W", "L"]
