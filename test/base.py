"""
Sanity tests for the syndicate library.
"""

import datetime
import syndicate
import syndicate.adapters.aio as aio_adapter
import syndicate.adapters.requests as requests_adapter
import syndicate.data
import unittest


class BaseTest(unittest.TestCase):

    def notest_service_construct(self):
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
        data = syndicate.data.serializers['json'].encode(input_)
        output = syndicate.data.serializers['json'].decode(data)
        self.assertEqual(input_, output)


class AuthTests(unittest.TestCase):

    def request(self):
        class Request(object): pass
        r = Request()
        r.headers = {}
        return r

    def test_header_auth_single(self):
        for Auth in (requests_adapter.HeaderAuth, aio_adapter.HeaderAuth):
            request = self.request()
            auth = Auth("foo", "bar")
            auth(request)
            self.assertEqual(request.headers, {'foo': 'bar'})
            auth = Auth("bar", "foo")
            auth(request)
            self.assertEqual(request.headers, {'foo': 'bar', 'bar': 'foo'})

    def test_header_auth_multi(self):
        for Auth in (requests_adapter.HeaderAuth, aio_adapter.HeaderAuth):
            request = self.request()
            auth = Auth({"foo": "bar"})
            auth(request)
            self.assertEqual(request.headers, {'foo': 'bar'})
            auth = Auth({"bar": "foo"})
            auth(request)
            self.assertEqual(request.headers, {'foo': 'bar', 'bar': 'foo'})
            auth = Auth({"foo": "replace"})
            auth(request)
            self.assertEqual(request.headers, {'foo': 'replace', 'bar': 'foo'})


class URLTests(unittest.TestCase):

    valid_path_signatures = {
        (): '%s',
        ('',): '%s',
        ('', ''): '%s',
        ('one', ''): '%s/one',
        ('', 'one'): '%s/one',
        ('', 'one', ''): '%s/one',
        ('/', 'one', ''): '%s/one',
        ('/one', '', ''): '%s/one',
        ('/one',): '%s/one',
        ('/one/',): '%s/one',
        ('one/',): '%s/one',
        ('one',): '%s/one',
        ('one', '/two'): '%s/one/two',
        ('one', '/two/'): '%s/one/two',
        ('one', 'two/'): '%s/one/two',
        ('one/', '/two'): '%s/one/two',
        ('/one/', '/two/'): '%s/one/two',
        # ('//foo//one/', '/two/'): '%s/one/two',  # TODO support this.
    }

    def snoop_request(self, service, snoop_callback):
        service.adapter.request = lambda m, url, **na: snoop_callback(url)

    def clean_url_filter(self, url):
        scheme, sep, uri = url.partition('://')
        self.assertEqual(scheme, 'https')
        self.assertEqual(sep, '://')  # ?
        self.assertNotIn('//', uri)
        return uri

    def test_uri_and_urn_slash_collapse(self):
        uri = 'tld/urn'
        for tld in ('tld', 'tld/'):
            for urn in ('urn', 'urn/', '/urn', '/urn/'):
                s = syndicate.Service(uri='https://%s' % tld, urn=urn)
                self.snoop_request(s, self.clean_url_filter)
                for args, valid_fmt in self.valid_path_signatures.items():
                    self.assertEqual(s.get(*args), (valid_fmt % uri) + '/')
                s = syndicate.Service(uri='https://%s' % tld, urn=urn, trailing_slash=False)
                self.snoop_request(s, self.clean_url_filter)
                for args, valid_fmt in self.valid_path_signatures.items():
                    self.assertEqual(s.get(*args), valid_fmt % uri)

    def test_no_urn(self):
        uri = 'tld'
        for tld in ('tld', 'tld/'):
            s = syndicate.Service(uri='https://%s' % tld)
            self.snoop_request(s, self.clean_url_filter)
            for args, valid_fmt in self.valid_path_signatures.items():
                self.assertEqual(s.get(*args), (valid_fmt % uri) + '/')
            s = syndicate.Service(uri='https://%s' % tld, trailing_slash=False)
            self.snoop_request(s, self.clean_url_filter)
            for args, valid_fmt in self.valid_path_signatures.items():
                self.assertEqual(s.get(*args), valid_fmt % uri)

    def test_slashes_with_hidden_query(self):
        s = syndicate.Service(uri='https://tld/')
        self.snoop_request(s, self.clean_url_filter)
        self.assertEqual(s.get('foo?hide=me'), 'tld/foo/?hide=me')
        self.assertEqual(s.get(urn='foo?hide=me'), 'tld/foo/?hide=me')
