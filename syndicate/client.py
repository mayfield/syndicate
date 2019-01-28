'''
Client for REST APIs.
'''

import re
from . import data as m_data
from .adapters import aio as aio_adapter
from .adapters import requests as requests_adapter


class ServiceError(Exception):
    pass


class ResponseError(ServiceError):

    def __init__(self, response):
        self.response = response
        super().__init__()

    def __str__(self):
        return '%s(%s)' % (type(self).__name__, self.response)


class Service(object):
    """ A stateful connection to a service. """

    default_page_size = 100
    urlpartition = re.compile('([?;])')

    @staticmethod
    def default_data_getter(response):
        if response.error:
            raise response.error
        content = response.content
        if not content:
            return None
        if not content['success']:
            raise ResponseError(content)
        return content.get('data')

    @staticmethod
    def default_meta_getter(response):
        content = response.content
        if not content:
            return None
        return content.get('meta')

    def __init__(self, uri=None, urn='', auth=None, serializer='json',
                 data_getter=None, meta_getter=None, trailing_slash=True,
                 aio=False, **adapter_config):
        if not uri:
            raise TypeError("Required: uri")
        if 'async' in adapter_config:
            raise TypeError("Invalid argument: `async` is now reserved; "
                            "Use `aio` instead")
        self.closing = False
        self.aio = aio
        self.auth = auth
        self.filters = []
        self.trailing_slash = trailing_slash
        self.uri = uri
        self.urn = urn
        self.data_getter = data_getter or self.default_data_getter
        self.meta_getter = meta_getter or self.default_meta_getter
        if hasattr(serializer, 'mime'):
            self.serializer = serializer
        else:
            self.serializer = m_data.serializers[serializer]
        self.adapter = self.make_adapter(ingress_filter=self.ingress_filter,
                                         serializer=self.serializer,
                                         auth=self.auth, aio=aio,
                                         **adapter_config)

    def make_adapter(self, aio=False, **config):
        if 'async' in config:
            raise TypeError("Invalid argument: `async` is now reserved; "
                            "Use `aio` instead")
        Adapter = aio_adapter.AioAdapter if aio else \
                  requests_adapter.RequestsAdapter
        a = Adapter(**config)
        a.set_header('accept', self.serializer.mime)
        a.set_header('content-type', self.serializer.mime)
        return a

    def ingress_filter(self, response):
        """ Flatten a response with meta and data keys into an object. """
        data = self.data_getter(response)
        if isinstance(data, dict):
            data = m_data.DictResponse(data)
        elif isinstance(data, list):
            data = m_data.ListResponse(data)
        else:
            return data
        data.meta = self.meta_getter(response)
        return data

    def do(self, method, path, urn=None, callback=None, data=None,
           timeout=None, **query):
        urlparts = [self.uri, self.urn if urn is None else urn]
        urlparts.extend(path)
        url = '/'.join(filter(None, (x.strip('/') for x in urlparts)))
        if self.trailing_slash:
            parts = self.urlpartition.split(url, 1)
            if not parts[0].endswith('/'):
                parts[0] += '/'
                url = ''.join(parts)
        return self.adapter.request(method, url, callback=callback, data=data,
                                    query=query, timeout=timeout)

    def get(self, *path, **kwargs):
        return self.do('get', path, **kwargs)

    def get_pager(self, *path, **kwargs):
        """ A generator for all the results a resource can provide. The pages
        are lazily loaded. """
        page_arg = kwargs.pop('page_size', None)
        limit_arg = kwargs.pop('limit', None)
        kwargs['limit'] = page_arg or limit_arg or self.default_page_size
        return self.adapter.get_pager(self.get, path, kwargs)

    def post(self, *path_and_data, **kwargs):
        path = list(path_and_data)
        data = path.pop(-1)
        return self.do('post', path, data=data, **kwargs)

    def delete(self, *path, **kwargs):
        data = kwargs.pop('data', None)
        return self.do('delete', path, data=data, **kwargs)

    def put(self, *path_and_data, **kwargs):
        path = list(path_and_data)
        data = path.pop(-1)
        return self.do('put', path, data=data, **kwargs)

    def patch(self, *path_and_data, **kwargs):
        path = list(path_and_data)
        data = path.pop(-1)
        return self.do('patch', path, data=data, **kwargs)

    def close(self):
        if self.closing or self.adapter is None:
            return
        self.closing = True
        adapter = self.adatper
        self.adapter = None
        return adapter.close()
