import logging
import functools
try:
    from urllib2 import urlopen, HTTPError, Request
except ImportError:
    # for Python 3
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError

from .base import RequestsBase

__all__ = ("Urllib2Client",)

logger = logging.getLogger("arango.urllib")


def safe_request(func):
    """
    Handle 404 errors and so on
    """
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HTTPError as e:
            content = e.read()
            e.close()
            return RequestsBase.build_response(
                e.code, e.msg, e.headers, content)

    return wrap


class Urllib2Client(RequestsBase):

    """
    If no PyCURL bindings available or
    client forced by hands. Quite useful for PyPy.
    """
    _config = {}
    encoding = "utf-8"
    headers = {}

    def updateauth(self, req):
        if self.headers.get('Authorization', None):
            req.add_header('Authorization', self.headers['Authorization'])

    def config(self, encoding=None, **kwargs):
        self._config.update(kwargs)

        if encoding is not None:
            self.encoding = encoding

    def parse_response(self, r, content=None):
        headers = {}

        if "dict" in r.headers.__dict__:
            headers.update(r.headers.__dict__["dict"])
        else:
            # Python3
            headers.update(dict(r.headers.raw_items()))

        content = content.decode(self.encoding)
        return self.build_response(r.code, r.msg, headers, content)

    @safe_request
    def get(self, url, **kwargs):
        req = Request(url)
        self.updateauth(req)
        response = urlopen(req)
        content = response.read()
        response.close()
        return self.parse_response(response, content=content)

    @safe_request
    def post(self, url, data=None):
        if data is None:
            data = ""

        req = Request(url)
        self.updateauth(req)
        req.add_header('Content-Type', 'application/json')
        req.add_data(data.encode(self.encoding))

        response = urlopen(req, **self._config)
        content = response.read()
        response.close()

        return self.parse_response(response, content=content)

    @safe_request
    def put(self, url, data=None):
        if data is None:
            data = ""

        req = Request(url)
        self.updateauth(req)
        req.add_header('Content-Type', 'application/json')
        req.add_data(data.encode(self.encoding))
        req.get_method = lambda: "put"
        response = urlopen(req)

        content = response.read()
        response.close()

        return self.parse_response(response, content=content)

    @safe_request
    def delete(self, url, data=None):
        req = Request(url)
        self.updateauth(req)
        req.get_method = lambda: "delete"
        response = urlopen(req)
        content = response.read()
        response.close()

        return self.parse_response(response, content=content)
