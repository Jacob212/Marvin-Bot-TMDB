from ..base import _get_obj, _call, _get_url, _get_api_key

class Search():
    @staticmethod
    def keywords(query, page=1):
        return _get_obj(_call('GET', f'{_get_url()}3/search/keyword?{_get_api_key()}&query="{query}"&page={str(page)}'))

    @staticmethod
    def movie(query, page=1):
        return _get_obj(_call('GET', f'{_get_url()}3/search/movie?{_get_api_key()}&language=en-US&include_adult=true&query="{query}"&page={str(page)}'))

    @staticmethod
    def multi(query, page=1):
        return _get_obj(_call('GET', f'{_get_url()}3/search/multi?{_get_api_key()}&language=en-US&include_adult=true&query="{query}"&page={str(page)}'))

    @staticmethod
    def people(query, page=1):
        return _get_obj(_call('GET', f'{_get_url()}3/search/person?{_get_api_key()}&language=en-US&include_adult=true&query="{query}"&page={str(page)}'))

    @staticmethod
    def tv(query, page=1):
        return _get_obj(_call('GET', f'{_get_url()}3/search/tv?{_get_api_key()}&language=en-US&include_adult=true&query="{query}"&page={str(page)}'))
