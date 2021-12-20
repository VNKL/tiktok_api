from django.contrib import admin
from .models import *


@admin.register(Audio)
class AudioAdmin(admin.ModelAdmin):
    list_display = 'owner', 'artist', 'title', 'album', 'videos_count', 'duration', 'audio_id', 'original', 'add_date'


@admin.register(AudioStat)
class AudioStatAdmin(admin.ModelAdmin):
    list_display = 'audio', 'videos_count', 'date', 'count_delta', 'count_delta_percent'


@admin.register(AudioLike)
class AudioLikeAdmin(admin.ModelAdmin):
    list_display = 'user', 'audio', 'add_date'
