"""
Syncronous adapter based on the 'requests' library.
"""

from __future__ import print_function, division

import json
import requests
from syndicate.adapters import base


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
    """ Auth where you need to perform an arbitrary "login" to get a cookie.
    The expectation is that the args to this constructor can be used to
    perform a request that generates the required cookie(s) for a valid
    session. """

    content_type = 'application/json'

    def __init__(self, *args, **kwargs):
        headers = {
            'content-type': self.content_type
        }
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
        kwargs['headers'] = headers
        if 'data' in kwargs:
            kwargs['data'] = self.serializer(kwargs['data'])
        self.req_args = args
        self.req_kwargs = kwargs
        self.tried = False

    def __call__(self, request):
        if not self.tried:
            login = requests.request(*self.req_args, **self.req_kwargs)
            self.check_login_response(login)
            request.prepare_cookies(login.cookies)
            self.tried = True
        return request

    def check_login_response(self, response):
        pass

    def serializer(self, data):
        return json.dumps(data)


class SyncAdapter(base.AdapterBase):

    def __init__(self, *args, **kwargs):
        config = kwargs.pop('config', {})
        self.session = requests.Session(**config)
        super(SyncAdapter, self).__init__(*args, **kwargs)

    def set_header(self, header, value):
        self.session.headers[header] = value

    def request(self, method, url, data=None, callback=None, query=None):
        if data is not None:
            data = self.serializer.encode(data)
        resp = self.session.request(method, url, data=data, params=query)
        try:
            content = self.serializer.decode(resp.content)
        except Exception as e:
            error = e
            content = None
        else:
            error = None
        r =base.Response(http_code=resp.status_code, headers=resp.headers,
                         content=content, error=error, extra=resp)
        return callback(r)