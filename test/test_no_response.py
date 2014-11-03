from unittest import mock
from unittest import TestCase


class TestAsyncAdapter204Response(TestCase):
    def _run_test(self, http_code, body=None):
        resp_mock = mock.MagicMock(**{
            "code": mock.PropertyMock(),
            "headers": mock.PropertyMock(),
            "body": mock.PropertyMock()
        })
        resp_mock.code = http_code
        resp_mock.headers = None
        resp_mock.body = body

        fetch_mock = mock.MagicMock(**{
            "exception.return_value": False,
            "result.return_value": resp_mock
        })

        user_result = mock.MagicMock()
        with mock.patch('tornado.httpclient.AsyncHTTPClient'):
            from syndicate.adapters.async import AsyncAdapter
            adapter = AsyncAdapter()
            def filter(obj):
                return obj
            adapter.ingress_filter = filter
            adapter.on_request_done(user_result, fetch_mock)
            from syndicate.adapters.base import Response

            r = Response(http_code=http_code, headers=None,
                          content=None, error=None, extra=resp_mock)
            user_result.set_result.assert_called_once_with(r)

    def test_204_response(self):
        self._run_test(204)

    def test_no_response(self):
        self._run_test(200, b"")


class TestSyncAdapter204Response(TestCase):
    def _run_test(self, http_code, body=None):
        response_mock = mock.MagicMock(**{
            "status_code": mock.PropertyMock(),
            "content": mock.PropertyMock(),
        })
        response_mock.status_code = http_code
        response_mock.content = body
        session_mock = mock.MagicMock(**{
            "request.return_value": response_mock
        })
        with mock.patch('requests.Session', return_value=session_mock):
            from syndicate.adapters.sync import SyncAdapter

            adapter = SyncAdapter()
            def filter(obj):
                return obj

            adapter.ingress_filter = filter
            result = adapter.request('DELETE', url='/foo/')
            self.assertEqual(result.http_code, http_code)
            self.assertIsNone(result.error)
            self.assertIsNone(result.content)
            return result

    def test_204_response(self):
        self._run_test(204)

    def test_empty_response(self):
        self._run_test(200, b"")


class TestClient204Response(TestCase):
    def test_client_service_204_default_data_getter(self):
        from syndicate.adapters.base import Response

        r = Response(http_code=204, headers=None,
                          content=None, error=None, extra=None)

        from syndicate.client import Service
        s = Service(uri='http://test', urn="/api/v1")

        value = s.default_data_getter(r)
        self.assertIsNone(value)

    def test_client_service_204_default_meta_getter(self):
        from syndicate.adapters.base import Response

        r = Response(http_code=204, headers=None,
                          content=None, error=None, extra=None)

        from syndicate.client import Service
        s = Service(uri='http://test', urn="/api/v1")

        value = s.default_meta_getter(r)
        self.assertIsNone(value)
