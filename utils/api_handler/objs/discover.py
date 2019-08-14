from ..base import _base

class Discover(_base):
    def movie(self, page=1):
        return self._get_obj(self._call('GET', f'{self._url}3/discover/movie?api_key={self._api_key}&language=en-US&page={str(page)}'))

    def tv(self, page=1):
        return self._get_obj(self._call('GET', f'{self._url}3/discover/tv?api_key={self._api_key}&language=en-US&page={str(page)}'))

    # def multi(self, page=1): not a feature of the api
    #     return self._get_obj(self._call('GET', f'{self._url}3/discover/multi?api_key={self._api_key}&language=en-US&page={str(page)}'))
