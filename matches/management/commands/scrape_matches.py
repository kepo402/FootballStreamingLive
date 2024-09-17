# matches/management/commands/scrape_matches.py
from django.core.management.base import BaseCommand
from match_scraper import scrape_matches  # Import your scraping function

class Command(BaseCommand):
    help = 'Scrape matches and save them to the database'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting the scraping process...")
        scraped_matches = scrape_matches()  # Call the scraping function
        self.stdout.write(self.style.SUCCESS(f"Successfully scraped {len(scraped_matches)} matches"))
