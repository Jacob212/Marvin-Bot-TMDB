import requests
import time

f = open("api.txt","r")#Reads api and read access token needed to use the api
KEY = f.readline().strip("\n")
TOKEN = f.readline()
f.close()


class _base():
    def __init__(self):
        self._url = 'https://api.themoviedb.org/'
        self._remaining = 40
        self._reset = None
        self._api_key = KEY
        self._read_access_token = TOKEN

    # def _call(self, type, action, append_to_response):
    #   url = "%s%s?api_key=%s&%s&language=%s" % (self._url, action, self.api_key, append_to_response, self.language)

    #   req = requests.get(url)
    #   headers = req.headers

    #   if 'X-RateLimit-Remaining' in headers:
    #       self._remaining = int(headers['X-RateLimit-Remaining'])

    #   if 'X-RateLimit-Reset' in headers:
    #       self._reset = int(headers['X-RateLimit-Reset'])

    #   if self._remaining < 1:
    #       current_time = int(time.time())
    #       sleep_time = self._reset - current_time
    #       print("Rate limit reached. Sleeping for: %d" % sleep_time)
    #       time.sleep(abs(sleep_time))
    #       self._call(action, append_to_response)
                
    #   json = req.json()

    #   return json

    @staticmethod
    def _get_obj(result, key="results"):
        if 'success' in result and result['success'] is False:
            raise Exception(result['status_message'])
        arr = []
        if key is not None:
            [arr.append(_AsObj(**res)) for res in result[key]]
            
        else:
            return _AsObj(**result)
        if key == "results":
            result.pop(key)
            return arr,_AsObj(**result)
        return arr

    def _call(self, request_type, url, headers=None, payload=None):
        req = requests.request(request_type,url,data=payload,headers=headers)
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

class search(_base):
    def multi(self,query,page=1):
        return self._get_obj(self._call('GET',f'{self._url}3/search/multi?api_key={self._api_key}&language=en-US&include_adult=true&query="{query}"&page={str(page)}'))

class details(_base):
    def movie(self,movie_id):
        return _AsObj(**self._call('GET',f'{self._url}3/movie/{movie_id}?api_key={self._api_key}&language=en-US'))

    def tv(self,tv_id):
        return _AsObj(**self._call('GET',f'{self._url}3/tv/{tv_id}?api_key={self._api_key}&language=en-US'))

class auth(_base):
    def request(self):
        payload = "{\"redirect_to\":\"http://www.themoviedb.org/\"}"
        headers = {
            'authorization': f'Bearer {self._read_access_token}',
            'content-type': 'application/json;charset=utf-8'
        }
        return self._get_obj(self._call('POST',f'{self._url}4/auth/request_token',headers=headers,payload=payload), key=None)

    def access(self,request_token):
        payload = '{"request_token":"'+request_token+'"}'
        headers = {
            'authorization': f'Bearer {self._read_access_token}',
            'content-type': 'application/json;charset=utf-8'
        }
        return self._get_obj(self._call('POST',f'{self._url}4/auth/access_token',headers=headers,payload=payload), key=None)

    def delete(self,access_token):
        payload = '{"access_token":"'+access_token+'"}'
        headers = {
            'authorization': f'Bearer {self._read_access_token}',
            'content-type': 'application/json;charset=utf-8'
        }
        return self._get_obj(self._call('DELETE',f'{self._url}4/auth/access_token',headers=headers,payload=payload) ,key=None)

class lists(_base):
    def get(self,list_id,page=1):
        return self._get_obj(self._call('GET',f'{self._url}4/list/{list_id}?api_key={self._api_key}&page={page}&sort_by=title.asc'))

    def create(self,access_token):
        payload = "{\"name\":\"Watched - Marvin\",\"iso_639_1\":\"en\"}"
        headers = {
            'authorization': "Bearer "+access_token,
            'content-type': "application/json;charset=utf-8"
            }
        return _AsObj(**self._call('POST',f'{self._url}4/list',headers=headers,payload=payload))

    def add_items(self,list_id,access_token,payload):
        headers = {
            'authorization': f'Bearer {access_token}',
            'content-type': "application/json;charset=utf-8"
            }
        return self._get_obj(self._call('POST',f'{self._url}4/list/{list_id}/items',headers=headers,payload=payload))