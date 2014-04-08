'''
Blocking client for REST apis.
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

    def __init__(self, uri=None, urn=None, auth=None, serializer='json',
                 data_getter=None, meta_getter=None, trailing_slash=True):
        if not (uri and urn):
            raise TypeError("Required: uri, urn")
        self.uri = uri
        self.urn = urn
        self.trailing_slash = trailing_slash
        self.url = '%s/%s' % (uri.strip('/'), urn.strip('/'))
        self.data_getter = data_getter
        self.meta_getter = meta_getter
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
        data = self.data_getter(root)
        if isinstance(data, dict):
            data = data.DictResponse(data)
        elif isinstance(root, list):
            data = data.ListResponse(data)
        else:
            return data
        meta = self.meta_getter(root)
        for mkey, mval in meta:
            setattr(data, mkey, mval)
        return data

    def do(self, method, *path, **query):
        path = tuple(x.strip('/') for x in path)
        if self.trailing_slash:
            path += ('',)
        d = self.session.request(method, '/'.join((self.url,) + path),
                                 params=query)
        d = self.serializer.decode(d.text)
        return self.import_filter(d)

    def get(self, *path, **query):
        return self.do('get', *path, **query)

    def get_pager(self, *path, **query):
        raise NotImplementedError()

    def post(self, method, *path, **query):
        raise NotImplementedError()

    def delete(self, method, *path, **query):
        raise NotImplementedError()

    def put(self, method, *path, **query):
        raise NotImplementedError()

    def patch(self, method, *path, **query):
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
