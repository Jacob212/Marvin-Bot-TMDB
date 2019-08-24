from ..base import _get_obj, _call, _get_url, _get_api_key

class Movies():
    @staticmethod
    def details(movie_id):
        return _get_obj(_call('GET', f'{_get_url()}3/movie/{movie_id}?{_get_api_key()}&language=en-US'), key=None)

    @staticmethod
    def account_states(movie_id, session_id):
        return _get_obj(_call('GET', f'{_get_url()}3/movie/{movie_id}/account_states?{_get_api_key()}'), key=None)

    @staticmethod
    def alternative_titles(movie_id):
        return _get_obj(_call('GET', f'{_get_url()}3/movie/{movie_id}/alternative_titles?{_get_api_key()}'), key=None)

    @staticmethod
    def changes(movie_id):
        return _get_obj(_call('GET', f'{_get_url()}3/movie/{movie_id}/changes?{_get_api_key()}'), key=None)

    @staticmethod
    def credits(movie_id):
        return _get_obj(_call('GET', f'{_get_url()}3/movie/{movie_id}/credits?{_get_api_key()}'), key=None)

    @staticmethod
    def external_ids(movie_id):
        return _get_obj(_call('GET', f'{_get_url()}3/movie/{movie_id}/external_ids?{_get_api_key()}'), key=None)

    @staticmethod
    def images(movie_id):
        return _get_obj(_call('GET', f'{_get_url()}3/movie/{movie_id}/images?{_get_api_key()}'), key=None)

    @staticmethod
    def keywords(movie_id):
        return _get_obj(_call('GET', f'{_get_url()}3/movie/{movie_id}/keywords?{_get_api_key()}'), key=None)

    @staticmethod
    def release_dates(movie_id):
        return _get_obj(_call('GET', f'{_get_url()}3/movie/{movie_id}/release_dates?{_get_api_key()}'), key=None)

    @staticmethod
    def videos(movie_id):
        return _get_obj(_call('GET', f'{_get_url()}3/movie/{movie_id}/videos?{_get_api_key()}'), key=None)

    @staticmethod
    def translations(movie_id):
        return _get_obj(_call('GET', f'{_get_url()}3/movie/{movie_id}/translations?{_get_api_key()}'), key=None)

    @staticmethod
    def recommendations(movie_id, page=1):
        return _get_obj(_call('GET', f'{_get_url()}3/movie/{movie_id}/recommendations?{_get_api_key()}&page={str(page)}'))

    @staticmethod
    def similar(movie_id, page=1):
        return _get_obj(_call('GET', f'{_get_url()}3/movie/{movie_id}/similar?{_get_api_key()}&page={str(page)}'))

    @staticmethod
    def reviews(movie_id, page=1):
        return _get_obj(_call('GET', f'{_get_url()}3/movie/{movie_id}/reviews?{_get_api_key()}&page={str(page)}'))

    @staticmethod
    def lists(movie_id, page=1):
        return _get_obj(_call('GET', f'{_get_url()}3/movie/{movie_id}/lists?{_get_api_key()}&page={str(page)}'))

    @staticmethod
    def rate(movie_id, session_id):
        return _get_obj(_call('POST', f'{_get_url()}3/movie/{movie_id}/rating?{_get_api_key()}'), key=None)

    @staticmethod
    def rating(movie_id, session_id):
        return _get_obj(_call('DELETE', f'{_get_url()}3/movie/{movie_id}/rating?{_get_api_key()}'), key=None)

    @staticmethod
    def latest():
        return _get_obj(_call('GET', f'{_get_url()}3/movie/latest?{_get_api_key()}&language=en-US'), key=None)

    @staticmethod
    def now_playing(page=1):
        return _get_obj(_call('GET', f'{_get_url()}3/movie/now_playing?{_get_api_key()}&language=en-US&page={str(page)}'))

    @staticmethod
    def popular(page=1):
        return _get_obj(_call('GET', f'{_get_url()}3/movie/popular?{_get_api_key()}&language=en-US&page={str(page)}'))

    @staticmethod
    def top_rated(page=1):
        return _get_obj(_call('GET', f'{_get_url()}3/movie/top_rated?{_get_api_key()}&language=en-US&page={str(page)}'))

    @staticmethod
    def upcoming(page=1):
        return _get_obj(_call('GET', f'{_get_url()}3/movie/upcoming?{_get_api_key()}&language=en-US&page={str(page)}'))
