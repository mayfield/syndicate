"""
Asyncronous adapter using the `asyncio` and `aiohttp`.
This code requires Python 3.4 or newer.
"""

import aiohttp
import asyncio
import collections
import functools
import json
import platform
from syndicate.adapters import base


def monkey_patch_issue_25593():
    """ Workaround for http://bugs.python.org/issue25593 """
    save = asyncio.selector_events.BaseSelectorEventLoop._sock_connect_cb

    @functools.wraps(save)
    def patched(instance, fut, sock, address):
        if not fut.done():
            save(instance, fut, sock, address)
    asyncio.selector_events.BaseSelectorEventLoop._sock_connect_cb = patched

if platform.python_version() <= '3.5.0':
    monkey_patch_issue_25593()


class AioAdapter(base.AdapterBase):

    def __init__(self, loop=None, session_config=None, connector_config=None,
                 **config):
        super().__init__(**config)
        if loop is None:
            loop = asyncio.get_event_loop()
        self.loop = loop
        c = aiohttp.TCPConnector(loop=loop, **(connector_config or {}))
        timeout = aiohttp.ClientTimeout(connect=self.connect_timeout)
        self.session = aiohttp.ClientSession(connector=c, timeout=timeout,
                                             **(session_config or {}))
        self.headers = {}

    def set_header(self, header, value):
        self.headers[header] = value

    def get_header(self, header):
        return self.headers[header]

    def set_cookie(self, cookie, value):
        self.session.cookie_jar.update_cookies({cookie: value})

    def get_cookie(self, cookie):
        for x in self.session.cookie_jar:
            if x.key == cookie:
                return x.value
        raise KeyError(cookie)

    def get_pager(self, *args, **kwargs):
        return AioPager(*args, **kwargs)

    async def request(self, method, url, data=None, query=None, callback=None,
                timeout=None):
        if data is not None:
            data = self.serializer.encode(data)
        if timeout is None:
            timeout = self.request_timeout
        await self.authenticate()
        params = []
        for key, values in query.items():
            if not isinstance(values, str):
                try:
                    params.extend((key, str(val)) for val in values)
                except TypeError:
                    pass
                else:
                    continue
            params.append((key, str(values)))
        r = self.session.request(method, url, data=data, headers=self.headers,
                                 params=params)
        result = await asyncio.wait_for(r, timeout, loop=self.loop)
        body = await result.read()
        content = body and self.serializer.decode(body.decode())
        resp = base.Response(http_code=result.status, headers=result.headers,
                             content=content, error=None, extra=result)
        final_resp = self.ingress_filter(resp)
        if callback is not None:
            callback(final_resp)
        return final_resp

    async def authenticate(self):
        if callable(self.auth):
            await self.auth()

    async def close(self):
        await self.session.close()


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
            kwargs['data'] = self.serializer(kwargs.pop('data'))
        self.url = url
        self.method = method
        self.req_kwargs = kwargs
        self.login = None

    async def __call__(self, request):
        if not self.login:
            with aiohttp.ClientSession() as http:
                self.login = http.request(self.method, self.url,
                                          **self.req_kwargs)
        response = await self.login
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


class AioPager(base.AdapterPager):

    max_overflow = 1000

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mark = 0
        self.active = None
        self.waiting = collections.deque()
        self.stop = False
        self.next_page = None

    def __iter__(self):
        return self

    def __next__(self):
        item = asyncio.Future()
        self.queue_next(item)
        return item

    next = __next__

    def queue_next_page(self):
        if self.next_page:
            self.active = self.getter(urn=self.next_page)
        else:
            self.active = self.getter(*self.path, **self.kwargs)
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

pager_class = AioPager  # For public reference
