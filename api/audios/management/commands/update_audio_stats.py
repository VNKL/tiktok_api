from django.core.management import BaseCommand

from api.audios.models import Audio
from api.audios.utils import process_audios, process_audio_stats
from tiktok.parser import TikTok


class Command(BaseCommand):
    help = 'update stats for audios in database'

    def handle(self, *args, **options):
        pars_audio_from_tiktok()


def pars_audio_from_tiktok():
    tiktok = TikTok()
    audios = Audio.objects.values()
    if audios:
        audios = tiktok.get_audio_stats(audios=audios)
        process_audios(audios=audios)
        process_audio_stats(audios=audios)

    print('update audios stats completed')
