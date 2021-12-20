def is_text_russian(text, rate=0.5):
    if not text:
        return False
    vocabulary = 'абвгдеёжзийклмнопрстуфхцчшщЪыьэюя'
    ru_symbols = [x for x in text.lower() if x in vocabulary]
    ru_symbols_rate = len(ru_symbols) / len(text)
    if ru_symbols_rate > rate:
        return True
    return False


def is_audio_russian(audio, include_original=False):
    if not isinstance(audio, dict):
        return False
    check_list = []
    if 'album' in audio.keys():
        check_list.append(is_text_russian(audio['album']))
    if 'authorName' in audio.keys():
        check_list.append(is_text_russian(audio['authorName']))
    if not include_original and 'title' in audio.keys():
        check_list.append(is_text_russian(audio['title']))
    if any(check_list):
        return True
    return False


def clean_audios_russian(audios, include_original=False):
    return [x for x in audios if is_audio_russian(audio=x, include_original=include_original)]


def clean_audios_doubles(audios):
    audios_dict = {}
    for audio in audios:
        audios_dict[audio['id']] = audio
    return list(audios_dict.values())


def clean_unnamed_audios(audios):
    return [x for x in audios if x['title'] not in ['оригинальный звук', 'оригінальний звук']]


def get_audios_from_tiktoks(tiktoks, include_original=False, russian_only=True, include_unnamed=False):
    if include_original:
        audios = [x['music'] for x in tiktoks]
    else:
        audios = [x['music'] for x in tiktoks if not x['music']['original']]
    audios = clean_audios_doubles(audios)
    if russian_only:
        audios = clean_audios_russian(audios=audios, include_original=include_original)
    if not include_unnamed:
        audios = clean_unnamed_audios(audios=audios)

    return audios


def get_video_count_from_tt_music_obj(music_obj):
    if isinstance(music_obj, dict) and 'stats' in music_obj.keys():
        stats = music_obj['stats']
        if isinstance(stats, dict) and 'videoCount' in stats.keys():
            return stats['videoCount']
