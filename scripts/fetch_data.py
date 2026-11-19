#!/usr/bin/env python3
"""Fetch the public contribution calendar and profile numbers into data/.

No dependencies. Run daily by .github/workflows/readme-cards.yml.
"""
import json
import os
import re
import urllib.request
from pathlib import Path

USER = os.environ.get("GH_USER", "kursadsahin0")
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def get(url, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": "readme-cards", **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def contributions():
    html = get(f"https://github.com/users/{USER}/contributions")
    days = {}
    for m in re.finditer(r'data-date="(\d{4}-\d\d-\d\d)"\s+id="([^"]+)"\s+data-level="(\d)"', html):
        days[m.group(2)] = {"date": m.group(1), "level": int(m.group(3)), "count": 0}
    for m in re.finditer(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', html):
        d = days.get(m.group(1))
        n = re.match(r"\s*(\d[\d,]*) contribution", m.group(2))
        if d and n:
            d["count"] = int(n.group(1).replace(",", ""))
    out = sorted(days.values(), key=lambda d: d["date"])
    if len(out) < 300:
        raise SystemExit(f"Only parsed {len(out)} days; GitHub markup may have changed.")
    return out


def profile():
    headers = {"Accept": "application/vnd.github+json"}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    u = json.loads(get(f"https://api.github.com/users/{USER}", headers))
    return {"public_repos": u["public_repos"], "followers": u["followers"], "created_at": u["created_at"]}


if __name__ == "__main__":
    DATA.mkdir(exist_ok=True)
    days = contributions()
    (DATA / "contributions.json").write_text(json.dumps(days, indent=0) + "\n")
    (DATA / "profile.json").write_text(json.dumps(profile(), indent=2) + "\n")
    print(f"{len(days)} days, {sum(d['count'] for d in days)} contributions")
