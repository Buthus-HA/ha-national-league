/* National League – carte de classement (livrée avec l'intégration national_league).
 * type: custom:national-league-standings-card
 * entity: sensor.<équipe>_classement   (obligatoire)
 * title: "Classement"                  (optionnel, "" pour masquer)
 * form: true                           (optionnel, affiche la colonne Forme)
 * zones:                               (optionnel, découpage du classement)
 *   - { label: Play-off, to: 6,  color: "#2e7d32" }
 *   - { label: Play-in,  to: 10, color: "#ef6c00" }
 *   - { label: Play-out, to: 14, color: "#c62828" }
 */
const NL_DEFAULT_ZONES = [
  { label: "Play-off", to: 6, color: "#2e7d32" },
  { label: "Play-in", to: 10, color: "#ef6c00" },
  { label: "Play-out", to: 99, color: "#c62828" },
];
const NL_FORM = { W: ["g", "V"], OW: ["g", "Vp"], L: ["r", "D"], OL: ["o", "Dp"] };

class NationalLeagueStandingsCard extends HTMLElement {
  setConfig(config) {
    if (!config || !config.entity) throw new Error("Indique l'entité de classement (entity: sensor.…_classement)");
    this._config = { title: "Classement National League", form: true, zones: NL_DEFAULT_ZONES, ...config };
    if (!this.shadowRoot) this.attachShadow({ mode: "open" });
    this._sig = null;
  }

  set hass(hass) {
    const st = hass.states[this._config.entity];
    const sig = st ? st.last_updated : "none";
    if (sig === this._sig) return;
    this._sig = sig;
    this._render(st);
  }

  getCardSize() { return 8; }
  getGridOptions() { return { columns: 12, min_columns: 6 }; }
  static getStubConfig(hass) {
    const e = Object.keys(hass.states).find((id) => id.startsWith("sensor.") && hass.states[id].attributes.standings);
    return { entity: e || "sensor.fribourg_gotteron_classement" };
  }

  _render(st) {
    const c = this._config;
    const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch]));
    if (!st) {
      this.shadowRoot.innerHTML = `<ha-card><div class="msg">Entité introuvable : ${esc(c.entity)}</div></ha-card>`;
      return;
    }
    const rows = st.attributes.standings || [];
    const me = String(st.attributes.team_id ?? "");
    // découpage en zones
    const zones = [];
    let from = 1;
    for (const z of c.zones) {
      const members = rows.filter((r) => r.rank >= from && r.rank <= z.to);
      if (members.length) zones.push({ ...z, members });
      from = z.to + 1;
    }
    const body = zones.map((z) => z.members.map((r, i) => {
      const mine = String(r.team_id) === me;
      const zoneCell = i === 0
        ? `<td class="zone" rowspan="${z.members.length}" style="--zc:${esc(z.color)}"><span>${esc(z.label)}</span></td>`
        : "";
      const form = c.form ? `<td class="form">${(r.streak || []).map((s) => {
        const [cls, txt] = NL_FORM[s] || ["n", s];
        return `<i class="${cls}" title="${esc(txt)}"></i>`;
      }).join("")}</td>` : "";
      const diff = r.goal_diff > 0 ? `+${r.goal_diff}` : `${r.goal_diff}`;
      return `<tr class="${mine ? "me" : ""}${i === 0 ? " first" : ""}">${zoneCell}
        <td class="rk">${r.rank}</td>
        <td class="logo">${r.logo ? `<img src="${esc(r.logo)}" alt="" loading="lazy">` : ""}</td>
        <td class="team">${esc(r.name)}</td>
        <td class="num">${r.gp}</td>
        <td class="num pts">${r.points}</td>
        <td class="num">${diff}</td>${form}</tr>`;
    }).join("")).join("");

    this.shadowRoot.innerHTML = `
      <ha-card>
        ${c.title ? `<h1 class="title">${esc(c.title)}</h1>` : ""}
        <table>
          <thead><tr><th></th><th>#</th><th></th><th class="team">Équipe</th>
            <th class="num" title="Matchs joués">MJ</th><th class="num">Pts</th><th class="num">Diff</th>
            ${c.form ? `<th class="form" title="5 derniers matchs, du plus ancien au plus récent">Forme</th>` : ""}</tr></thead>
          <tbody>${body}</tbody>
        </table>
        <div class="foot">Données : nationalleague.ch</div>
      </ha-card>
      <style>
        ha-card { padding: 0 0 8px; overflow: hidden; }
        .title { font-size: 1.2em; font-weight: 500; margin: 0; padding: 14px 16px 6px; }
        table { width: 100%; border-collapse: collapse; font-size: 14px; }
        th { font-weight: 500; color: var(--secondary-text-color); font-size: 12px; padding: 6px 6px; text-align: left; }
        td { padding: 5px 6px; border-top: 1px solid var(--divider-color); }
        tr.first td { border-top: 2px solid var(--divider-color); }
        .num { text-align: right; font-variant-numeric: tabular-nums; }
        .rk { text-align: right; width: 1.6em; color: var(--secondary-text-color); }
        .pts { font-weight: 600; }
        .logo { width: 26px; padding: 2px 4px; }
        .logo img { width: 24px; height: 24px; object-fit: contain; display: block; }
        .team { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 0; width: 100%; }
        .zone { width: 22px; padding: 0; background: var(--zc); border-top: 2px solid var(--card-background-color, #fff); }
        .zone span { writing-mode: vertical-rl; transform: rotate(180deg); display: block; margin: auto;
          color: #fff; font-size: 11px; font-weight: 600; letter-spacing: .06em; text-transform: uppercase;
          white-space: nowrap; padding: 6px 0; text-align: center; }
        tr.me td:not(.zone) { background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.12); font-weight: 600; }
        tr.me .rk { color: var(--primary-text-color); }
        .form { white-space: nowrap; text-align: center; }
        .form i { display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin: 0 1.5px; vertical-align: middle; }
        .form i.g { background: #43a047; } .form i.r { background: #e53935; }
        .form i.o { background: #fb8c00; } .form i.n { background: #9e9e9e; }
        .foot { font-size: 11px; color: var(--secondary-text-color); padding: 6px 16px 0; text-align: right; }
        .msg { padding: 16px; color: var(--error-color); }
        @media (max-width: 420px) { th.form, td.form { display: none; } }
      </style>`;
  }
}

if (!customElements.get("national-league-standings-card")) {
  customElements.define("national-league-standings-card", NationalLeagueStandingsCard);
}
window.customCards = window.customCards || [];
if (!window.customCards.some((c) => c.type === "national-league-standings-card")) {
  window.customCards.push({
    type: "national-league-standings-card",
    name: "National League – classement",
    description: "Classement avec zones Play-off / Play-in / Play-out, logos et forme.",
    preview: true,
  });
}
