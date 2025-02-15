import os
import django
from datetime import datetime
import pytz
from bs4 import BeautifulSoup
import requests

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_streaming_site.settings')
django.setup()

from matches.models import Match

def get_embed_url(match_url):
    """Extracts the iframe embed URL from the match page."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    try:
        response = requests.get(match_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            iframe = soup.find("iframe")  # Find the first iframe
            if iframe:
                return iframe.get("src")  # Extract the iframe URL
    except Exception as e:
        print(f"Error fetching iframe from {match_url}: {e}")
    
    return None  # Return None if no iframe is found

def scrape_matches():
    url = "https://crack-streams.live/Soccer-stream/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Failed to fetch data, status code: {response.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    match_listings = soup.find_all('a', class_='btn btn-default btn-lg btn-block')

    for match in match_listings:
        match_url = match['href']  # Main match page URL
        title = match.find('h4', class_='media-heading').text.strip()
        date_time_text = match.find('p').text.strip()

        # Extract time and date
        try:
            time_part, date_part = date_time_text.split(' - ')

            # Convert to datetime object in Eastern Time (ET)
            et_tz = pytz.timezone('America/New_York')
            naive_dt = datetime.strptime(f"{date_part} {time_part}", "%m/%d/%Y %I:%M %p ET")
            et_time = et_tz.localize(naive_dt)

            # Convert to Nigeria time (WAT)
            nigeria_time = et_time.astimezone(pytz.timezone('Africa/Lagos'))
        except Exception as e:
            print(f"Error parsing date/time for {title}: {e}")
            continue

        # Extract the iframe URL
        embed_url = get_embed_url(match_url)
        if not embed_url:
            print(f"No iframe found for {title}")
            continue  # Skip if there's no valid embed link

        # Save match to the database
        match_obj, created = Match.objects.update_or_create(
            title=title,
            date=nigeria_time,
            defaults={
                'live_stream_url': embed_url,  # Save the direct iframe URL
                'is_featured': False,
                'game_type': Match.SOCCER,
                'team1_name': 'Team 1',
                'team2_name': 'Team 2',
            }
        )

        print(f"Saved: {title} at {nigeria_time}, Iframe URL: {embed_url}")

if __name__ == '__main__':
    scrape_matches()
