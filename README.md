Friends of Progress: directory page of UK progress/growth/abundance orgs. Companion to luma.com/progressevents.
Live: https://nazzacode.github.io/friends-of-progress/ (GitHub Pages, repo nazzacode/friends-of-progress, `main` /). Old artifact DvzEMKFGadyxYnv5uNuqu6 = superseded.

- `orgs.json` — the list. One object per org: `name`, `url`, `lean` (left/right/nonpartisan, label on card), `group` (Movements & community / Ideas & policy / Science & culture), `blurb` (own words), `tags`; optional `luma` (calendar api_id → Luma avatar, cover, "Events on Luma" link), `image` / `avatar` (override URLs), `fit: "contain"` (logo that crops badly).
- `build.py` — per org: og meta; hero = image > og:image > Luma cover > homepage screenshot (Luma-only orgs: cover > avatar, Luma og = generic card) (headless Chrome, cached); avatar = Luma avatar > apple-touch-icon > favicon. Shrinks big images (ImageMagick), prunes unused, renders `template.html` → `index.html`.
- Tags understood by the filter bar (others still show on cards): topic housing/energy/science/cities/economy/infrastructure/state capacity/culture; kind think tank/campaign/community/publication/funder/runs events.

Add an org: append a line to `orgs.json` → `python3 build.py` → `git commit -am … && git push` (Pages redeploys ~30s).
`share.jpg` = OG preview (1200×630 Chrome screenshot of index.html); regenerate by hand if the top changes.
Local preview: `python3 -m http.server -d directory` (launch.json `directory`).

**Inclusion rule = progress-pilled** (Nathan, 2026-11-23): building/growth/science/tech is THE main thing. Lean irrelevant; generic left/right/civic/wonk ≠ enough. Vibe > checklist. Cut: Fabian, Compass, IPPR, Demos, Renewal, Labour Together, Progressive Britain, SMF, London Society, TBI, Roots of Progress (US). Kept on purpose: IEA, Resolution Foundation, Common Wealth.
