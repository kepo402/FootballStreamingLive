import os
import django
from datetime import datetime, timedelta
import pytz
import requests
import re

# ---- Django setup ----
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_streaming_site.settings')
django.setup()

from matches.models import Match

URL = "https://sportsonline.st/prog.txt"
HEADERS = {"User-Agent": "Mozilla/5.0"}

DAY_HEADERS = {
    "MONDAY", "TUESDAY", "WEDNESDAY",
    "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"
}

WEEKDAY_MAP = {
    "MONDAY": 0,
    "TUESDAY": 1,
    "WEDNESDAY": 2,
    "THURSDAY": 3,
    "FRIDAY": 4,
    "SATURDAY": 5,
    "SUNDAY": 6,
}


def scrape_matches():
    r = requests.get(URL, headers=HEADERS, timeout=15)
    r.raise_for_status()

    lines = r.text.splitlines()

    nigeria_tz = pytz.timezone("Africa/Lagos")
    utc_tz = pytz.UTC

    now_utc = datetime.now(utc_tz)
    base_date = now_utc.date()
    current_date = base_date

    saved = 0

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # ---- Detect explicit day headers ----
        upper_line = line.upper()
        if upper_line in DAY_HEADERS:
            today_weekday = base_date.weekday()
            target_weekday = WEEKDAY_MAP[upper_line]
            delta_days = (target_weekday - today_weekday) % 7
            current_date = base_date + timedelta(days=delta_days)
            continue

        if "|" not in line:
            continue

        try:
            left, stream_url = map(str.strip, line.split("|", 1))
        except ValueError:
            continue

        # Extract time and title
        time_match = re.match(r"^(\d{1,2}:\d{2})\s+(.*)$", left)
        if not time_match:
            continue

        time_part = time_match.group(1)
        title = time_match.group(2).strip()

        if "Basketball:" in title:
            continue

        match_time = datetime.strptime(time_part, "%H:%M").time()
        match_dt = datetime.combine(current_date, match_time)

        utc_dt = utc_tz.localize(match_dt)
        nigeria_dt = utc_dt.astimezone(nigeria_tz)

        match, created = Match.objects.get_or_create(
            title=title,
            date=nigeria_dt,
            defaults={
                "game_type": Match.SOCCER,
                "live_stream_url": stream_url,
            }
        )

        if created:
            saved += 1

    print(f"Saved {saved} new matches")


if __name__ == "__main__":
    scrape_matches()
