from ..base import _base

class Lists(_base):
    def get(self, list_id, sort="title.asc", page=1):
        return self._get_obj(self._call('GET', f'{self._url}4/list/{list_id}?api_key={self._api_key}&page={page}&sort_by={sort}', disable_cache=True))

    def create(self, access_token):
        payload = "{\"name\":\"Watched - Marvin\", \"iso_639_1\":\"en\"}"
        headers = {
            'authorization': "Bearer "+access_token,
            'content-type': "application/json;charset=utf-8"
            }
        return self._get_obj(self._call('POST', f'{self._url}4/list', headers=headers, payload=payload), key=None)

    def delete(self, list_id, access_token):
        headers = {
            'authorization': "Bearer "+access_token,
            'content-type': "application/json;charset=utf-8"
            }
        return self._get_obj(self._call('DELETE', f'{self._url}4/list{list_id}', headers=headers), key=None)

    def add_items(self, list_id, access_token, payload):
        headers = {
            'authorization': f'Bearer {access_token}',
            'content-type': "application/json;charset=utf-8"
            }
        return self._get_obj(self._call('POST', f'{self._url}4/list/{list_id}/items', headers=headers, payload=payload))

    def update_items(self, list_id, access_token, payload):
        headers = {
            'authorization': f'Bearer {access_token}',
            'content-type': "application/json;charset=utf-8"
            }
        return self._get_obj(self._call('PUT', f'{self._url}4/list/{list_id}/items', headers=headers, payload=payload))

    def remove_items(self, list_id, access_token, payload):
        headers = {
            'authorization': f'Bearer {access_token}',
            'content-type': "application/json;charset=utf-8"
            }
        return self._get_obj(self._call('DELETE', f'{self._url}4/list/{list_id}/items', headers=headers, payload=payload))
