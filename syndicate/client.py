'''
Client for REST apis.
'''

from __future__ import print_function, division

import requests
from . import data


class HeaderAuth(requests.auth.AuthBase):
    """ A simple header based auth.  Instantiate this with the header key/value
    needed by the target API. """

    def __init__(self, header, value):
        self.header = header
        self.value = value

    def __call__(self, request):
        request.headers[self.header] = self.value
        return request


class LoginAuth(requests.auth.AuthBase):
    """ Auth where you need to perform an arbitrary "login" to get a cookie. """

    def __init__(self, *args, **kwargs):
        self.req_args = args
        self.req_kwargs = kwargs

    def __call__(self, request):
        print("doing a thing?")
        request.session.request(*self.req_args, **self.req_kwargs)
        return request


class Service(object):
    """ A stateful connection to a service. """

    @staticmethod
    def default_data_getter(x):
        return x['data']

    @staticmethod
    def default_meta_getter(x):
        return x['meta']

    @staticmethod
    def default_next_page_getter(x):
        return x['meta']['next']

    def __init__(self, uri=None, urn=None, auth=None, serializer='json',
                 data_getter=None, meta_getter=None, next_page_getter=None,
                 trailing_slash=True):
        if not (uri and urn):
            raise TypeError("Required: uri, urn")
        self.uri = uri.rstrip('/')
        self.urn = urn
        self.trailing_slash = trailing_slash
        self.data_getter = data_getter or self.default_data_getter
        self.meta_getter = meta_getter or self.default_meta_getter
        self.next_page_getter = next_page_getter or self.default_next_page_getter
        self.session = requests.Session()
        if hasattr(serializer, 'mime'):
            self.serializer = serializer
        else:
            self.serializer = data.serializers[serializer]
        self.session.headers['accept'] = self.serializer.mime
        self.session.auth = auth

    def import_filter(self, root):
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
        return result

    def do(self, method, path, urn=None, **query):
        path = tuple(x.strip('/') for x in path)
        if path and self.trailing_slash:
            path += ('',)
        urn = self.urn if urn is None else urn
        url = '%s/%s' % (self.uri, urn.strip('/'))
        d = self.session.request(method, '/'.join((url,) + path),
                                 params=query)
        d = self.serializer.decode(d.text)
        return self.import_filter(d)

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

    def post(self, *path, **query):
        raise NotImplementedError()

    def delete(self, *path, **query):
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
