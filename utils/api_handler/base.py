import time
import os
import requests
import requests_cache

requests_cache.install_cache(cache_name='TMDB-cache', backend='sqlite', expire_after=3600)
os.environ["remaining"] = "40"


def purge_cache():
    requests_cache.remove_expired_responses()

def _get_api_key():
    return f'api_key={os.environ.get("TMDB_API_KEY")}'

def _get_url():
    return "https://api.themoviedb.org/"

def _get_read_access_token():
    return os.environ.get("TMDB_READ_ACCESS_TOKEN")

def _get_obj(result, key="results"):
    if "success" in result and result["success"] is False:
        raise Exception(result["status_message"])
    if key is None:
        return _AsObj(**result)

    arr = [_AsObj(**res) for res in result[key]]

    if key == "results":
        result.pop(key)
        return arr, _AsObj(**result)
    return arr

def _call(request_type, url, headers=None, payload=None, disable_cache=None):
    if disable_cache:
        with requests_cache.disabled():
            req = requests.request(request_type, url, data=payload, headers=headers)
    else:
        req = requests.request(request_type, url, data=payload, headers=headers)
    headers = req.headers
    if "X-RateLimit-Remaining" in headers:
        os.environ["remaining"] = headers["X-RateLimit-Remaining"]

    if "X-RateLimit-Reset" in headers:
        os.environ["reset"] = headers["X-RateLimit-Reset"]

    if int(os.environ.get("remaining")) < 1:
        current_time = int(time.time())
        sleep_time = int(os.environ.get("reset")) - current_time
        print("Rate limit reached. Sleeping for: %d" % sleep_time)
        time.sleep(abs(sleep_time))
        _call(request_type, url, headers, payload)

    json = req.json()

    return json

class _AsObj:
    def __init__(self, **entries):
        self.__dict__.update(entries)
