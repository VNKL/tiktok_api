from django.utils.timezone import now
from rest_framework import serializers

from .models import *


class AudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Audio
        fields = 'artist', 'title', 'album', 'videos_count', 'duration', 'audio_id',  'original', \
                 'play_url', 'cover_large_url', 'cover_medium_url', 'cover_small_url', 'add_date',


class AudioExtendedSerializer(serializers.ModelSerializer):
    stats = serializers.SerializerMethodField()

    class Meta:
        model = Audio
        fields = 'artist', 'title', 'album', 'audio_id', 'duration', 'duration', 'original', \
                 'play_url', 'cover_large_url', 'cover_medium_url', 'cover_small_url', 'stats'

    def get_stats(self, instance):
        stats = instance.stats.all().order_by('-date')
        return AudioStatSerializer(stats, many=True).data


class ChartSerializer(serializers.ModelSerializer):
    audio = serializers.SerializerMethodField()

    class Meta:
        model = AudioStat
        fields = 'videos_count', 'date', 'count_delta', 'count_delta_percent', 'audio'

    def get_audio(self, instance):
        audio = instance.audio
        return AudioLikedSerializer(audio).data


class AudioLikedSerializer(serializers.Serializer):
    artist = serializers.CharField()
    title = serializers.CharField()
    videos_count = serializers.IntegerField()
    duration = serializers.IntegerField()
    audio_id = serializers.CharField()
    original = serializers.BooleanField()
    play_url = serializers.CharField()
    cover_small_url = serializers.CharField()
    add_date = serializers.DateTimeField()
    is_liked = serializers.BooleanField(default=False)


class AudioStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioStat
        fields = 'videos_count', 'date', 'count_delta', 'count_delta_percent'


class ParsTrendsViewSerializer(serializers.Serializer):
    count = serializers.IntegerField(default=30)
    include_original = serializers.BooleanField(default=True)
    russian_only = serializers.BooleanField(default=True)
    include_unnamed = serializers.BooleanField(default=False)


class AudioIDViewSerializer(serializers.Serializer):
    audio_id = serializers.IntegerField()


class AudioAddViewSerializer(serializers.Serializer):
    tiktok_url = serializers.CharField()


class AudiosGetQuerysetSerializer(serializers.Serializer):
    order_by = serializers.ChoiceField(choices=['artist', 'title', 'original', 'duration', 'videos_count', 'add_date'],
                                       default='videos_count')
    order = serializers.ChoiceField(choices=['asc', 'desc'], default='desc')
    title = serializers.CharField(default='')
    artist = serializers.CharField(default='')
