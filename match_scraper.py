import os
import django
from datetime import datetime
import pytz
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin

# Django setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "football_streaming_site.settings")
django.setup()

from matches.models import Match

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

BASE_URL = "https://crackstreams1.in"

def get_embed_url(match_url):
    try:
        r = requests.get(match_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        iframe = soup.find("iframe")
        return iframe["src"] if iframe else None
    except Exception as e:
        print(f"[IFRAME ERROR] {match_url}: {e}")
        return None

def scrape_matches():
    url = f"{BASE_URL}/Soccer/"
    r = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    matches = soup.find_all("a", class_="btn btn-default btn-lg btn-block")
    print(f"Found {len(matches)} matches")

    for m in matches:
        title = m.find("h4").get_text(strip=True)
        date_time_text = m.find("p").get_text(strip=True)

        # Fix datetime parsing
        try:
            time_part, date_part = date_time_text.replace(" ET", "").split(" - ")
            naive_dt = datetime.strptime(
                f"{date_part} {time_part}",
                "%m/%d/%Y %I:%M %p"
            )
            et_time = pytz.timezone("America/New_York").localize(naive_dt)
            nigeria_time = et_time.astimezone(pytz.timezone("Africa/Lagos"))
        except Exception as e:
            print(f"[DATE ERROR] {title}: {e}")
            continue

        match_url = urljoin(BASE_URL, m["href"])
        embed_url = get_embed_url(match_url)

        if not embed_url:
            print(f"[NO STREAM] {title}")
            continue

        Match.objects.update_or_create(
            title=title,
            date=nigeria_time,
            defaults={
                "live_stream_url": embed_url,
                "is_featured": False,
                "game_type": Match.SOCCER,
                "team1_name": title.split(" vs ")[0],
                "team2_name": title.split(" vs ")[-1],
            }
        )

        print(f"✅ Saved: {title} @ {nigeria_time}")

if __name__ == "__main__":
    scrape_matches()
