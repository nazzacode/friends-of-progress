Friends of Progress: directory page of UK progress/growth/abundance orgs. Companion to luma.com/progressevents.
Artifact (private): https://claude.ai/artifact/DvzEMKFGadyxYnv5uNuqu6

- `orgs.json` — the list. One object per org: `name`, `url`, `lean` (left/right/nonpartisan, label on card), `group` (Movements & community / Ideas & policy / Science & culture), `blurb` (own words), `tags`; optional `luma` (calendar api_id → Luma avatar, cover, "Events on Luma" link), `image` / `avatar` (override URLs), `fit: "contain"` (logo that crops badly).
- `build.py` — per org: og meta; hero = image > og:image > Luma cover > homepage screenshot (headless Chrome, cached); avatar = Luma avatar > apple-touch-icon > favicon. Shrinks big images (ImageMagick), prunes unused, renders `template.html` → `index.html`.
- Tags understood by the filter bar (others still show on cards): topic housing/energy/science/cities/economy/infrastructure/state capacity/culture; kind think tank/campaign/community/publication/funder/runs events.

Add an org: append a line to `orgs.json` → `python3 build.py` → republish `index.html` with `img/*` as files.
Local preview: `python3 -m http.server -d directory` (launch.json `directory`).
