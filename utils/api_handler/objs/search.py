from ..base import _base

class Search(_base):
    def keywords(self, query, page=1):
        return self._get_obj(self._call('GET', f'{self._url}3/search/keyword?api_key={self._api_key}&query="{query}"&page={str(page)}'))

    def movie(self, query, page=1):
        return self._get_obj(self._call('GET', f'{self._url}3/search/movie?api_key={self._api_key}&language=en-US&include_adult=true&query="{query}"&page={str(page)}'))

    def multi(self, query, page=1):
        return self._get_obj(self._call('GET', f'{self._url}3/search/multi?api_key={self._api_key}&language=en-US&include_adult=true&query="{query}"&page={str(page)}'))

    def people(self, query, page=1):
        return self._get_obj(self._call('GET', f'{self._url}3/search/person?api_key={self._api_key}&language=en-US&include_adult=true&query="{query}"&page={str(page)}'))

    def tv(self, query, page=1):
        return self._get_obj(self._call('GET', f'{self._url}3/search/tv?api_key={self._api_key}&language=en-US&include_adult=true&query="{query}"&page={str(page)}'))
