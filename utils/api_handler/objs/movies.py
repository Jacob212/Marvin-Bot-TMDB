from ..base import _base

class Movies(_base):
    def details(self, movie_id):
        return self._get_obj(self._call('GET', f'{self._url}3/movie/{movie_id}?api_key={self._api_key}&language=en-US'), key=None)

    def account_states(self, movie_id, session_id):
        return self._get_obj(self._call('GET', f'{self._url}3/movie/{movie_id}/account_states?api_key={self._api_key}'), key=None)

    def alternative_titles(self, movie_id):
        return self._get_obj(self._call('GET', f'{self._url}3/movie/{movie_id}/alternative_titles?api_key={self._api_key}'), key=None)

    def changes(self, movie_id):
        return self._get_obj(self._call('GET', f'{self._url}3/movie/{movie_id}/changes?api_key={self._api_key}'), key=None)

    def credits(self, movie_id):
        return self._get_obj(self._call('GET', f'{self._url}3/movie/{movie_id}/credits?api_key={self._api_key}'), key=None)

    def external_ids(self, movie_id):
        return self._get_obj(self._call('GET', f'{self._url}3/movie/{movie_id}/external_ids?api_key={self._api_key}'), key=None)

    def images(self, movie_id):
        return self._get_obj(self._call('GET', f'{self._url}3/movie/{movie_id}/images?api_key={self._api_key}'), key=None)

    def keywords(self, movie_id):
        return self._get_obj(self._call('GET', f'{self._url}3/movie/{movie_id}/keywords?api_key={self._api_key}'), key=None)

    def release_dates(self, movie_id):
        return self._get_obj(self._call('GET', f'{self._url}3/movie/{movie_id}/release_dates?api_key={self._api_key}'), key=None)

    def videos(self, movie_id):
        return self._get_obj(self._call('GET', f'{self._url}3/movie/{movie_id}/videos?api_key={self._api_key}'), key=None)

    def translations(self, movie_id):
        return self._get_obj(self._call('GET', f'{self._url}3/movie/{movie_id}/translations?api_key={self._api_key}'), key=None)

    def recommendations(self, movie_id, page=1):
        return self._get_obj(self._call('GET', f'{self._url}3/movie/{movie_id}/recommendations?api_key={self._api_key}&page={str(page)}'))

    def similar(self, movie_id, page=1):
        return self._get_obj(self._call('GET', f'{self._url}3/movie/{movie_id}/similar?api_key={self._api_key}&page={str(page)}'))

    def reviews(self, movie_id, page=1):
        return self._get_obj(self._call('GET', f'{self._url}3/movie/{movie_id}/reviews?api_key={self._api_key}&page={str(page)}'))

    def lists(self, movie_id, page=1):
        return self._get_obj(self._call('GET', f'{self._url}3/movie/{movie_id}/lists?api_key={self._api_key}&page={str(page)}'))

    def rating(self, movie_id, session_id):
        return self._get_obj(self._call('POST', f'{self._url}3/movie/{movie_id}/rating?api_key={self._api_key}'), key=None)

    def rating(self, movie_id, session_id):
        return self._get_obj(self._call('DELETE', f'{self._url}3/movie/{movie_id}/rating?api_key={self._api_key}'), key=None)

    def latest(self):
        return self._get_obj(self._call('GET', f'{self._url}3/movie/latest?api_key={self._api_key}&language=en-US'), key=None)

    def now_playing(self, page=1):
        return self._get_obj(self._call('GET', f'{self._url}3/movie/now_playing?api_key={self._api_key}&language=en-US&page={str(page)}'))

    def popular(self, page=1):
        return self._get_obj(self._call('GET', f'{self._url}3/movie/popular?api_key={self._api_key}&language=en-US&page={str(page)}'))

    def top_rated(self, page=1):
        return self._get_obj(self._call('GET', f'{self._url}3/movie/top_rated?api_key={self._api_key}&language=en-US&page={str(page)}'))

    def upcoming(self, page=1):
        return self._get_obj(self._call('GET', f'{self._url}3/movie/upcoming?api_key={self._api_key}&language=en-US&page={str(page)}'))
