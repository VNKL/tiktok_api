from django.db import models

from api.users.models import User


class Audio(models.Model):

    owner = models.ForeignKey(User, related_name='added_audios', on_delete=models.SET_NULL, null=True)
    artist = models.TextField()
    title = models.TextField()
    album = models.TextField(blank=True)
    videos_count = models.IntegerField(default=0)
    audio_id = models.BigIntegerField()
    duration = models.IntegerField()
    original = models.BooleanField()
    play_url = models.TextField()
    cover_large_url = models.TextField()
    cover_medium_url = models.TextField()
    cover_small_url = models.TextField()
    add_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.artist} - {self.title}'


class AudioStat(models.Model):

    audio = models.ForeignKey(Audio, related_name='stats', on_delete=models.CASCADE)
    videos_count = models.IntegerField(blank=True)
    count_delta = models.IntegerField(blank=True, null=True)
    count_delta_percent = models.FloatField(blank=True, null=True)
    date = models.DateField(auto_now=True)

    def __str__(self):
        return f'Stat for "{self.audio.artist} - {self.audio.title}" by {self.date}'


class AudioLike(models.Model):

    user = models.ForeignKey(User, related_name='liked_audios', on_delete=models.CASCADE)
    audio = models.ForeignKey(Audio, related_name='likes', on_delete=models.CASCADE)
    add_date = models.DateTimeField(auto_now=True)
