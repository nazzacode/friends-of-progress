#!/usr/bin/env python3
"""Rebuild the directory: orgs.json → fetch og meta + hero image → index.html.

Add an org = one line in orgs.json, then `python3 build.py`.
Keys: name, url, lean (left/right/nonpartisan), group, blurb (own words), tags.
Optional: luma (calendar api_id → avatar, cover, events link), image / avatar (override URLs),
fit: "contain" (logo images that crop badly).
Hero = image > og:image > Luma cover > homepage screenshot (headless Chrome, cached; delete to refresh).
Avatar = avatar > Luma avatar > apple-touch-icon > favicon.
"""
import json, re, sys, html, shutil, subprocess, urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

D = Path(__file__).parent
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) progress-directory/0.1"}
IMG = D / "img"


class Meta(HTMLParser):
    def __init__(s):
        super().__init__(); s.m, s.title, s._t = {}, "", False
    def handle_starttag(s, tag, a):
        a = dict(a)
        if tag == "meta":
            k = (a.get("property") or a.get("name") or "").lower()
            if k and a.get("content") and k not in s.m: s.m[k] = a["content"]
        elif tag == "link" and "icon" in (rel := (a.get("rel") or "").lower()):
            k = "apple" if "apple-touch-icon" in rel else "icon"
            if k not in s.m: s.m[k] = a.get("href", "")
        s._t = tag == "title"
    def handle_data(s, d):
        if s._t and not s.title: s.title = d.strip()
    def handle_endtag(s, tag): s._t = False


get = lambda url, t=20: urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=t)


def meta(url):
    try:
        with get(url) as r:
            p = Meta(); p.feed(r.read(600_000).decode("utf-8", "replace")); final = r.url
    except Exception as e:
        print(f"  ! {url}: {e}", file=sys.stderr); return {}
    img = p.m.get("og:image") or p.m.get("twitter:image") or p.m.get("twitter:image:src")
    icon = p.m.get("apple") or p.m.get("icon") or "/favicon.ico"
    return {"title": html.unescape(p.m.get("og:title") or p.title),
            "description": html.unescape(p.m.get("og:description") or p.m.get("description", "")),
            "image": urljoin(final, img) if img else None, "icon": urljoin(final, icon)}


def luma(api_id):
    try:
        with get(f"https://api.lu.ma/calendar/get?api_id={api_id}") as r:
            c = json.load(r).get("calendar", {})
    except Exception as e:
        print(f"  ! luma {api_id}: {e}", file=sys.stderr); return {}
    return {"avatar": c.get("avatar_url"), "cover": c.get("cover_image_url"),
            "url": f"https://luma.com/{c['slug']}" if c.get("slug") else None}


def screenshot(url, slug):
    """Homepage screenshot as last-resort hero. Cached: delete img/<slug>.jpg to refresh."""
    if (hit := cached(slug)): return hit
    chrome = shutil.which("google-chrome") or shutil.which("chromium")
    if not (chrome and shutil.which("magick")): return None
    raw = IMG / f"{slug}.shot.png"
    try:  # tall window, keep the top 1200x630: drops bottom-fixed cookie banners
        subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1200,900",
                        "--virtual-time-budget=8000", f"--screenshot={raw}", url], capture_output=True, timeout=90)
        subprocess.run(["magick", str(raw), "-crop", "1200x630+0+0", "-quality", "85", str(IMG / f"{slug}.jpg")], check=True)
    except Exception as e:
        print(f"  ! shot {url}: {e}", file=sys.stderr); return None
    finally:
        raw.unlink(missing_ok=True)
    return f"img/{slug}.jpg"


EXT = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp", "image/gif": ".gif", "image/svg+xml": ".svg",
       "image/x-icon": ".ico", "image/vnd.microsoft.icon": ".ico"}


def download(src, slug):
    try:
        with get(src) as r:
            ext = EXT.get(r.headers.get_content_type())
            if not ext: return None
            data = r.read(8_000_000)
    except Exception as e:
        print(f"  ! img {src}: {e}", file=sys.stderr); return None
    IMG.mkdir(exist_ok=True)
    for old in IMG.glob(slug + ".*"): old.unlink()
    f = IMG / f"{slug}{ext}"; f.write_bytes(data)
    if ext not in (".svg", ".ico") and shutil.which("magick") and \
            subprocess.run(["magick", "-regard-warnings", str(f), "null:"], capture_output=True).returncode:
        print(f"  ! broken image {src}", file=sys.stderr); f.unlink(); return None
    return f"img/{slug}{ext}"


slugify = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def cached(slug):
    old = sorted(IMG.glob(slug + ".*"))
    return f"img/{old[0].name}" if old else None


def shrink(rel, box):
    """Resize big raster images in place (needs ImageMagick); keeps the page light."""
    p = D / rel
    if not shutil.which("magick") or p.suffix in (".svg", ".ico", ".gif") or p.stat().st_size < 120_000: return rel
    out = p.with_suffix(".jpg") if p.suffix == ".png" and p.stat().st_size > 300_000 else p
    flat = ["-background", "white", "-flatten"] if out.suffix == ".jpg" and p.suffix != ".jpg" else []
    subprocess.run(["magick", str(p), *flat, "-resize", f"{box}>", "-strip", "-quality", "82", str(out)], check=False)
    if out == p: return rel
    if not out.exists(): return rel  # conversion failed → keep original
    p.unlink(); return f"img/{out.name}"


def fetch_img(src, slug, box="1200x1200"):  # fetch failure → keep last good image
    got = (download(src, slug) if src else None) or cached(slug)
    return shrink(got, box) if got else None


def build(org):
    print("·", org["name"])
    slug, m = slugify(org["name"]), meta(org["url"])
    lu = luma(org["luma"]) if org.get("luma") else {}
    on_luma = "luma.com/" in org["url"]  # Luma's own og:image is a generic share card → prefer the cover
    heroes = (org.get("image"), lu.get("cover"), m.get("image")) if on_luma else (org.get("image"), m.get("image"), lu.get("cover"))
    hero = next(filter(None, (fetch_img(u, slug) for u in heroes if u)), None) \
        or screenshot(org["url"], slug)
    avatar = fetch_img(org.get("avatar") or lu.get("avatar") or m.get("icon"), slug + "-icon", "128x128")
    return {**org, "slug": slug, "og": m, "img": hero, "avatar": avatar, "luma_url": lu.get("url")}


def prune(built):
    keep = {o["img"] for o in built} | {o["avatar"] for o in built}
    for f in IMG.glob("*"):
        if f"img/{f.name}" not in keep: print("  - pruned", f.name); f.unlink()


def main():
    orgs = json.loads((D / "orgs.json").read_text())
    built = [build(o) for o in orgs]
    prune(built)
    (D / "orgs.built.json").write_text(json.dumps(built, indent=1, ensure_ascii=False))
    page = (D / "template.html").read_text().replace(
        "/*DATA*/[]", json.dumps(built, ensure_ascii=False).replace("</", "<\\/"))
    (D / "index.html").write_text(page)
    miss = [o["name"] for o in built if not o["img"]]
    print(f"{len(built)} orgs → index.html" + (f"; no image: {', '.join(miss)}" if miss else ""))


if __name__ == "__main__":
    main()
