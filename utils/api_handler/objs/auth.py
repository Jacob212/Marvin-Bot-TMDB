from ..base import _base

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
        return self._get_obj(self._call('DELETE', f'{self._url}4/auth/access_token', headers=headers, payload=payload), key=None
