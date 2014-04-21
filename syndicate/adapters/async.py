"""
Syncronous adapter based on the 'tornado'.
"""

from __future__ import print_function, division

import functools
from syndicate.adapters import base
from tornado import httpclient
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


class AsyncAdapter(base.AdapterBase):

    def __init__(self, *args, **kwargs):
        config = kwargs.pop('config', {})
        self.client = httpclient.AsyncHTTPClient(**config)
        self.headers = {}
        super(AsyncAdapter, self).__init__(*args, **kwargs)

    def set_header(self, header, value):
        self.headers[header] = value

    def request(self, method, url, data=None, callback=None, query=None):
        if data is not None:
            data = self.serializer.encode(data)
        cb = functools.partial(self.on_request, callback)
        if query:
            url = '%s?%s' % (url, urlencode(query))
        return self.client.fetch(url, method=method, body=data, callback=cb,
                                 headers=self.headers)

    def on_request(self, callback, resp):
        """ Async handler for response to a fetch() call. """
        try:
            content = self.serializer.decode(resp.body)
        except Exception as e:
            error = e
            content = None
        else:
            error = None
        return base.Response(http_code=resp.code, headers=resp.headers,
                             content=content, error=error, extra=resp)

