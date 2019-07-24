import time
import os
import requests
import requests_cache

requests_cache.install_cache(cache_name='TMDB-cache', backend='sqlite', expire_after=3600)

def purge_cache():
    requests_cache.remove_expired_responses()

class _base():
    def __init__(self):
        self._url = 'https://api.themoviedb.org/'
        self._remaining = 40
        self._reset = None
        self._api_key = os.environ.get("TMDB_API_KEY")
        self._read_access_token = os.environ.get("TMDB_READ_ACCESS_TOKEN")

    @staticmethod
    def _get_obj(result, key="results"):
        if 'success' in result and result['success'] is False:
            raise Exception(result['status_message'])
        if key is None:
            return _AsObj(**result)

        arr = [_AsObj(**res) for res in result[key]]

        if key == "results":
            result.pop(key)
            return arr, _AsObj(**result)
        return arr

    def _call(self, request_type, url, headers=None, payload=None, disable_cache=None):
        if disable_cache:
            with requests_cache.disabled():
                req = requests.request(request_type, url, data=payload, headers=headers)
        else:
            req = requests.request(request_type, url, data=payload, headers=headers)
            print(f'Used cache: {req.from_cache}')
        headers = req.headers
        if 'X-RateLimit-Remaining' in headers:
            self._remaining = int(headers['X-RateLimit-Remaining'])

        if 'X-RateLimit-Reset' in headers:
            self._reset = int(headers['X-RateLimit-Reset'])

        if self._remaining < 1:
            current_time = int(time.time())
            sleep_time = self._reset - current_time
            print("Rate limit reached. Sleeping for: %d" % sleep_time)
            time.sleep(abs(sleep_time))
            self._call(request_type, url, headers, payload)

        json = req.json()

        return json

class _AsObj:
    def __init__(self, **entries):
        self.__dict__.update(entries)

class Search(_base):
    def multi(self, query, page=1):
        return self._get_obj(self._call('GET', f'{self._url}3/search/multi?api_key={self._api_key}&language=en-US&include_adult=true&query="{query}"&page={str(page)}'))

    def movie(self, query, page=1):
        return self._get_obj(self._call('GET', f'{self._url}3/search/movie?api_key={self._api_key}&language=en-US&include_adult=true&query="{query}"&page={str(page)}'))

    def tv(self, query, page=1):
        return self._get_obj(self._call('GET', f'{self._url}3/search/tv?api_key={self._api_key}&language=en-US&include_adult=true&query="{query}"&page={str(page)}'))

class Details(_base):
    def movie(self, movie_id):
        return _AsObj(**self._call('GET', f'{self._url}3/movie/{movie_id}?api_key={self._api_key}&language=en-US'))

    def tv(self, tv_id):
        return _AsObj(**self._call('GET', f'{self._url}3/tv/{tv_id}?api_key={self._api_key}&language=en-US'))

class Auth(_base):
    def request(self):
        payload = "{\"redirect_to\":\"http://www.themoviedb.org/\"}"
        headers = {
            'authorization': f'Bearer {self._read_access_token}',
            'content-type': 'application/json;charset=utf-8'
        }
        return self._get_obj(self._call('POST', f'{self._url}4/auth/request_token', headers=headers, payload=payload), key=None)

    def access(self, request_token):
        payload = '{"request_token":"'+request_token+'"}'
        headers = {
            'authorization': f'Bearer {self._read_access_token}',
            'content-type': 'application/json;charset=utf-8'
        }
        return self._get_obj(self._call('POST', f'{self._url}4/auth/access_token', headers=headers, payload=payload), key=None)

    def delete(self, access_token):
        payload = '{"access_token":"'+access_token+'"}'
        headers = {
            'authorization': f'Bearer {self._read_access_token}',
            'content-type': 'application/json;charset=utf-8'
        }
        return self._get_obj(self._call('DELETE', f'{self._url}4/auth/access_token', headers=headers, payload=payload), key=None)

class Lists(_base):
    def get(self, listID, sort="title.asc", page=1):
        return self._get_obj(self._call('GET', f'{self._url}4/list/{listID}?api_key={self._api_key}&page={page}&sort_by={sort}', disable_cache=True))

    def create(self, access_token):
        payload = "{\"name\":\"Watched - Marvin\", \"iso_639_1\":\"en\"}"
        headers = {
            'authorization': "Bearer "+access_token,
            'content-type': "application/json;charset=utf-8"
            }
        return _AsObj(**self._call('POST', f'{self._url}4/list', headers=headers, payload=payload))

    def delete(self, listID, access_token):
        headers = {
            'authorization': "Bearer "+access_token,
            'content-type': "application/json;charset=utf-8"
            }
        return _AsObj(**self._call('DELETE', f'{self._url}4/list{listID}', headers=headers))

    def add_items(self, listID, access_token, payload):
        headers = {
            'authorization': f'Bearer {access_token}',
            'content-type': "application/json;charset=utf-8"
            }
        return self._get_obj(self._call('POST', f'{self._url}4/list/{listID}/items', headers=headers, payload=payload))

    def update_items(self, listID, access_token, payload):
        headers = {
            'authorization': f'Bearer {access_token}',
            'content-type': "application/json;charset=utf-8"
            }
        return self._get_obj(self._call('PUT', f'{self._url}4/list/{listID}/items', headers=headers, payload=payload))

    def remove_items(self, listID, access_token, payload):
        headers = {
            'authorization': f'Bearer {access_token}',
            'content-type': "application/json;charset=utf-8"
            }
        return self._get_obj(self._call('DELETE', f'{self._url}4/list/{listID}/items', headers=headers, payload=payload))
