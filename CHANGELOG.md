# Changelog

## 0.3.0 — 2026-11-24
- Carte `custom:national-league-standings-card` : classement avec zones Play-off / Play-in / Play-out en colonne colorée (texte vertical), logos, équipe suivie mise en évidence, forme.
- Capteur de classement : attribut `team_id`.

## 0.2.0 — 2026-11-24
- Logos des équipes (référencés depuis le site officiel) : attributs `logo` / `opponent_logo` et image des capteurs.

## 0.1.0 — 2026-11-23
- Version initiale : prochain match, 5 prochains matchs, derniers résultats, classement complet.
- Événement `national_league_game_finished` à la fin de chaque match de l'équipe suivie.
- Interrogation adaptative : 1 h en temps normal, 15 min le jour de match, 3 min pendant le match.
