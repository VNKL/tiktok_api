from django.core.management import BaseCommand

from api.audios.utils import process_audios, process_audio_stats, get_new_audios
from tiktok.parser import TikTok


class Command(BaseCommand):
    help = 'pars audios from tiktok trends'

    def add_arguments(self, parser):
        parser.add_argument('-count', action='store', dest='count', type=int)
        parser.add_argument('-include_original', action='store', dest='include_original', type=bool)
        parser.add_argument('-russian_only', action='store', dest='russian_only', type=bool)
        parser.add_argument('-include_unnamed', action='store', dest='include_unnamed', type=bool)

    def handle(self, *args, **options):
        pars_trends(options)


def pars_trends(options):
    tiktok = TikTok()
    audios = tiktok.get_audios_from_trends(count=options['count'],
                                           include_original=options['include_original'],
                                           russian_only=options['russian_only'],
                                           include_unnamed=options['include_unnamed'])
    if audios:
        audios = get_new_audios(audios)
        audios = tiktok.get_audio_stats(audios=audios)
        process_audios(audios=audios)
        process_audio_stats(audios=audios)

    print('parsing trends completed')
