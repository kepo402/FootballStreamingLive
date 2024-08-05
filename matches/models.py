from django.db import models
from django.utils import timezone

class League(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Match(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    live_stream_url = models.URLField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    team1_name = models.CharField(max_length=100)
    team1_image_url = models.URLField(blank=True, null=True)
    team2_name = models.CharField(max_length=100)
    team2_image_url = models.URLField(blank=True, null=True)

    def is_live(self):
        now = timezone.now()
        start_time = self.date
        soon_time = start_time - timezone.timedelta(minutes=30)
        end_time = start_time + timezone.timedelta(hours=2, minutes=15)
        return soon_time <= now <= end_time

    def save(self, *args, **kwargs):
        if self.date < timezone.now() - timezone.timedelta(hours=2, minutes=15):
            # Remove the match if it’s past the end time
            self.delete()
        else:
            # Otherwise, save it normally
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
