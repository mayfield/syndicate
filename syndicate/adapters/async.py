"""
Asyncronous adapter using the 'tornado' engine.
"""

from __future__ import print_function, division

import functools
import json
import sys
from syndicate.adapters import base
from tornado import httpclient, concurrent, gen
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


class AsyncAdapter(base.AdapterBase):

    def __init__(self, *args, **kwargs):
        config = kwargs.pop('config', {})
        self.client = httpclient.AsyncHTTPClient(**config)
        self.headers = {}
        self.request_timeout = None
        self.connect_timeout = None
        super(AsyncAdapter, self).__init__(*args, **kwargs)

    def set_header(self, header, value):
        self.headers[header] = value

    def request(self, method, url, data=None, query=None, callback=None,
                timeout=None):
        user_result = concurrent.TracebackFuture()
        if callback is not None:
            user_result.add_done_callback(callback)
        if data is not None:
            data = self.serializer.encode(data)
        if query:
            url = '%s?%s' % (url, urlencode(query, doseq=True))
        timeout = self.request_timeout if timeout is None else timeout
        request = httpclient.HTTPRequest(url, method=method.upper(),
                                         body=data, headers=self.headers,
                                         request_timeout=timeout,
                                         connect_timeout=self.connect_timeout)
        start = lambda f: self.start_request(f, request, user_result)
        self.authenticate(request).add_done_callback(start)
        return user_result

    def authenticate(self, request):
        f = None
        if callable(self.auth):
            f = self.auth(request)
        elif self.auth is not None:
            request.auth_username, request.auth_password = self.auth
        if f is None:
            # TODO: Replace with gen.maybe_future in tornado 3.3
            f = concurrent.Future()
            f.set_result(None)
        return f

    def start_request(self, auth_result, request, user_result):
        if auth_result.exception():
            concurrent.chain_future(auth_result, user_result)
            return
        try:
            f = self.client.fetch(request)
        except Exception:
            user_result.set_exc_info(sys.exc_info())
        else:
            cb = functools.partial(self.on_request_done, user_result)
            f.add_done_callback(cb)

    def on_request_done(self, user_result, fetch_result):
        """ Finally parse the result and run the user's callback. """
        if fetch_result.exception():
            concurrent.chain_future(fetch_result, user_result)
        else:
            native_resp = fetch_result.result()
            content = None
            try:
                if native_resp.body and len(native_resp.body):
                    content = self.serializer.decode(native_resp.body.decode())
            except Exception:
                user_result.set_exc_info(sys.exc_info())
            else:
                resp = base.Response(http_code=native_resp.code,
                                     headers=native_resp.headers,
                                     content=content, error=None,
                                     extra=native_resp)
                user_result.set_result(self.ingress_filter(resp))


class LoginAuth(object):
    """ Auth where you need to perform an arbitrary "login" to get a cookie.
    The expectation is that the args to this constructor can be used to
    perform a request that generates the required cookie(s) for a valid
    session. """

    content_type = 'application/json'
    OK_HTTP_CODES = 200, 201

    def __init__(self, url, method='POST', **kwargs):
        headers = {
            'content-type': self.content_type
        }
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
        kwargs['headers'] = headers
        if 'data' in kwargs:
            kwargs['body'] = self.serializer(kwargs.pop('data'))
        self.url = url
        self.method = method
        self.req_kwargs = kwargs
        self.login = None

    @gen.coroutine
    def __call__(self, request):
        if not self.login:
            http = httpclient.AsyncHTTPClient()
            self.login = http.fetch(self.url, method=self.method.upper(),
                                    **self.req_kwargs)
        response = yield self.login
        self.check_login_response()
        request.headers['cookie'] = response.headers['set-cookie']

    def check_login_response(self):
        if self.login.result().code not in self.OK_HTTP_CODES:
            raise Exception('login failed')

    def serializer(self, data):
        return json.dumps(data)


class HeaderAuth(object):
    """ A simple header based auth.  Instantiate this with header name and
    value arguments for a single header or with a dictionary of name/value
    pairs. """

    def __init__(self, header_or_headers_dict, value=None):
        if hasattr(header_or_headers_dict, 'items'):
            self.headers = header_or_headers_dict.copy()
        else:
            self.headers = {header_or_headers_dict: value}

    def __call__(self, request):
        request.headers.update(self.headers)
