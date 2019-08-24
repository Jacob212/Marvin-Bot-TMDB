from ..base import _get_obj, _call, _get_url, _get_read_access_token

class Auth():
    @staticmethod
    def request():
        payload = "{\"redirect_to\":\"http://www.themoviedb.org/\"}"
        headers = {
            'authorization': f'Bearer {_get_read_access_token()}',
            'content-type': 'application/json;charset=utf-8'
        }
        return _get_obj(_call('POST', f'{_get_url()}4/auth/request_token', headers=headers, payload=payload), key=None)

    @staticmethod
    def access(request_token):
        payload = '{"request_token":"'+request_token+'"}'
        headers = {
            'authorization': f'Bearer {_get_read_access_token()}',
            'content-type': 'application/json;charset=utf-8'
        }
        return _get_obj(_call('POST', f'{_get_url()}4/auth/access_token', headers=headers, payload=payload), key=None)

    @staticmethod
    def delete(access_token):
        payload = '{"access_token":"'+access_token+'"}'
        headers = {
            'authorization': f'Bearer {_get_read_access_token()}',
            'content-type': 'application/json;charset=utf-8'
        }
        return _get_obj(_call('DELETE', f'{_get_url()}4/auth/access_token', headers=headers, payload=payload), key=None)
