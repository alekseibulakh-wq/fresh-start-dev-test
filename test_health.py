"""Exercise the WSGI application directly, without a listening server."""

import json
import unittest
from wsgiref.util import setup_testing_defaults

from health import application


class HealthTests(unittest.TestCase):
    def assert_response(self, method, path, status, body, payload, allow=None,
                        query=""):
        environ = {}
        setup_testing_defaults(environ)
        environ.update(REQUEST_METHOD=method, PATH_INFO=path, QUERY_STRING=query)
        calls = []

        def start_response(response_status, headers, exc_info=None):
            calls.append((response_status, headers, exc_info))

        response = application(environ, start_response)
        try:
            chunks = list(response)
        finally:
            if hasattr(response, "close"):
                response.close()

        for chunk in chunks:
            self.assertIsInstance(chunk, bytes)
        actual_body = b"".join(chunks)
        self.assertEqual(actual_body, body)
        self.assertEqual(json.loads(actual_body), payload)
        self.assertEqual(len(calls), 1)
        actual_status, headers, exc_info = calls[0]
        self.assertEqual(actual_status, status)
        self.assertIsNone(exc_info)
        expected_headers = [
            ("Content-Type", "application/json"),
            ("Content-Length", str(len(actual_body))),
        ]
        if allow is not None:
            expected_headers.append(("Allow", allow))
        self.assertCountEqual(headers, expected_headers)

    def test_get_health(self):
        self.assert_response("GET", "/health", "200 OK", b'{"status":"ok"}',
                             {"status": "ok"})

    def test_query_does_not_change_health_route(self):
        self.assert_response("GET", "/health", "200 OK", b'{"status":"ok"}',
                             {"status": "ok"}, query="probe=synthetic")

    def test_unknown_paths(self):
        for path in ("", "/", "/missing", "/health/", "/Health", "/health/live"):
            for method in ("GET", "POST"):
                with self.subTest(path=path, method=method):
                    self.assert_response(
                        method, path, "404 Not Found", b'{"error":"not found"}',
                        {"error": "not found"},
                    )

    def test_other_methods(self):
        for method in ("HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS",
                       "TRACE", "CONNECT", "CUSTOM", "get"):
            with self.subTest(method=method):
                self.assert_response(
                    method, "/health", "405 Method Not Allowed",
                    b'{"error":"method not allowed"}',
                    {"error": "method not allowed"}, allow="GET",
                )


if __name__ == "__main__":
    unittest.main()
