from copy import deepcopy
from TikTokApi import TikTokApi
from TikTokApi.exceptions import TikTokNotAvailableError, JSONDecodeFailure
from .utils import get_audios_from_tiktoks, get_video_count_from_tt_music_obj


class TikTok(TikTokApi):

    def _get_audio_stats(self, audio_id, n_try=0):
        if n_try > 10:
            return 0
        try:
            music_obj = self.get_music_object_full_by_api(id=audio_id)
            if music_obj:
                return get_video_count_from_tt_music_obj(music_obj=music_obj)
            if not music_obj and n_try < 5:
                return self._get_audio_stats(audio_id=audio_id, n_try=n_try+1)
        except (KeyError, TikTokNotAvailableError, JSONDecodeFailure):
            return self._get_audio_stats(audio_id=audio_id, n_try=n_try+1)

    def get_audios_from_trends(self, count=30, include_original=False, russian_only=True, include_unnamed=False,
                               n_try=0):
        if n_try > 10:
            return []
        count = count if count < 2000 else 2000
        try:
            tiktoks = self.by_trending(count=count)
        except KeyError:
            return self.get_audios_from_trends(count=count,
                                               include_original=include_original,
                                               russian_only=russian_only,
                                               include_unnamed=include_unnamed,
                                               n_try=n_try+1)
        return get_audios_from_tiktoks(tiktoks=tiktoks,
                                       include_original=include_original,
                                       russian_only=russian_only,
                                       include_unnamed=include_unnamed)

    def get_audio_stats(self, audios):
        if isinstance(audios, dict):
            audios = [audios]

        audios_with_stats = []
        len_audios = len(audios)
        for n, audio in enumerate(audios):
            stats = self._get_audio_stats(audio_id=audio['audio_id'] if 'audio_id' in audio.keys() else audio['id'])
            audio = deepcopy(audio)
            audio['videos_count'] = stats
            audios_with_stats.append(audio)
            if 'artist' in audio.keys():
                print(f'Update stats: {n + 1} / {len_audios} \t | \t {audio["artist"]} - {audio["title"]}')
            else:
                print(f'Collect stats: {n + 1} / {len_audios} \t | \t {audio["authorName"]} - {audio["title"]}')

        return audios_with_stats

    def get_audio_from_tiktok(self, tiktok_url, n_try=0):
        if n_try > 10:
            return
        try:
            tiktok = self.get_tiktok_by_url(url=tiktok_url)
        except KeyError:
            return self.get_audio_from_tiktok(tiktok_url=tiktok_url)
        except Exception:
            return
        if isinstance(tiktok, dict) and 'itemInfo' in tiktok.keys():
            item_info = tiktok['itemInfo']
            if isinstance(item_info, dict) and 'itemStruct' in item_info.keys():
                item = item_info['itemStruct']
                if isinstance(item, dict) and 'music' in item.keys():
                    audio = item['music']
                    if isinstance(audio, dict):
                        return audio
