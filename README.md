# National League (hockey) pour Home Assistant

Intégration **non officielle et à usage personnel** qui suit une équipe de National League
(hockey sur glace suisse) : prochains matchs, derniers résultats et classement.

> ⚠️ Elle lit l'API **interne** du site nationalleague.ch, qui n'est ni publique ni documentée
> et dont le `robots.txt` exclut les robots. Elle peut cesser de fonctionner à tout moment.
> Le rythme d'interrogation est volontairement modéré. Ce projet n'est pas affilié à la National League.

## Installation (manuelle)

```bash
cd /tmp && git clone --depth 1 <url-du-dépôt> nl
cp -r nl/custom_components/national_league /config/custom_components/
rm -rf nl && ha core restart
```
Puis **Paramètres → Appareils et services → Ajouter une intégration → National League** et choisir l'équipe.

## Entités (exemple pour Fribourg-Gottéron, HA en français)

| Entité | État | Attributs utiles |
|---|---|---|
| `sensor.fribourg_gotteron_prochain_match` | date/heure du prochain match | `opponent`, `home`, `arena`, `upcoming` (5 prochains) |
| `sensor.fribourg_gotteron_dernier_resultat` | `3-0 (W)` | `opponent`, `result`, `result_label`, `win`, `results` (5 derniers) |
| `sensor.fribourg_gotteron_classement` | rang | `points`, `games_played`, `goal_diff`, `streak`, `standings` (tableau complet) |

Chaque équipe a une URL de logo (`logo` dans `standings`, `opponent_logo` dans les matchs) pointant vers le site officiel ;
les logos sont des marques des clubs et ne sont pas inclus dans ce dépôt.

Codes de résultat : `W` victoire, `L` défaite, `OTW`/`OTL` en prolongation, `SOW`/`SOL` aux tirs au but.
Les matchs amicaux sont ignorés.

## Carte de classement

Livrée avec l'intégration (aucune ressource à ajouter) :

```yaml
type: custom:national-league-standings-card
entity: sensor.fribourg_gotteron_classement
# title: Classement        # "" pour masquer
# form: true               # colonne Forme (masquée sur petits écrans)
# zones:                   # découpage par défaut
#   - { label: Play-off, to: 6,  color: "#2e7d32" }
#   - { label: Play-in,  to: 10, color: "#ef6c00" }
#   - { label: Play-out, to: 14, color: "#c62828" }
```

## Événement

`national_league_game_finished` est émis quand un match de l'équipe se termine :
`opponent`, `home`, `score` (`buts pour-buts contre`), `result`, `result_label`, `win`, `date`, `id`.

## Rythme d'interrogation

2 requêtes par mise à jour : toutes les heures, toutes les 15 min le jour d'un match,
toutes les 3 min de 10 min avant le coup d'envoi à 3 h 30 après.
