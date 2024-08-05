from django.core.management.base import BaseCommand
from django.utils import timezone
from matches.models import Match, League

class Command(BaseCommand):
    help = 'Remove completed matches and leagues if they have no remaining matches'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        completed_matches = Match.objects.filter(date__lt=now - timezone.timedelta(hours=2, minutes=15))
        leagues_to_check = completed_matches.values_list('league', flat=True).distinct()

        # Delete completed matches
        completed_matches.delete()

        # Delete leagues with no remaining matches
        for league_id in leagues_to_check:
            if not Match.objects.filter(league_id=league_id).exists():
                League.objects.filter(id=league_id).delete()

        self.stdout.write(self.style.SUCCESS('Successfully removed completed matches and empty leagues'))
