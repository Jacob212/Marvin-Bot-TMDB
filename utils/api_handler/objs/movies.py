from ..base import _base

class Movies(_base):
    def details(self, movie_id):
        return self._get_obj(self._call('GET', f'{self._url}3/movie/{movie_id}?api_key={self._api_key}&language=en-US'))

    def now_playing(self, page=1):
        return self._get_obj(self._call('GET', f'{self._url}3/movie/now_playing?api_key={self._api_key}&language=en-US&page={str(page)}'))

    def latest(self):
        return self._get_obj(self._call('GET', f'{self._url}3/movie/latest?api_key={self._api_key}&language=en-US'))