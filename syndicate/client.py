'''
Client for REST APIs.
'''

from __future__ import print_function, division

import collections
from syndicate import data as m_data
from syndicate.adapters import sync as m_sync, async as m_async
from tornado import concurrent


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
        if response.error:
            raise response.error
        content = response.content
        if not content['success']:
            raise ResponseError(content)
        return content['data']

    @staticmethod
    def default_meta_getter(response):
        content = response.content
        return content['meta']

    def __init__(self, uri=None, urn=None, auth=None, serializer='json',
                 data_getter=None, meta_getter=None, trailing_slash=True,
                 async=False, adapter=None):
        if not (uri and urn):
            raise TypeError("Required: uri, urn")
        self.async = async
        self.auth = auth
        self.filters = []
        self.trailing_slash = trailing_slash
        self.uri = uri.rstrip('/')
        self.urn = urn
        self.data_getter = data_getter or self.default_data_getter
        self.meta_getter = meta_getter or self.default_meta_getter
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
        """ A generator for all the results a resource can provide. The pages
        are lazily loaded. """
        fn = self.get_pager_async if self.async else self.get_pager_sync
        page_arg = query.pop('page_size', None)
        limit_arg = query.pop('limit', None)
        query['limit'] = page_arg or limit_arg or self.default_page_size
        return fn(path=path, query=query)

    def get_pager_sync(self, path=None, query=None):
        page = self.get(*path, **query)
        for x in page:
            yield x
        while page.meta['next']:
            page = self.get(urn=page.meta['next'])
            for x in page:
                yield x

    def get_pager_async(self, path=None, query=None):
        return AsyncPager(getter=self.get, path=path, query=query)

    def post(self, method, *path, **query):
        raise NotImplementedError()

    def delete(self, method, *path, **query):
        raise NotImplementedError()

    def put(self, *path, **query):
        raise NotImplementedError()

    def patch(self, *path, **query):
        raise NotImplementedError()


class AsyncPager(object):

    max_overflow = 1000

    def __init__(self, getter=None, path=None, query=None):
        self.mark = 0
        self.active = None
        self.waiting = collections.deque()
        self.getter = getter
        self.path = path
        self.query = query
        self.stop = False
        self.next_page = None

    def __iter__(self):
        return self

    def __next__(self):
        item = concurrent.Future()
        self.queue_next(item)
        return item

    next = __next__

    def queue_next_page(self):
        if self.next_page:
            self.active = self.getter(urn=self.next_page)
        else:
            self.active = self.getter(*self.path, **self.query)
        self.active.add_done_callback(self.on_next_page)

    def queue_next(self, item):
        if len(self.waiting) >= self.max_overflow:
            raise OverflowError('max overflow exceeded')
        if self.active:
            if self.active.done():
                if self.active.result():
                    item.set_result(self.active.result().pop(0))
                elif self.stop:
                    raise StopIteration()
                else:
                    self.waiting.append(item)
                    self.queue_next_page()
            else:
                self.waiting.append(item)
        else:
            self.waiting.append(item)
            self.queue_next_page()

    def on_next_page(self, page):
        res = page.result()
        self.next_page = res.meta['next']
        self.stop = not self.next_page
        while self.waiting and res:
            self.waiting.popleft().set_result(res.pop(0))
        if self.waiting:
            if self.stop:
                while self.waiting:
                    self.waiting.popleft().set_exception(StopIteration())
            else:
                self.queue_next_page()


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
