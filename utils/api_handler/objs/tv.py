from ..base import _base

class TV(_base):
    def details(self, tv_id):
        return self._get_obj(self._call('GET', f'{self._url}3/tv/{tv_id}?api_key={self._api_key}&language=en-US'), key=None)

    def on_the_air(self, page=1):
        return self._get_obj(self._call('GET', f'{self._url}3/movie/on_the_air?api_key={self._api_key}&language=en-US&page={str(page)}'))

    def latest(self):
        return self._get_obj(self._call('GET', f'{self._url}3/tv/latest?api_key={self._api_key}&language=en-US'))
