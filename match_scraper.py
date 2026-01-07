import os
import django
from datetime import datetime
import pytz
import requests
import re

# ---- Django setup ----
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_streaming_site.settings')
django.setup()

from matches.models import Match

URL = "https://sportsonline.st/prog.txt"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def scrape_matches():
    r = requests.get(URL, headers=HEADERS, timeout=15)
    r.raise_for_status()

    lines = r.text.splitlines()

    nigeria_tz = pytz.timezone("Africa/Lagos")
    utc_tz = pytz.UTC

    today = datetime.utcnow().date()  # IMPORTANT: use UTC date

    saved = 0

    for line in lines:
        line = line.strip()

        if not line or "|" not in line:
            continue

        try:
            left, stream_url = map(str.strip, line.split("|", 1))
        except ValueError:
            continue

        # Extract time
        time_match = re.match(r"^(\d{1,2}:\d{2})\s+(.*)$", left)
        if not time_match:
            continue

        time_part = time_match.group(1)
        title = time_match.group(2).strip()

        if "Basketball:" in title:
            continue

        # ---- TIME HANDLING (CORRECT) ----
        match_time = datetime.strptime(time_part, "%H:%M").time()
        match_dt = datetime.combine(today, match_time)

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

        saved += 1

    print(f"Saved/updated {saved} matches")


if __name__ == "__main__":
    scrape_matches()
