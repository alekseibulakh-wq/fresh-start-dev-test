# fresh-start-dev-test
Synthetic test repository for Fresh Start development automation.

`health.py` exports `application(environ, start_response)`, a Python standard
library WSGI application that returns an iterable of bytes. No dependencies or
listening server are required.

- `GET /health` returns `200 OK` with `{"status":"ok"}`.
- Unknown paths return `404 Not Found` with `{"error":"not found"}`.
- Other methods on `/health` return `405 Method Not Allowed` with
  `{"error":"method not allowed"}` and `Allow: GET`.

All responses use `Content-Type: application/json` and a `Content-Length` matching
the response bytes. Paths match exactly; query strings do not affect routing.
Unknown paths return 404 regardless of the request method.

Invoke the application directly from the repository directory without binding a
network port:

```sh
python3 -B - <<'PY'
from wsgiref.util import setup_testing_defaults
from health import application

environ = {}
setup_testing_defaults(environ)
environ.update(REQUEST_METHOD="GET", PATH_INFO="/health")

def start_response(status, headers):
    print(status)
    print(headers)

print(b"".join(application(environ, start_response)).decode("utf-8"))
PY
```

Run the existing greeting tests and the direct WSGI response tests, then lint and
check the diff:

```sh
python3 -B -m unittest -v
/usr/local/lib/fresh-start/qa/bin/ruff check --no-cache --isolated --select E9,F .
git diff --check
```

The lint command uses the supplied QA tool; the application itself needs only
Python's standard library.

## Expanded CI
The existing required `unit-tests` check now runs lint, strict application type checking, all unit tests, real loopback HTTP integration tests, wheel/sdist build, installed-wheel smoke test, dependency audit (including CI tools), Bandit SAST and detect-secrets scanning of the checkout. Any failure fails the required job. CI uses hosted Ubuntu and read-only repository permission, with actions pinned to commits. No credentials or paid services are required.

Use Python 3.12 and install `requirements-ci.txt`, then run the commands in `.github/workflows/test.yml`. `mypy` and Bandit cover application code; tests are covered by lint and execution. Secret scanning covers current files, not Git history, and never prints matched values. There are no runtime dependencies or container images; container scanning is deferred until an image exists. Dependency versions need periodic maintenance; audit failure must be investigated rather than ignored.
