'''
Client for REST APIs.
'''

from __future__ import print_function, division

import functools
from syndicate import data as m_data
from syndicate.adapters import sync as m_sync, async as m_async


class ServiceError(Exception):
    pass


class ResponseError(ServiceError):

    def __init__(self, response):
        self.response = response

    def __str__(self):
        return '%s(%s)' % (type(self).__name__, self.response)


class Service(object):
    """ A stateful connection to a service. """

    default_page_size = 100

    @staticmethod
    def default_data_getter(response):
        content = response.content
        if not content['success']:
            raise ResponseError(content)
        return content['data']

    @staticmethod
    def default_meta_getter(response):
        content = response.content
        return content['meta']

    @staticmethod
    def default_next_page_getter(response):
        content = response.content
        return content['meta']['next']

    def __init__(self, uri=None, urn=None, auth=None, serializer='json',
                 data_getter=None, meta_getter=None, next_page_getter=None,
                 trailing_slash=True, async=False, adapter=None):
        if not (uri and urn):
            raise TypeError("Required: uri, urn")
        self.auth = auth
        self.uri = uri.rstrip('/')
        self.urn = urn
        self.filters = []
        self.trailing_slash = trailing_slash
        self.data_getter = data_getter or self.default_data_getter
        self.meta_getter = meta_getter or self.default_meta_getter
        self.next_page_getter = next_page_getter or \
                                self.default_next_page_getter
        if hasattr(serializer, 'mime'):
            self.serializer = serializer
        else:
            self.serializer = m_data.serializers[serializer]
        if adapter is None:
            if async:
                adapter = m_async.AsyncAdapter()
            else:
                adapter = m_sync.SyncAdapter()
        self.bind_adapter(adapter)

    def bind_adapter(self, adapter):
        adapter.set_header('accept', self.serializer.mime)
        adapter.ingress_filter = self.ingress_filter
        adapter.serializer = self.serializer
        adapter.auth = self.auth
        self.adapter = adapter

    def ingress_filter(self, response):
        """ Flatten a response with meta and data keys into an single object
        where the values in the meta dict are converted to attrs. """
        data = self.data_getter(response)
        if isinstance(data, dict):
            data = m_data.DictResponse(data)
        elif isinstance(data, list):
            data = m_data.ListResponse(data)
            data.next_page = self.next_page_getter(response)
        else:
            return data
        meta = self.meta_getter(response)
        for mkey, mval in meta.items():
            setattr(data, mkey, mval)
        return data

    def do(self, method, path, urn=None, callback=None, **query):
        path = tuple(x.strip('/') for x in path)
        if path and self.trailing_slash:
            path += ('',)
        urn = self.urn if urn is None else urn
        url = '%s/%s' % (self.uri, urn.strip('/'))
        return self.adapter.request(method, '/'.join((url,) + path),
                                    callback=callback, query=query)

    def get(self, *path, **query):
        return self.do('get', path, **query)

    def get_pager(self, *path, **query):
        page_arg = query.pop('page_size', None)
        limit_arg = query.pop('limit', None)
        page_size = page_arg or limit_arg or self.default_page_size
        page = self.get(*path, limit=page_size, **query)
        for x in page:
            yield x
        while page.next_page:
            page = self.get(urn=page.next_page)
            for x in page:
                yield x

    def post(self, method, *path, **query):
        raise NotImplementedError()

    def delete(self, method, *path, **query):
        raise NotImplementedError()

    def put(self, *path, **query):
        raise NotImplementedError()

    def patch(self, *path, **query):
        raise NotImplementedError()


class Resource(dict):
    """ Extended dictionary format that makes future operations on this object
    more object-mapper like. """

    def do(self, method, *path, **query):
        """ XXX: Debatable existence. """
        raise NotImplementedError()

    def fetch(self, method, *path, **query):
        """ Get a subresource. """
        raise NotImplementedError()

    def save(self):
        raise NotImplementedError()

    def delete(self, method, *path, **query):
        raise NotImplementedError()
