"""Exercise real loopback HTTP requests through the standard WSGI server."""
import http.client
import json
import threading
import unittest
from wsgiref.simple_server import WSGIRequestHandler, make_server

from health import application


class QuietHandler(WSGIRequestHandler):
    def log_message(self, format, *args):
        pass


class HTTPIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = make_server("127.0.0.1", 0, application, handler_class=QuietHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)
        if cls.thread.is_alive():
            raise AssertionError("HTTP server did not stop")

    def test_http_contract(self):
        cases = [
            ("GET", "/health", 200, {"status": "ok"}),
            ("GET", "/health?probe=1", 200, {"status": "ok"}),
            ("GET", "/missing", 404, {"error": "not found"}),
            ("POST", "/health", 405, {"error": "method not allowed"}),
        ]
        for method, path, status, payload in cases:
            with self.subTest(method=method, path=path):
                connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
                try:
                    connection.request(method, path)
                    response = connection.getresponse()
                    body = response.read()
                    self.assertEqual(response.status, status)
                    self.assertEqual(json.loads(body), payload)
                    self.assertEqual(response.getheader("Content-Type"), "application/json")
                    self.assertEqual(int(response.getheader("Content-Length")), len(body))
                    if status == 405:
                        self.assertEqual(response.getheader("Allow"), "GET")
                finally:
                    connection.close()
