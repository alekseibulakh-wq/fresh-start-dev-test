"""Dependency-free WSGI application for a synthetic health endpoint."""

import json


def application(environ, start_response):
    """Return a JSON response without opening a network connection."""
    extra_headers = []
    if environ.get("PATH_INFO") != "/health":
        status = "404 Not Found"
        payload = {"error": "not found"}
    elif environ.get("REQUEST_METHOD") != "GET":
        status = "405 Method Not Allowed"
        payload = {"error": "method not allowed"}
        extra_headers.append(("Allow", "GET"))
    else:
        status = "200 OK"
        payload = {"status": "ok"}

    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    headers = [
        ("Content-Type", "application/json"),
        ("Content-Length", str(len(body))),
    ]
    start_response(status, headers + extra_headers)
    return [body]
