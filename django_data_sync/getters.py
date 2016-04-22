from datetime import datetime

from connection_manager.connection import RemoteConnection


class GetterMixin(object):

    def __init__(self, app_model):
        self.app_model = app_model


class APIMixin(GetterMixin):

    def __init__(self, app_model, **kwargs):
        super(APIMixin, self).__init__(app_model)
        self._connection = kwargs.get('connection')
        self._request_result = None

    def set_connection(self, connection_info=None):
        if self._connection:
            return
        if connection_info is None:
            connection_info = {}
        self._connection = RemoteConnection(connection_info)

    @property
    def connection(self):
        if self._connection is None:
            self.set_connection(self.app_model.get_elements_data.get('connection_info', {}))
        return self._connection

    @property
    def request_result(self):
        return self._request_result


class APIJson(APIMixin):

    def get_elements(self, **kwargs):
        request_kwargs = kwargs.get('request_kwargs', {})

        if kwargs.get('auto_date', True) and self.app_model.last_sync_date:
            request_kwargs.setdefault('params', {})
            request_kwargs['params'].update(
                {'last_edit_date_from':
                     self.app_model.last_sync_date.strftime('%Y-%m-%dT%H:%M:%S.%f')})

        self._request_result = \
            self.connection.request('GET', self.app_model.get_elements_data['data_url'],
                                    **request_kwargs)
        return self._request_result.json()
