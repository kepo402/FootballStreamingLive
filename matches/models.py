from django.db import models
from django.utils import timezone

class League(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Match(models.Model):
    # Existing choices
    NBA = 'nba'
    NHL = 'nhl'
    MLB = 'mlb'
    MMA = 'mma'
    BOXING = 'boxing'
    NFL = 'nfl'
    CFB = 'cfb'
    MOTOR_SPORTS = 'motor_sports'
    SOCCER = 'soccer'

    GAME_TYPES = [
        (NBA, 'NBA Streams'),
        (NHL, 'NHL Streams'),
        (MLB, 'MLB Streams'),
        (MMA, 'MMA Streams'),
        (BOXING, 'Boxing Streams'),
        (NFL, 'NFL Streams'),
        (CFB, 'CFB Streams'),
        (MOTOR_SPORTS, 'Motor Sports Streams'),
        (SOCCER, 'Soccer Streams'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    live_stream_url = models.URLField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    team1_name = models.CharField(max_length=100)
    team1_image_url = models.URLField(blank=True, null=True)
    team2_name = models.CharField(max_length=100)
    team2_image_url = models.URLField(blank=True, null=True)
    game_type = models.CharField(max_length=50, choices=GAME_TYPES, default=SOCCER)

    def is_live(self):
        now = timezone.now()
        start_time = self.date
        soon_time = start_time - timezone.timedelta(minutes=30)
        end_time = start_time + timezone.timedelta(hours=4)
        return soon_time <= now <= end_time

    def save(self, *args, **kwargs):
        if self.pk and self.date < timezone.now() - timezone.timedelta(hours=4):
            super().delete()
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return self.title


    
class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title