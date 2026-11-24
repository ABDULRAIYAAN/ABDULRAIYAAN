#!/usr/bin/env python3
"""
Read daily contribution counts from GitHub's public contributions page
(no token needed) and write data/contributions.json with the raw days plus
derived stats: total, current streak, longest streak, best day, monthly totals.

Run daily by .github/workflows/update-profile-art.yml.
"""
import datetime
import json
import os
import re
import sys
from collections import OrderedDict

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_PROFILE_USER", "ABDULRAIYAAN")
URL = f"https://github.com/users/{USERNAME}/contributions"
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT_PATH = os.path.join(ROOT, "data", "contributions.json")


def fetch_days():
    resp = requests.get(URL, headers={"User-Agent": "profile-readme/1.0"}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    cells = soup.select("td.ContributionCalendar-day")
    if not cells:
        sys.exit("No calendar cells found. GitHub's markup may have changed.")

    tooltips = {t.get("for"): t.get_text(strip=True) for t in soup.find_all("tool-tip")}

    days = []
    for td in cells:
        date = td.get("data-date")
        if not date:
            continue
        text = tooltips.get(td.get("id"), "")
        m = re.match(r"([\d,]+)\s+contribution", text)
        count = int(m.group(1).replace(",", "")) if m else 0
        days.append({"date": date, "count": count, "level": int(td.get("data-level") or 0)})

    days.sort(key=lambda d: d["date"])
    return days


def current_streak(days):
    i = len(days) - 1
    if i >= 0 and days[i]["count"] == 0:
        i -= 1  # today is not over yet, so it does not break the streak
    n = 0
    while i >= 0 and days[i]["count"] > 0:
        n += 1
        i -= 1
    return n


def longest_streak(days):
    best = run = 0
    for d in days:
        run = run + 1 if d["count"] > 0 else 0
        best = max(best, run)
    return best


def main():
    days = fetch_days()
    total = sum(d["count"] for d in days)
    best = max(days, key=lambda d: d["count"]) if days else {"date": None, "count": 0}

    months = OrderedDict()
    for d in days:
        key = d["date"][:7]
        months[key] = months.get(key, 0) + d["count"]

    data = {
        "user": USERNAME,
        "updated": datetime.datetime.utcnow().strftime("%Y-%m-%d"),
        "total": total,
        "current_streak": current_streak(days),
        "longest_streak": longest_streak(days),
        "active_days": sum(1 for d in days if d["count"] > 0),
        "best_day": {"date": best["date"], "count": best["count"]},
        "months": months,
        "days": days,
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(data, f, indent=1)
    print(f"{USERNAME}: {total} contributions, streak {data['current_streak']}, "
          f"longest {data['longest_streak']}")


if __name__ == "__main__":
    main()
