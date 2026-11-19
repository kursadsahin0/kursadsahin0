#!/usr/bin/env python3
"""Render the profile README cards (animated SVG) into cards/.

Reads data/contributions.json, data/profile.json and data/portrait.txt.
No dependencies. STATIC=1 renders every card at its final frame.
Edit PROFILE below to change the text, tiles, featured repos or stack.
"""
import base64
import calendar
import datetime as dt
import json
import os
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA, FONTS, OUT = ROOT / "data", ROOT / "fonts", ROOT / "cards"
STATIC = os.environ.get("STATIC") == "1"

PAPER, INK, RED, GREEN = "#FDFDFF", "#0E0E10", "#F42902", "#83FD80"
MUTED, LINE, SOFT = "#5F5F6B", "#E6E6EC", "#F3F3F6"
HEAT = ["#EEEEF2", "#FFD6CC", "#FF9C84", "#FA5B35", "#F42902"]

PROFILE = {
    "first": "Kürşat",
    "last": "Şahin",
    "now": "Currently Frontend Developer at Sinyatek",
    "role": "Frontend Developer",
    "about": ["crafting fast, accessible and user-focused",
              "web interfaces with React, Next.js, Vue.js & Quasar."],
    "location": "Trabzon, Türkiye",
    "live_apps": 6,
    "repos": [
        ("menümGo", "QR code digital menu for cafes and restaurants, TR/EN, allergens and stock.",
         ["Vue", "Quasar", "Fastify", "Prisma"]),
        ("KPSS Haritası", "Free KPSS exam prep app with a topic map, quizzes and progress tracking.",
         ["Vue", "Quasar", "Pinia"]),
        ("CryptoPulse", "Real-time crypto analytics with a watchlist and portfolio tracking.",
         ["Vue", "Quasar", "Pinia"]),
        ("CodeDNA", "Maps a repository's dependencies, architecture and change impact.",
         ["Next.js", "TypeScript", "Tailwind"]),
        ("ParkKasa", "Parking cash desk, subscriptions and end-of-day management panel.",
         ["Vue", "Quasar", "Supabase"]),
        ("Yeşil Bakery", "One-page site for a croissant bakery in Trabzon with reviews and a map.",
         ["Vue", "Vite"]),
    ],
    "stack": [
        ("TypeScript", "#3178C6"), ("JavaScript", "#F7DF1E"), ("Vue.js", "#42B883"),
        ("Quasar", "#16B7FB"), ("Pinia", "#FFD859"), ("React", "#61DAFB"),
        ("Next.js", "#0E0E10"), ("Redux", "#764ABC"), ("HTML5", "#E34F26"),
        ("CSS3", "#1572B6"), ("Sass", "#CC6699"), ("Tailwind", "#38BDF8"),
        ("Bootstrap", "#7952B3"), ("Vite", "#646CFF"), ("Supabase", "#3ECF8E"),
        ("Firebase", "#FFCA28"), ("GSAP", "#88CE02"), ("Git", "#F05032"),
        ("Vercel", "#0E0E10"), ("Jira", "#0052CC"),
    ],
}

# ---------------------------------------------------------------- text helpers
METRICS = json.loads((FONTS / "metrics.json").read_text())


def width(text, font, size):
    m = METRICS[font]
    return sum(m["w"].get(c, m["upm"] * 0.55) for c in text) * size / m["upm"]


def wrap(text, font, size, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if cur and width(trial, font, size) > max_w:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    return lines + [cur] if cur else lines


def e(s):
    return escape(str(s), quote=True)


def font_face(*names):
    fams = {"display-800": ("Display", 800), "display-700": ("Display", 700),
            "inter-400": ("Inter", 400), "inter-600": ("Inter", 600), "mono-500": ("Mono", 500)}
    out = []
    for n in names:
        fam, w = fams[n]
        b64 = base64.b64encode((FONTS / f"{n}.woff").read_bytes()).decode()
        out.append(f"@font-face{{font-family:'{fam}';font-weight:{w};"
                   f"src:url(data:font/woff;base64,{b64}) format('woff')}}")
    return "".join(out)


BASE_CSS = f"""
.d8{{font-family:'Display',sans-serif;font-weight:800}}
.d7{{font-family:'Display',sans-serif;font-weight:700}}
.i4{{font-family:'Inter',sans-serif;font-weight:400}}
.i6{{font-family:'Inter',sans-serif;font-weight:600}}
.mo{{font-family:'Mono',monospace;font-weight:500}}
@keyframes rise{{from{{opacity:0;transform:translateY(26px)}}to{{opacity:1;transform:none}}}}
@keyframes fade{{from{{opacity:0}}to{{opacity:1}}}}
@keyframes pop{{0%{{opacity:0;transform:scale(.2)}}70%{{opacity:1;transform:scale(1.15)}}100%{{opacity:1;transform:scale(1)}}}}
@keyframes grow{{from{{transform:scaleY(0)}}to{{transform:scaleY(1)}}}}
@keyframes wipe{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
@keyframes flash{{0%,100%{{opacity:1}}}}
@keyframes pulse{{0%{{opacity:.7;transform:scale(1)}}100%{{opacity:0;transform:scale(3)}}}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
@keyframes nudge{{0%,80%,100%{{transform:none}}88%{{transform:translate(3px,-3px)}}}}
@keyframes shine{{0%{{transform:translateX(-140%)}}35%,100%{{transform:translateX(140%)}}}}
@keyframes swing{{0%{{opacity:0;transform:translateY(60px) rotate(-6deg)}}60%{{opacity:1;transform:translateY(-6px) rotate(1.5deg)}}100%{{opacity:1;transform:none}}}}
.a{{animation-fill-mode:both;animation-timing-function:cubic-bezier(.2,.7,.2,1)}}
.tb{{transform-box:fill-box}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
"""
if STATIC:
    BASE_CSS += "*{animation:none!important}"


def svg(w, h, body, fonts, extra_css="", title=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{e(title)}"><title>{e(title)}</title>'
            f'<style>{font_face(*fonts)}{BASE_CSS}{extra_css}</style>{body}</svg>\n')


def anim(name, delay, dur=0.7, extra=""):
    return f'class="a tb {extra}" style="animation-name:{name};animation-duration:{dur}s;animation-delay:{delay:.3f}s"'


def card(w, h, fill=PAPER, stroke=LINE, r=26):
    return f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'


def counter(value, x, y, cls, size, fill, delay, anchor="start", frames=18, dur=0.9):
    """Count up from 0 with CSS: one text per frame, each flashed briefly; the final value stays."""
    parts, step = [], dur / frames
    for i in range(1, frames):
        v = round(value * (1 - (1 - i / frames) ** 3))
        parts.append(f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
                     f'opacity="0" style="animation:flash {step:.3f}s linear {delay + i * step:.3f}s">{v}</text>')
    parts.append(f'<text x="{x}" y="{y}" class="{cls} a" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
                 f'style="animation-name:fade;animation-duration:.01s;animation-delay:{delay + dur:.3f}s">{value}</text>')
    return "".join(parts)


# ------------------------------------------------------------------- the data
DAYS = json.loads((DATA / "contributions.json").read_text())
PROF = json.loads((DATA / "profile.json").read_text())
PORTRAIT = (DATA / "portrait.txt").read_text().rstrip("\n").split("\n")


def stats():
    total = sum(d["count"] for d in DAYS)
    active = sum(1 for d in DAYS if d["count"])
    longest = run = 0
    for d in DAYS:
        run = run + 1 if d["count"] else 0
        longest = max(longest, run)
    current = 0
    for i, d in enumerate(reversed(DAYS)):
        if d["count"]:
            current += 1
        elif i > 0:  # today without commits doesn't break the streak yet
            break
    best = max(DAYS, key=lambda d: d["count"])
    return dict(total=total, active=active, longest=longest, current=current, best=best)


def months():
    last = dt.date.fromisoformat(DAYS[-1]["date"])
    keys = []
    y, m = last.year, last.month
    for _ in range(12):
        keys.append((y, m))
        y, m = (y, m - 1) if m > 1 else (y - 1, 12)
    keys.reverse()
    totals = {k: 0 for k in keys}
    for d in DAYS:
        k = (int(d["date"][:4]), int(d["date"][5:7]))
        if k in totals:
            totals[k] += d["count"]
    return [(calendar.month_abbr[m], y, totals[(y, m)]) for y, m in keys]


# ------------------------------------------------------------------- the cards
def hero():
    W, H = 840, 400
    p = PROFILE
    b = [card(W, H)]
    # "now" pill with a pulsing dot
    pw = width(p["now"], "inter-600", 13) + 46
    b.append(f'<g {anim("fade", .05, .6)}><rect x="40" y="40" width="{pw:.0f}" height="32" rx="16" fill="{SOFT}" stroke="{LINE}"/>'
             f'<circle cx="60" cy="56" r="4.5" fill="#22C55E"/>'
             f'<circle cx="60" cy="56" r="4.5" fill="#22C55E" class="a tb" style="transform-origin:center;'
             f'animation:pulse 1.8s ease-out 1s infinite"/>'
             f'<text x="74" y="60.5" class="i6" font-size="13" fill="{INK}">{e(p["now"])}</text></g>')
    # name, line by line
    size = 92
    b.append(f'<g {anim("rise", .15, .8)}><text x="36" y="168" class="d8" font-size="{size}" fill="{INK}" '
             f'letter-spacing="-3">{e(p["first"])}</text></g>')
    lw = width(p["last"], "display-800", size) - 3 * len(p["last"])
    b.append('<defs><linearGradient id="sh" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
             '<stop offset=".5" stop-color="#fff" stop-opacity=".75"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>'
             f'</linearGradient><clipPath id="lastclip"><text x="36" y="252" class="d8" font-size="{size}" '
             f'letter-spacing="-3">{e(p["last"])}</text></clipPath></defs>')
    b.append(f'<g {anim("rise", .3, .8)}><text x="36" y="252" class="d8" font-size="{size}" fill="{INK}" '
             f'letter-spacing="-3">{e(p["last"])}</text>'
             f'<g clip-path="url(#lastclip)"><rect x="36" y="170" width="{lw:.0f}" height="100" fill="url(#sh)" '
             f'class="a tb" style="transform:translateX(-200%);animation:shine 4.5s ease-in-out 2s infinite"/></g>'
             f'<circle cx="{36 + lw + 14:.0f}" cy="240" r="11" fill="{RED}" class="a tb" '
             f'style="transform-origin:center;animation:pop .6s cubic-bezier(.3,1.6,.5,1) 1.05s both"/></g>')
    # role with a green marker highlight, then the rest of the sentence wrapped beside the portrait
    rw = width(p["role"], "inter-600", 17)
    lines = wrap(p["role"] + " " + " ".join(p["about"]), "inter-400", 17, 440)
    first_rest = lines[0][len(p["role"]):]
    b.append(f'<rect x="38" y="288" width="{rw + 4:.0f}" height="10" fill="{GREEN}" '
             f'class="a tb" style="transform-origin:left;animation:wipe .6s cubic-bezier(.2,.7,.2,1) 1.1s both"/>')
    t = [f'<text x="40" y="297" class="i6" font-size="17" fill="{INK}">{e(p["role"])}'
         f'<tspan class="i4" fill="{MUTED}">{e(first_rest)}</tspan></text>']
    for j, line in enumerate(lines[1:3]):
        t.append(f'<text x="40" y="{321 + j * 24}" class="i4" font-size="17" fill="{MUTED}">{e(line)}</text>')
    b.append(f'<g {anim("fade", .7, .7)}>{"".join(t)}</g>')
    b.append(f'<g {anim("fade", .95, .7)}><text x="40" y="{321 + len(lines[1:3]) * 24 + 16}" class="mo" font-size="12.5" '
             f'fill="{MUTED}" letter-spacing=".5">↗ {e(p["location"].upper())}  ·  {PROF["public_repos"]} REPOS  ·  '
             f'{PROF["followers"]} FOLLOWERS</text></g>')
    # portrait: a red arch with the ASCII portrait printing in row by row
    ax, ay, aw, ah = 520, 40, 280, 320
    arch = (f'M{ax},{ay + ah} V{ay + aw / 2} A{aw / 2},{aw / 2} 0 0 1 {ax + aw},{ay + aw / 2} V{ay + ah - 22} '
            f'Q{ax + aw},{ay + ah} {ax + aw - 22},{ay + ah} Z')
    b.append(f'<defs><clipPath id="arch"><path d="{arch}"/></clipPath></defs>')
    b.append(f'<g {anim("rise", .2, .9)}><path d="{arch}" fill="{RED}"/><g clip-path="url(#arch)">')
    cols = max(len(r) for r in PORTRAIT)
    cw = (aw + 10) / cols
    fs = cw / 0.6
    lh = fs * 1.16
    top = ay + ah - len(PORTRAIT) * lh + 2
    for i, row in enumerate(PORTRAIT):
        if row.strip():
            b.append(f'<text x="{ax - 5}" y="{top + (i + 1) * lh:.1f}" font-size="{fs:.2f}" fill="{INK}" '
                     f'xml:space="preserve" opacity=".92" class="mo a" '
                     f'style="animation:fade .25s linear {.6 + i * .035:.3f}s both">{e(row)}</text>')
    b.append('</g></g>')
    # spinning "open to work" badge
    cx, cy, r = 506, 92, 44
    b.append(f'<g class="a" style="transform-origin:{cx}px {cy}px;animation:pop .6s cubic-bezier(.3,1.6,.5,1) 1.4s both">'
             f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{GREEN}" stroke="{INK}" stroke-width="1.5"/>'
             f'<defs><path id="ring" d="M{cx - 31},{cy} a31,31 0 1,1 62,0 a31,31 0 1,1 -62,0"/></defs>'
             f'<g class="a" style="transform-origin:{cx}px {cy}px;animation:spin 14s linear infinite">'
             f'<text class="mo" font-size="10.5" fill="{INK}"><textPath href="#ring" textLength="190" lengthAdjust="spacing">'
             f'OPEN TO WORK • OPEN TO WORK •</textPath></text></g>'
             f'<text x="{cx}" y="{cy + 7}" text-anchor="middle" class="d8" font-size="20" fill="{INK}">↗</text></g>')
    return svg(W, H, "".join(b), ["display-800", "inter-400", "inter-600", "mono-500"],
               title=f'{p["first"]} {p["last"]}, {p["role"]}')


def graph():
    W, H = 840, 210
    weeks, cur = [], []
    first = dt.date.fromisoformat(DAYS[0]["date"])
    pad = (first.weekday() + 1) % 7  # GitHub weeks start on Sunday
    cur = [None] * pad
    for d in DAYS:
        cur.append(d)
        if len(cur) == 7:
            weeks.append(cur)
            cur = []
    if cur:
        weeks.append(cur + [None] * (7 - len(cur)))
    weeks = weeks[-53:]
    cell, gap = 12, 2.85
    x0, y0 = 40, 78
    total = sum(d["count"] for d in DAYS)
    b = [card(W, H)]
    b.append(f'<g {anim("fade", .05, .5)}><text x="40" y="46" class="d7" font-size="20" fill="{INK}">Contributions</text>'
             f'<text x="{W - 40}" y="46" text-anchor="end" class="mo" font-size="12" fill="{MUTED}">'
             f'{total} IN THE LAST YEAR</text></g>')
    last_month = None
    for wi, wk in enumerate(weeks):
        x = x0 + wi * (cell + gap)
        for di, d in enumerate(wk):
            if not d:
                continue
            m = d["date"][5:7]
            if di == 0 and m != last_month and wi < len(weeks) - 2:
                last_month = m
                b.append(f'<g {anim("fade", .1 + wi * .012, .3)}><text x="{x}" y="{y0 - 10}" class="mo" font-size="10" '
                         f'fill="{MUTED}">{calendar.month_abbr[int(m)].upper()}</text></g>')
            y = y0 + di * (cell + gap)
            b.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell}" height="{cell}" rx="3" fill="{HEAT[d["level"]]}" '
                     f'style="transform-origin:center;animation:pop .35s ease-out {.15 + wi * .018 + di * .01:.3f}s both" class="a tb">'
                     f'<title>{d["count"]} on {d["date"]}</title></rect>')
    lx = W - 40 - 5 * 15 - 70
    b.append(f'<g {anim("fade", 1.2, .5)}><text x="{lx}" y="{H - 14}" class="mo" font-size="10" fill="{MUTED}">LESS</text>')
    for i, c in enumerate(HEAT):
        b.append(f'<rect x="{lx + 36 + i * 15}" y="{H - 24}" width="11" height="11" rx="2.5" fill="{c}"/>')
    b.append(f'<text x="{lx + 36 + 5 * 15 + 3}" y="{H - 14}" class="mo" font-size="10" fill="{MUTED}">MORE</text></g>')
    return svg(W, H, "".join(b), ["display-700", "mono-500"], title=f"{total} contributions in the last year")


def activity():
    W, H = 840, 300
    s, ms = stats(), months()
    b = [card(W, H)]
    b.append(f'<g {anim("fade", .05, .5)}><text x="40" y="52" class="d7" font-size="20" fill="{INK}">Monthly activity</text></g>')
    rows = [("TOTAL", s["total"], "contributions"), ("CURRENT STREAK", s["current"], "days"),
            ("LONGEST STREAK", s["longest"], "days"), ("ACTIVE DAYS", s["active"], "of the last 365")]
    for i, (k, v, u) in enumerate(rows):
        y = 100 + i * 46
        b.append(f'<g {anim("rise", .15 + i * .1, .6)}><text x="40" y="{y}" class="mo" font-size="10.5" fill="{MUTED}" '
                 f'letter-spacing=".6">{k}</text></g>')
        b.append(counter(v, 40, y + 28, "d8", 28, RED if i == 0 else INK, .25 + i * .1, dur=.8))
        b.append(f'<g {anim("fade", 1.1 + i * .1, .4)}><text x="{40 + width(str(v), "display-800", 28) + 8:.0f}" y="{y + 27}" '
                 f'class="i4" font-size="13" fill="{MUTED}">{u}</text></g>')
    # bars
    bx, by, bw, bh = 300, 96, 500, 150
    peak = max(1, max(t for _, _, t in ms))
    best = max(range(12), key=lambda i: ms[i][2])
    slot = bw / 12
    for i, (mon, yr, t) in enumerate(ms):
        h = max(3, t / peak * bh)
        x = bx + i * slot + 7
        w = slot - 14
        col = RED if i == best and t else INK
        b.append(f'<rect x="{x:.1f}" y="{by + bh - h:.1f}" width="{w:.1f}" height="{h:.1f}" rx="5" fill="{col}" '
                 f'opacity="{1 if col == RED else .88}" class="a tb" style="transform-origin:bottom;'
                 f'animation:grow .8s cubic-bezier(.2,.8,.2,1) {.3 + i * .06:.2f}s both"><title>{t} in {mon} {yr}</title></rect>')
        b.append(f'<text x="{x + w / 2:.1f}" y="{by + bh + 22}" text-anchor="middle" class="mo" font-size="10.5" '
                 f'fill="{RED if i == best else MUTED}">{mon.upper()}</text>')
        if i == best and t:
            b.append(f'<g class="a tb" style="transform-origin:center bottom;animation:pop .5s cubic-bezier(.3,1.6,.5,1) 1.3s both">'
                     f'<text x="{x + w / 2:.1f}" y="{by + bh - h - 10:.1f}" text-anchor="middle" class="d8" font-size="17" '
                     f'fill="{RED}">{t}</text></g>')
    bd = s["best"]
    when = dt.date.fromisoformat(bd["date"]).strftime("%-d %b %Y").upper()
    b.append(f'<line x1="{bx}" y1="{by + bh + .5}" x2="{bx + bw}" y2="{by + bh + .5}" stroke="{LINE}"/>')
    b.append(f'<g {anim("fade", 1.5, .5)}><text x="{W - 40}" y="52" text-anchor="end" class="mo" font-size="11" fill="{MUTED}">'
             f'BUSIEST DAY · {when} · {bd["count"]}</text></g>')
    return svg(W, H, "".join(b), ["display-800", "display-700", "inter-400", "mono-500"],
               title=f'{s["total"]} contributions, {s["longest"]} day longest streak')


def tile(name, kicker, value, unit, note, bg, fg, delay):
    W, H = 272, 210
    ring = GREEN if bg != GREEN else INK
    b = [f'<g class="a" style="transform-origin:50% 100%;animation:swing .9s cubic-bezier(.2,.8,.2,1) {delay}s both">',
         card(W, H, bg, bg, 24),
         f'<circle cx="{W - 36}" cy="36" r="10" fill="none" stroke="{ring}" stroke-width="2" class="a tb" opacity="0" '
         f'style="transform-origin:center;animation:pulse 2.4s ease-out {delay + 1:.1f}s infinite"/>',
         f'<g class="a" style="transform-origin:center;animation:nudge 3s ease-in-out {delay + 1:.1f}s infinite">'
         f'<text x="{W - 36}" y="43" text-anchor="middle" class="d8" font-size="20" fill="{fg}">↗</text></g>',
         f'<text x="26" y="44" class="mo" font-size="11.5" fill="{fg}" letter-spacing="1.6" opacity=".85">{e(kicker)}</text>',
         counter(value, 24, 128, "d8", 72, fg, delay + .3, frames=18, dur=.9),
         f'<text x="26" y="160" class="i6" font-size="15" fill="{fg}">{e(unit)}</text>',
         f'<text x="26" y="184" class="i4" font-size="13" fill="{fg}" opacity=".75">{e(note)}</text>',
         '<defs><linearGradient id="ts" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
         '<stop offset=".5" stop-color="#fff" stop-opacity=".28"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>'
         f'</linearGradient><clipPath id="tc"><rect width="{W}" height="{H}" rx="24"/></clipPath></defs>',
         f'<g clip-path="url(#tc)"><rect x="0" y="0" width="{W * .6:.0f}" height="{H}" fill="url(#ts)" '
         f'class="a tb" style="transform:translateX(-200%);animation:shine 5s ease-in-out {delay + 2:.1f}s infinite"/></g>',
         '</g>']
    return svg(W, H + 16, "".join(b), ["display-800", "inter-400", "inter-600", "mono-500"],
               title=f"{value} {unit}")


def tiles():
    s = stats()
    return {
        "work": tile("work", "BUILD", PROF["public_repos"], "public repos", "Vue · React · Next.js", RED, "#FFFFFF", .1),
        "live": tile("live", "SHIP", PROFILE["live_apps"], "live apps", "in production today", GREEN, INK, .25),
        "commits": tile("commits", "COMMIT", s["total"], "contributions", "in the last 12 months", INK, "#FFFFFF", .4),
    }


def repo(i, name, desc, tech):
    W, H = 410, 176
    d = .1 + (i % 2) * .12 + (i // 2) * .08
    b = [f'<g {anim("rise", d, .8)}>', card(W, H, PAPER, LINE, 22)]
    b.append(f'<text x="26" y="34" class="mo" font-size="10.5" fill="{MUTED}" letter-spacing="1.4">'
             f'0{i + 1} · PROJECT</text>')
    b.append(f'<text x="26" y="68" class="d8" font-size="26" fill="{INK}" letter-spacing="-.5">{e(name)}</text>')
    b.append(f'<circle cx="{W - 34}" cy="34" r="13" fill="{RED}"/>'
             f'<g class="a" style="transform-origin:center;animation:nudge 3s ease-in-out {d + 1.5:.2f}s infinite">'
             f'<text x="{W - 34}" y="39.5" text-anchor="middle" class="d8" font-size="15" fill="#fff">↗</text></g>')
    for j, line in enumerate(wrap(desc, "inter-400", 14, W - 52)[:2]):
        b.append(f'<text x="26" y="{96 + j * 20}" class="i4" font-size="14" fill="{MUTED}">{e(line)}</text>')
    x = 26
    for t in tech:
        tw = width(t, "mono-500", 11) + 18
        b.append(f'<rect x="{x}" y="{H - 44}" width="{tw:.0f}" height="22" rx="11" fill="{SOFT}" stroke="{LINE}"/>'
                 f'<text x="{x + 9}" y="{H - 29}" class="mo" font-size="11" fill="{INK}">{e(t)}</text>')
        x += tw + 6
    b.append('</g>')
    return svg(W, H + 8, "".join(b), ["display-800", "inter-400", "mono-500"], title=f"{name}: {desc}")


def stack():
    W = 840
    b, x, y, row_h = [], 40, 86, 40
    items = []
    for i, (name, col) in enumerate(PROFILE["stack"]):
        w = width(name, "inter-600", 14) + 46
        if x + w > W - 40:
            x, y = 40, y + row_h
        items.append((name, col, x, y, w, i))
        x += w + 8
    H = y + 62
    b.append(card(W, H))
    b.append(f'<g {anim("fade", .05, .5)}><text x="40" y="52" class="d7" font-size="20" fill="{INK}">Stack</text>'
             f'<text x="{W - 40}" y="52" text-anchor="end" class="mo" font-size="12" fill="{MUTED}">'
             f'{len(items)} TOOLS I SHIP WITH</text></g>')
    for name, col, x, y, w, i in items:
        b.append(f'<g class="a tb" style="transform-origin:center;animation:pop .45s cubic-bezier(.3,1.5,.5,1) {.15 + i * .045:.3f}s both">'
                 f'<rect x="{x:.0f}" y="{y}" width="{w:.0f}" height="30" rx="15" fill="{PAPER}" stroke="{LINE}" stroke-width="1.5"/>'
                 f'<circle cx="{x + 17:.0f}" cy="{y + 15}" r="5" fill="{col}"/>'
                 f'<text x="{x + 29:.0f}" y="{y + 20}" class="i6" font-size="14" fill="{INK}">{e(name)}</text></g>')
    return svg(W, H, "".join(b), ["display-700", "inter-600", "mono-500"],
               title="Stack: " + ", ".join(n for n, _ in PROFILE["stack"]))


def main():
    OUT.mkdir(exist_ok=True)
    files = {"hero": hero(), "graph": graph(), "activity": activity(), "stack": stack()}
    files.update(tiles())
    for i, (name, desc, tech) in enumerate(PROFILE["repos"]):
        files[f"repo-{i + 1}"] = repo(i, name, desc, tech)
    for name, content in files.items():
        (OUT / f"{name}.svg").write_text(content)
    print(f"Rendered {len(files)} cards into {OUT.relative_to(ROOT)}/" + (" (static)" if STATIC else ""))


if __name__ == "__main__":
    main()
