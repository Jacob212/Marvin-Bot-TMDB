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
