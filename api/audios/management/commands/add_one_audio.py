from django.core.management import BaseCommand

from api.audios.utils import process_audios, process_audio_stats
from tiktok.parser import TikTok


class Command(BaseCommand):
    help = 'pars audio from one tiktok'

    def add_arguments(self, parser):
        parser.add_argument('-tiktok_url', action='store', dest='tiktok_url', type=str)
        parser.add_argument('-owner_username', action='store', dest='owner_username', type=str)

    def handle(self, *args, **options):
        pars_audio_from_tiktok(options)


def pars_audio_from_tiktok(options):
    tiktok = TikTok()
    audio = tiktok.get_audio_from_tiktok(tiktok_url=options['tiktok_url'])
    if audio:
        audios = tiktok.get_audio_stats(audios=audio)
        process_audios(audios=audios, owner_username=options['owner_username'])
        process_audio_stats(audios=audios)

    print('parsing one audio completed')
