from ..base import _base

class Genres(_base):
    def movie(self):
        return self._get_obj(self._call('GET', f'{self._url}3/genre/movie/list?api_key={self._api_key}&language=en-US'), key=None)

    def tv(self):
        return self._get_obj(self._call('GET', f'{self._url}3/genre/tv/list?api_key={self._api_key}&language=en-US'), key=None)
