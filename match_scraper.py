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

# Function to retrieve the live stream URL
def get_live_stream_url(match_url):
    try:
        response = requests.get(match_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the textarea that contains the iframe
        textarea = soup.find('textarea')
        if textarea:
            # Extract the iframe code from the textarea
            iframe_code = textarea.get_text()

            # Debug: Print the extracted iframe content
            print(f"Extracted iframe content from {match_url}:")
            print(iframe_code)  # Debugging the extracted iframe content

            # Find the src attribute in the iframe code
            start_index = iframe_code.find('src="') + len('src="')
            end_index = iframe_code.find('"', start_index)

            if start_index != -1 and end_index != -1:
                return iframe_code[start_index:end_index]
            else:
                print(f"Error: Couldn't find iframe src in {match_url}")
                return ''
        else:
            print(f"Error: No textarea found in {match_url}")
            return ''
        
    except Exception as e:
        print(f"Error retrieving live stream URL from {match_url}: {e}")
        return ''

# Function to determine the game type from the URL
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

# Function to scrape matches
def scrape_matches():
    base_urls = {
        'soccer': "https://v1.bestsolaris.com/soccerstreams/",
        'nba': "https://v1.bestsolaris.com/nbastreams/",
        'nhl': 'https://v1.bestsolaris.com/nhlstreams/',
        'mlb': 'https://v1.bestsolaris.com/mlbstreams/',
        'mma': 'https://v1.bestsolaris.com/mmastreams/',
        'boxing': 'https://v1.bestsolaris.com/boxingstreams/',
        # Add more base URLs for other game types here
    }
    
    all_matches = []

    for game_type, url in base_urls.items():
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        matches = []

        # Iterate over the match items
        for match_item in soup.select('li.f1-podium--item'):
            # Extract match title
            title = match_item.select_one('.f1-podium--driver span.d-md-inline').get_text(strip=True)
            
            # Try to extract match timestamp
            time_element = match_item.select_one('.f1-podium--time')
            if time_element and 'data-zaman' in time_element.attrs:
                timestamp = time_element['data-zaman']
            else:
                print(f"Warning: No timestamp found for match: {title}. Skipping this match.")
                print(f"HTML of match item: {match_item.prettify()}")
                continue  # Skip this match if timestamp is not found

            # Extract match URL
            match_url = match_item.select_one('a.f1-podium--link')['href']

            # Convert the timestamp to Nigeria time
            try:
                # Convert timestamp to datetime (USA time, New York)
                usa_time = datetime.fromtimestamp(int(timestamp), tz=pytz.timezone('America/New_York'))
                
                # Convert to Nigeria time
                nigeria_time = usa_time.astimezone(pytz.timezone('Africa/Lagos'))
                
                # Debug output to check the match details
                print(f"Match: {title}")
                print(f"USA time: {usa_time}")
                print(f"Nigeria time: {nigeria_time}")
            except ValueError as e:
                print(f"Error parsing timestamp: {timestamp} - {e}")
                continue

            # Get the livestream URL
            live_stream_url = get_live_stream_url(match_url)

            # Save the match to the database
            try:
                match, created = Match.objects.update_or_create(
                    title=title,
                    date=nigeria_time,
                    defaults={
                        'live_stream_url': live_stream_url,
                        'is_featured': False,
                        # You can update the logic for selecting a league
                        #'league': League.objects.first(),  # Placeholder league logic
                        'team1_name': 'Team 1',  # Placeholder team name
                        'team1_image_url': '',  # Placeholder team image
                        'team2_name': 'Team 2',  # Placeholder team name
                        'team2_image_url': '',  # Placeholder team image
                        'game_type': determine_game_type(url),  # Determine game type (e.g., soccer, NBA, etc.)
                    }
                )
                matches.append(match)
            except Exception as e:
                print(f"Error saving match: {e}")

        all_matches.extend(matches)

    return all_matches

# Main entry point for the script
if __name__ == '__main__':
    scrape_matches() 



