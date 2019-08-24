from ..base import _get_obj, _call, _get_url, _get_api_key

class Lists():
    @staticmethod
    def get(list_id, sort="title.asc", page=1):
        return _get_obj(_call('GET', f'{_get_url()}4/list/{list_id}?{_get_api_key()}&page={page}&sort_by={sort}', disable_cache=True))

    @staticmethod
    def create(access_token):
        payload = "{\"name\":\"Watched - Marvin\", \"iso_639_1\":\"en\"}"
        headers = {
            'authorization': "Bearer "+access_token,
            'content-type': "application/json;charset=utf-8"
            }
        return _get_obj(_call('POST', f'{_get_url()}4/list', headers=headers, payload=payload), key=None)

    @staticmethod
    def delete(list_id, access_token):
        headers = {
            'authorization': "Bearer "+access_token,
            'content-type': "application/json;charset=utf-8"
            }
        return _get_obj(_call('DELETE', f'{_get_url()}4/list{list_id}', headers=headers), key=None)

    @staticmethod
    def add_items(list_id, access_token, payload):
        headers = {
            'authorization': f'Bearer {access_token}',
            'content-type': "application/json;charset=utf-8"
            }
        return _get_obj(_call('POST', f'{_get_url()}4/list/{list_id}/items', headers=headers, payload=payload))

    @staticmethod
    def update_items(list_id, access_token, payload):
        headers = {
            'authorization': f'Bearer {access_token}',
            'content-type': "application/json;charset=utf-8"
            }
        return _get_obj(_call('PUT', f'{_get_url()}4/list/{list_id}/items', headers=headers, payload=payload))

    @staticmethod
    def remove_items(list_id, access_token, payload):
        headers = {
            'authorization': f'Bearer {access_token}',
            'content-type': "application/json;charset=utf-8"
            }
        return _get_obj(_call('DELETE', f'{_get_url()}4/list/{list_id}/items', headers=headers, payload=payload))
