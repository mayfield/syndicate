"""
Interface(s) for adapters subclasses.  Eventually common authentication
should find its way here.
"""

from __future__ import print_function, division

import collections


Response = collections.namedtuple('Response', ('http_code', 'headers',
                                  'content', 'error', 'extra'))


class AdapterBase(object):
    """ Adapter interface.  Must subclass. """

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
