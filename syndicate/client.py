'''
Blocking client for REST apis.
'''

from __future__ import print_function, division

import requests
from . import serialization


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

    def __init__(self, host=None, urn=None, auth=None, serializer='json'):
        if not (host and urn):
            raise TypeError("Required: host, urn")
        self.session = requests.Session()
        if hasattr(serializer, 'mime'):
            self.serializer = serializer
        else:
            self.serializer = serialization.serializers[serializer]
        self.session.headers['accept'] = self.serializer.mime
        self.session.auth = auth

    def do(self, method, *path, **query):
        raise NotImplementedError()

    def get(self, *path, **query):
        path = (x.strip('/') for x in path)
        return self.session.get('/'.join(self.url, *path), params=query)

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
