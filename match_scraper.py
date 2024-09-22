import os
import django
from datetime import datetime
import pytz
from bs4 import BeautifulSoup
import requests

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_streaming_site.settings')
django.setup()

from matches.models import Match, League

def get_live_stream_url(match_url):
    try:
        response = requests.get(match_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        # Find the iframe URL in the textarea
        iframe_code = soup.find('textarea').get_text()
        start_index = iframe_code.find('src="') + len('src="')
        end_index = iframe_code.find('"', start_index)
        return iframe_code[start_index:end_index]
    except Exception as e:
        print(f"Error retrieving livestream URL from {match_url}: {e}")
        return ''

def determine_game_type(url):
    """Determine the game type from the URL."""
    if 'soccerstreams' in url:
        return Match.SOCCER
    elif 'nbastreams' in url:
        return Match.NBA
    elif 'nhlstreams' in url:
        return Match.NHL
    elif 'mlbstreams' in url:
        return Match.MLB
    elif 'mmastreams' in url:
        return Match.MMA
    elif 'boxingstreams' in url:
        return Match.BOXING
    elif 'nflstreams' in url:
        return Match.NFL
    elif 'cfbstreams' in url:
        return Match.CFB
    elif 'motorsportsstreams' in url:
        return Match.MOTOR_SPORTS
    else:
        return Match.SOCCER  # Default game type if not matched

def scrape_matches():
    base_urls = {
        'soccer': "https://bestsolaris.com/soccerstreams/",
        'nba': "https://bestsolaris.com/category/nbastreams/",
        'nhl': 'https://bestsolaris.com/category/nhlstreams/',
        'mlb': 'https://bestsolaris.com/category/mlbstreams/',
        'mma': 'https://bestsolaris.com/category/mmastreams/',
        'boxing': 'https://bestsolaris.com/category/boxingstreams/',
        # Add more base URLs for other game types here
    }
    
    all_matches = []

    for game_type, url in base_urls.items():
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        matches = []

        for match_item in soup.select('li.f1-podium--item'):
            title = match_item.select_one('.f1-podium--driver span.d-md-inline').get_text(strip=True)
            timestamp = match_item.select_one('.f1-podium--time')['data-zaman']
            match_url = match_item.select_one('a.f1-podium--link')['href']

            # Convert the timestamp to Nigeria time
            try:
                # Convert timestamp to datetime
                usa_time = datetime.fromtimestamp(int(timestamp), tz=pytz.timezone('America/New_York'))
                
                # Convert to Nigeria time
                nigeria_time = usa_time.astimezone(pytz.timezone('Africa/Lagos'))
                
                print(f"Match: {title}")
                print(f"USA time: {usa_time}")
                print(f"Nigeria time: {nigeria_time}")
            except ValueError as e:
                print(f"Error parsing timestamp: {timestamp} - {e}")
                continue

            # Get the livestream URL
            live_stream_url = get_live_stream_url(match_url)

            # Save to the database
            try:
                match, created = Match.objects.update_or_create(
                    title=title,
                    date=nigeria_time,
                    defaults={
                        'live_stream_url': live_stream_url,
                        'is_featured': False,
                        #'league': League.objects.first(),  # Replace with your actual league selection logic
                        'team1_name': 'Team 1',  # Placeholder
                        'team1_image_url': '',  # Placeholder
                        'team2_name': 'Team 2',  # Placeholder
                        'team2_image_url': '',  # Placeholder
                        'game_type': determine_game_type(url),
                    }
                )
                matches.append(match)
            except Exception as e:
                print(f"Error saving match: {e}")

        all_matches.extend(matches)

    return all_matches

if __name__ == '__main__':
    scrape_matches()
