"""
Sanity tests for the syndicate library.
"""

from __future__ import print_function, division

import datetime
import io
import syndicate
import unittest
from tornado import httpclient


class BaseTest(unittest.TestCase):

    def test_service_construct(self):
        self.assertRaises(TypeError, syndicate.Service)
        syndicate.Service(uri='foo', urn='bar')

    def test_json_serializer(self):
        input_ = {
            "duck": {
                "talk": "Quack!",
                "walk": 0.001,
                "is_duck": True,
                "born": datetime.datetime.utcnow()
            }
        }
        data = syndicate.serializers['json'].encode(input_)
        output = syndicate.serializers['json'].decode(data)
        self.assertEqual(input_, output)


class MockAsyncClient(object):

    def __init__(self, data_callback=None):
        self.data_callback = data_callback

    def fetch(self, url, method=None, body=None, callback=None, headers=None):
        buf = io.StringIO(self.data_callback())
        req = httpclient.HTTPRequest(url, method=method, headers=headers)
        resp = httpclient.HTTPResponse(req, 200, buffer=buf)
        return callback(resp)


class AdapterTest(unittest.TestCase):

    def test_async_adapter(self):
        test = lambda: u'ABC'
        s = syndicate.Service(uri='john', urn='belushi', async=True)
        s.adapter.client = MockAsyncClient(data_callback=test)
        assert s.get('foo')
