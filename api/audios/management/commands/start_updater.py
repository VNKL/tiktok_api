from datetime import datetime, time, timedelta
from random import uniform
from time import sleep
from multiprocessing import Process

from django import db
from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    def handle(self, *args, **options):
        start_updater()


def start_updater():
    trends_process = Process(target=trends_updater)
    stats_process = Process(target=stats_updater)

    trends_process.start()
    sleep(uniform(900, 1300))
    stats_process.start()

    trends_process.join()
    stats_process.join()


def stats_updater():
    print('background updater start updating stats')
    process = Process(target=call_command, args=('update_audio_stats',))
    process.start()
    process.join()

    update_time = _get_stats_update_time()
    while True:
        if datetime.now() >= update_time:
            db.connections.close_all()
            process = Process(target=call_command,
                              args=('update_audio_stats',))
            process.start()
            process.join()
            update_time = _get_stats_update_time()
            print('background updater updated stats')
        else:
            sleep(uniform(900, 1200))


def trends_updater():
    print('background updater start updating trends')
    db.connections.close_all()
    process = Process(target=call_command,
                      args=('pars_trends',),
                      kwargs={'count': 2000,
                              'include_original': True,
                              'russian_only': True,
                              'include_unnamed': False})
    process.start()
    process.join()

    update_time = _get_trends_update_time()
    while True:
        if datetime.now() >= update_time:
            db.connections.close_all()
            process = Process(target=call_command,
                              args=('pars_trends',),
                              kwargs={'count': 2000,
                                      'include_original': True,
                                      'russian_only': True,
                                      'include_unnamed': False})
            process.start()
            process.join()
            update_time = _get_trends_update_time()
            print('background updater updated trends')
        else:
            sleep(uniform(900, 1200))


def _get_stats_update_time():
    return datetime.combine(datetime.now().date(), time(hour=3)) + timedelta(days=1)


def _get_trends_update_time():
    return datetime.now() + timedelta(hours=3, minutes=18)
