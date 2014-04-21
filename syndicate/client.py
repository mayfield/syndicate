'''
Client for REST APIs.
'''

from __future__ import print_function, division

import functools
from syndicate import data
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

    @staticmethod
    def default_data_getter(x):
        if x['success']:
            return x['data']
        else:
            raise ResponseError(x)

    @staticmethod
    def default_meta_getter(x):
        return x['meta']

    @staticmethod
    def default_next_page_getter(x):
        return x['meta']['next']

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
            self.serializer = data.serializers[serializer]
        if adapter is None:
            if async:
                adapter = m_async.AsyncAdapter()
            else:
                adapter = m_sync.SyncAdapter()
        self.bind_adapter(adapter)

    def bind_adapter(self, adapter):
        adapter.set_header('accept', self.serializer.mime)
        adapter.serializer = self.serializer
        adapter.auth = self.auth
        self.adapter = adapter

    def import_filter(self, callback, root):
        """ Flatten a response with meta and data keys into an single object
        where the values in the meta dict are converted to attrs. """
        result = self.data_getter(root)
        if isinstance(result, dict):
            result = data.DictResponse(result)
        elif isinstance(result, list):
            result = data.ListResponse(result)
            result.next_page = self.next_page_getter(root)
        else:
            return result
        meta = self.meta_getter(root)
        for mkey, mval in meta.items():
            setattr(result, mkey, mval)
        return callback(result)

    def do(self, method, path, urn=None, callback=None, **query):
        path = tuple(x.strip('/') for x in path)
        if path and self.trailing_slash:
            path += ('',)
        urn = self.urn if urn is None else urn
        url = '%s/%s' % (self.uri, urn.strip('/'))
        cb = functools.partial(self.import_filter, callback)
        return self.adapter.request(method, '/'.join((url,) + path),
                                    callback=cb, query=query)

    def get(self, *path, **query):
        return self.do('get', path, **query)

    def get_pager(self, *path, **query):
        page = self.get(*path, **query)
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
