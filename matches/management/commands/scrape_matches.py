from django.core.management.base import BaseCommand
from datetime import datetime
import pytz
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from matches.models import Match

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

BASE_URL = "https://crackstreams1.in"

class Command(BaseCommand):
    help = "Scrape soccer matches automatically"

    def handle(self, *args, **kwargs):
        url = f"{BASE_URL}/Soccer/"
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")

        matches = soup.find_all("a", class_="btn btn-default btn-lg btn-block")
        self.stdout.write(f"Found {len(matches)} matches")

        for m in matches:
            title = m.find("h4").get_text(strip=True)
            date_time_text = m.find("p").get_text(strip=True)

            try:
                time_part, date_part = date_time_text.replace(" ET", "").split(" - ")
                naive_dt = datetime.strptime(
                    f"{date_part} {time_part}",
                    "%m/%d/%Y %I:%M %p"
                )
                et_time = pytz.timezone("America/New_York").localize(naive_dt)
                nigeria_time = et_time.astimezone(pytz.timezone("Africa/Lagos"))
            except Exception:
                continue

            match_url = urljoin(BASE_URL, m["href"])

            Match.objects.update_or_create(
                title=title,
                date=nigeria_time,
                defaults={
                    "live_stream_url": match_url,
                    "game_type": Match.SOCCER,
                }
            )

            self.stdout.write(f"Saved: {title}")
