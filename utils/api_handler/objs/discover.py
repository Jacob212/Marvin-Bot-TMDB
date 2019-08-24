from ..base import _get_obj, _call, _get_url, _get_api_key

class Discover():
    @staticmethod
    def movie(options, page=1):
        query_string = ""
        for value, key in options.items():
            query_string += f'{value}={key}&'
        return _get_obj(_call('GET', f'{_get_url()}3/discover/movie?{_get_api_key()}&{query_string}sort_by=popularity.desc&language=en-US&page={str(page)}'))

    @staticmethod
    def tv(options, page=1):
        query_string = ""
        for value, key in options.items():
            query_string += f'{value}={key}&'
        return _get_obj(_call('GET', f'{_get_url()}3/discover/tv?{_get_api_key()}&{query_string}sort_by=popularity.desc&language=en-US&page={str(page)}'))
