from django import db
from django.utils.timezone import now
from django.shortcuts import get_object_or_404

from api.audios.models import Audio, AudioStat, AudioLike
from api.audios.serializers import AudiosGetQuerysetSerializer
from api.users.models import User


def process_audios(audios, owner_username=None):
    user = User.objects.filter(username=owner_username).first() if owner_username else None
    audios_to_create = []
    audios_to_update = []
    for audio in audios:
        existed_audio_obj = Audio.objects.filter(audio_id=audio['audio_id'] if 'audio_id' in audio.keys() else audio['id']).first()
        if not existed_audio_obj:
            audio_obj = Audio(artist=audio['artist'] if 'artist' in audio.keys() else audio['authorName'],
                              title=audio['title'],
                              album=audio['album'],
                              audio_id=audio['audio_id'] if 'audio_id' in audio.keys() else audio['id'],
                              duration=audio['duration'],
                              original=audio['original'],
                              play_url=audio['play_url'] if 'play_url' in audio.keys() else audio['playUrl'],
                              cover_large_url=audio['cover_large_url'] if 'cover_large_url' in audio.keys() else audio['coverLarge'],
                              cover_medium_url=audio['cover_medium_url'] if 'cover_medium_url' in audio.keys() else audio['coverMedium'],
                              cover_small_url=audio['cover_small_url'] if 'cover_small_url' in audio.keys() else audio['coverThumb'],
                              videos_count=audio['videos_count'],
                              owner=user)
            audios_to_create.append(audio_obj)
        else:
            existed_audio_obj.videos_count = audio['videos_count']
            audios_to_update.append(existed_audio_obj)

    batch_size = 100
    if audios_to_create:
        Audio.objects.bulk_create(audios_to_create, batch_size)
    if audios_to_update:
        Audio.objects.bulk_update(audios_to_update, batch_size=batch_size, fields=['videos_count'])

    if user:
        last_audio = Audio.objects.filter(owner=user).order_by('-pk').first()
        if last_audio:
            existed_like = AudioLike.objects.filter(audio=last_audio, user=user).first()
            if not existed_like:
                like = AudioLike(audio=last_audio, user=user)
                like.save()


def process_audio_stats(audios):
    today = now().date()
    stats_to_create = []
    stats_to_update = []
    for audio in audios:
        if audio['videos_count'] == 0:
            continue
        audio_obj = Audio.objects.filter(audio_id=audio['audio_id'] if 'audio_id' in audio.keys() else audio['id']).first()
        prev_stat = AudioStat.objects.filter(audio=audio_obj).exclude(date=today).order_by('-date').first()
        count_delta = audio['videos_count'] - prev_stat.videos_count if prev_stat else None
        count_delta_percent = round((audio['videos_count'] / prev_stat.videos_count - 1), 4) if prev_stat else None
        exist_stat_obj = AudioStat.objects.filter(audio=audio_obj, date=today).first()
        if not exist_stat_obj:
            stat_obj = AudioStat(audio=audio_obj,
                                 videos_count=audio['videos_count'],
                                 date=now().date(),
                                 count_delta=count_delta,
                                 count_delta_percent=count_delta_percent)
            stats_to_create.append(stat_obj)
        else:
            exist_stat_obj.videos_count = audio['videos_count']
            exist_stat_obj.count_delta = count_delta
            exist_stat_obj.count_delta_percent = count_delta_percent
            stats_to_update.append(exist_stat_obj)

    batch_size = 100
    if stats_to_create:
        AudioStat.objects.bulk_create(stats_to_create, batch_size)
    if stats_to_update:
        AudioStat.objects.bulk_update(stats_to_update, batch_size=batch_size, fields=['videos_count',
                                                                                      'count_delta',
                                                                                      'count_delta_percent'])


def process_like(audio_id, username):
    audio = Audio.objects.filter(audio_id=audio_id).first()
    user = get_object_or_404(User, username=username)
    existed_like = AudioLike.objects.filter(audio=audio, user=user).first()
    if existed_like:
        existed_like.delete()
    else:
        like = AudioLike(audio=audio, user=user)
        like.save()


def get_new_audios(audios):
    audios_ids = [int(x['id']) for x in audios]
    existed_audios = Audio.objects.filter(audio_id__in=audios_ids)
    existed_audios_ids = [x.audio_id for x in existed_audios]
    new_audios_ids = set(audios_ids) - set(existed_audios_ids)
    db.connections.close_all()
    return [x for x in audios if int(x['id']) in new_audios_ids]


def get_sp_all_audios_with_likes(query_params, user_id):
    order_by = '-videos_count'
    serializer = AudiosGetQuerysetSerializer(data=query_params)
    if serializer.is_valid():
        order_by = f"{'-' if serializer.data['order'] == 'desc' else ''}{serializer.data['order_by']}"
        if serializer.data['artist'] and serializer.data['title']:
            all_audios = Audio.objects.filter(title__icontains=serializer.data['title'],
                                              artist__icontains=serializer.data['artist']).order_by(order_by)
        elif serializer.data['artist']:
            all_audios = Audio.objects.filter(artist__icontains=serializer.data['artist']).order_by(order_by)
        elif serializer.data['title']:
            all_audios = Audio.objects.filter(title__icontains=serializer.data['title']).order_by(order_by)
        else:
            all_audios = Audio.objects.all().order_by(order_by)
    else:
        all_audios = Audio.objects.all().order_by(order_by)

    liked_audios = Audio.objects.filter(likes__in=AudioLike.objects.filter(user=user_id))

    return_audios = []
    for audio in all_audios:
        if audio in liked_audios:
            audio.is_liked = True
        else:
            audio.is_liked = False
        return_audios.append(audio)

    return return_audios


def get_sp_liked_audios(query_params, user_id):
    order_by = '-videos_count'
    serializer = AudiosGetQuerysetSerializer(data=query_params)
    if serializer.is_valid():
        order_by = f"{'-' if serializer.data['order'] == 'desc' else ''}{serializer.data['order_by']}"
        if serializer.data['artist'] and serializer.data['title']:
            liked_audios = Audio.objects.filter(likes__in=AudioLike.objects.filter(user=user_id),
                                                title__icontains=serializer.data['title'],
                                                artist__icontains=serializer.data['artist']
                                                ).order_by(order_by)
        elif serializer.data['artist']:
            liked_audios = Audio.objects.filter(likes__in=AudioLike.objects.filter(user=user_id),
                                                artist__icontains=serializer.data['artist']
                                                ).order_by(order_by)
        elif serializer.data['title']:
            liked_audios = Audio.objects.filter(likes__in=AudioLike.objects.filter(user=user_id),
                                                title__icontains=serializer.data['title'],
                                                ).order_by(order_by)
        else:
            liked_audios = Audio.objects.filter(likes__in=AudioLike.objects.filter(user=user_id),
                                                ).order_by(order_by)
    else:
        liked_audios = Audio.objects.filter(likes__in=AudioLike.objects.filter(user=user_id)
                                            ).order_by(order_by)

    return_audios = []
    for audio in liked_audios:
        audio.is_liked = True
        return_audios.append(audio)

    return return_audios


def get_sp_owned_audios(query_params, user_id):
    order_by = '-videos_count'
    serializer = AudiosGetQuerysetSerializer(data=query_params)
    if serializer.is_valid():
        order_by = f"{'-' if serializer.data['order'] == 'desc' else ''}{serializer.data['order_by']}"
        if serializer.data['artist'] and serializer.data['title']:
            owned_audios = Audio.objects.filter(owner=user_id,
                                                title__icontains=serializer.data['title'],
                                                artist__icontains=serializer.data['artist']
                                                ).order_by(order_by)
        elif serializer.data['artist']:
            owned_audios = Audio.objects.filter(owner=user_id,
                                                artist__icontains=serializer.data['artist']
                                                ).order_by(order_by)
        elif serializer.data['title']:
            owned_audios = Audio.objects.filter(owner=user_id,
                                                title__icontains=serializer.data['title'],
                                                ).order_by(order_by)
        else:
            owned_audios = Audio.objects.filter(owner=user_id).order_by(order_by)
    else:
        owned_audios = Audio.objects.filter(owner=user_id).order_by(order_by)

    return_audios = []
    for audio in owned_audios:
        audio.is_liked = True
        return_audios.append(audio)

    return return_audios
