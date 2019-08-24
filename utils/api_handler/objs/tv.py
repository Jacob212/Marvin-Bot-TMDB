from ..base import _base

class TV(_base):
    def details(self, tv_id):
        return self._get_obj(self._call('GET', f'{self._url}3/tv/{tv_id}?api_key={self._api_key}&language=en-US'), key=None)

    def account_states(self, tv_id, session_id):
        return self._get_obj(self._call('GET', f'{self._url}3/tv/{tv_id}?api_key={self._api_key}&language=en-US'), key=None)

    def alternative_titles(self, tv_id):
        return self._get_obj(self._call('GET', f'{self._url}3/tv/{tv_id}?api_key={self._api_key}&language=en-US'), key=None)

    def changes(self, tv_id, start_date, end_date):
        return self._get_obj(self._call('GET', f'{self._url}3/tv/{tv_id}?api_key={self._api_key}&language=en-US'), key=None)

    def content_ratings(self, tv_id):
        return self._get_obj(self._call('GET', f'{self._url}3/tv/{tv_id}?api_key={self._api_key}&language=en-US'), key=None)

    def credits(self, tv_id):
        return self._get_obj(self._call('GET', f'{self._url}3/tv/{tv_id}?api_key={self._api_key}&language=en-US'), key=None)

    def episode_groups(self, tv_id):
        return self._get_obj(self._call('GET', f'{self._url}3/tv/{tv_id}?api_key={self._api_key}&language=en-US'))

    def external_ids(self, tv_id):
        return self._get_obj(self._call('GET', f'{self._url}3/tv/{tv_id}?api_key={self._api_key}&language=en-US'), key=None)

    def images(self, tv_id):
        return self._get_obj(self._call('GET', f'{self._url}3/tv/{tv_id}?api_key={self._api_key}&language=en-US'), key=None)

    def keywords(self, tv_id):
        return self._get_obj(self._call('GET', f'{self._url}3/tv/{tv_id}?api_key={self._api_key}&language=en-US'), key=None)

    def recommendations(self, tv_id):
        return self._get_obj(self._call('GET', f'{self._url}3/tv/{tv_id}?api_key={self._api_key}&language=en-US'), key=None)

    def reviews(self, tv_id):
        return self._get_obj(self._call('GET', f'{self._url}3/tv/{tv_id}?api_key={self._api_key}&language=en-US'), key=None)

    def screened_theatrically(self, tv_id):
        return self._get_obj(self._call('GET', f'{self._url}3/tv/{tv_id}?api_key={self._api_key}&language=en-US'), key=None)

    def similar(self, tv_id):
        return self._get_obj(self._call('GET', f'{self._url}3/tv/{tv_id}?api_key={self._api_key}&language=en-US'), key=None)

    def translations(self, tv_id):
        return self._get_obj(self._call('GET', f'{self._url}3/tv/{tv_id}?api_key={self._api_key}&language=en-US'), key=None)

    def videos(self, tv_id):
        return self._get_obj(self._call('GET', f'{self._url}3/tv/{tv_id}?api_key={self._api_key}&language=en-US'), key=None)

    def rate(self, tv_id):
        return self._get_obj(self._call('POST', f'{self._url}3/tv/{tv_id}?api_key={self._api_key}&language=en-US'), key=None)

    def delete_rating(self, tv_id):
        return self._get_obj(self._call('DELETE', f'{self._url}3/tv/{tv_id}?api_key={self._api_key}&language=en-US'), key=None)

    def latest(self):
        return self._get_obj(self._call('GET', f'{self._url}3/tv/latest?api_key={self._api_key}&language=en-US'))

    def airing_today(self, page=1):
        return self._get_obj(self._call('GET', f'{self._url}3/tv/{tv_id}?api_key={self._api_key}&language=en-US'))

    def on_the_air(self, page=1):
        return self._get_obj(self._call('GET', f'{self._url}3/movie/on_the_air?api_key={self._api_key}&language=en-US&page={str(page)}'))

    def popular(self, tv_id):
        return self._get_obj(self._call('GET', f'{self._url}3/tv/{tv_id}?api_key={self._api_key}&language=en-US'), key=None)

    def top_rated(self, tv_id):
        return self._get_obj(self._call('GET', f'{self._url}3/tv/{tv_id}?api_key={self._api_key}&language=en-US'), key=None)





