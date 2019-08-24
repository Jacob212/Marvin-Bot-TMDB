from ..base import _get_obj, _call, _get_url, _get_api_key

class Genres():
    @staticmethod
    def movie():
        return _get_obj(_call('GET', f'{_get_url()}3/genre/movie/list?{_get_api_key()}&language=en-US'), key=None)

    @staticmethod
    def tv():
        return _get_obj(_call('GET', f'{_get_url()}3/genre/tv/list?{_get_api_key()}&language=en-US'), key=None)
