"""Dependency-free WSGI application for a synthetic health endpoint."""

import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from _typeshed.wsgi import StartResponse


def application(environ: dict[str, Any], start_response: "StartResponse") -> list[bytes]:
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
