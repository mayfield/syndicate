"""
Interface(s) for adapters subclasses.  Eventually common authentication
should find its way here.
"""

import collections

Response = collections.namedtuple('Response', ('http_code', 'headers',
                                  'content', 'error', 'extra'))


class AdapterBase(object):
    """ Adapter interface.  Must subclass. """

    def __init__(self, connect_timeout=None, request_timeout=None,
                 serializer=None, auth=None, ingress_filter=None):
        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        self.serializer = serializer
        self.auth = auth
        self.ingress_filter = ingress_filter

    def set_header(self, header, value):
        """ Set a header that will be included in every HTTP request. """
        raise NotImplementedError('pure virtual method')

    def get_header(self, header):
        """ Examine a header that would be included in every HTTP request. """
        raise NotImplementedError('pure virtual method')

    def set_cookie(self, cookie, value):
        """ Set a session cookie. """
        raise NotImplementedError('pure virtual method')

    def get_cookie(self, cookie):
        """ Examine a cookie morsel. """
        raise NotImplementedError('pure virtual method')

    def request(self, method, url, data=None, callback=None, query=None):
        raise NotImplementedError('pure virtual method')


class AdapterPager(object):
    """ A sized generator that iterators over API pages. """

    def __init__(self, getter, path, kwargs):
        self.getter = getter
        self.path = path
        self.kwargs = kwargs
        super().__init__()

    def __len__(self):
        raise NotImplementedError("pure virtual")
