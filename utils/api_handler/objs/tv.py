from ..base import _get_obj, _call, _get_url, _get_api_key

class TV():
    @staticmethod
    def details(tv_id):
        return _get_obj(_call('GET', f'{_get_url()}3/tv/{tv_id}?{_get_api_key()}&language=en-US'), key=None)

    @staticmethod
    def on_the_air(page=1):
        return _get_obj(_call('GET', f'{_get_url()}3/movie/on_the_air?{_get_api_key()}&language=en-US&page={str(page)}'))

    @staticmethod
    def latest():
        return _get_obj(_call('GET', f'{_get_url()}3/tv/latest?{_get_api_key()}&language=en-US'))
