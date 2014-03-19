try:
    import StringIO
except ImportError:
    # python3
    from io import StringIO

import pycurl

from .base import RequestsBase

__all__ = ("PyCurlClient",)

CONTINUE_HEADER = "HTTP/1.1 100 (Continue)"


def performer(func):
    """
    Decorator to simplify work with PyCURL
    """
    def wrap(cls, *args, **kwargs):
        client, buf = func(cls, *args, **kwargs)
        return PyCurlClient.build_response(*PyCurlClient.perform(client, buf))
    return wrap


class PyCurlClient(RequestsBase):

    """
    PyCURL-based HTTP client
    """
    DEBUG = False
    IPRESOLVE = pycurl.IPRESOLVE_V4

    encoding = "utf-8"
    headers = {}

    def client(self, url):
        pc = pycurl.Curl()

        buf = StringIO.StringIO()

        if self.DEBUG:
            pc.setopt(pycurl.VERBOSE, True)

        # TODO: do not attempt to connect via IPv6
        # XXX: NEED TO BE CONFIGURABLE!!!
        pc.setopt(pycurl.IPRESOLVE, self.IPRESOLVE)
        pc.setopt(pycurl.URL, url)
        pc.setopt(pycurl.HEADER, 1)
        pc.setopt(pycurl.NOSIGNAL, 1)
        pc.setopt(pycurl.WRITEFUNCTION, buf.write)
        if self.headers.get('Authorization', None):
            pc.setopt(
                pycurl.HTTPHEADER, ['Authorization: ' + self.headers['Authorization']])
        return pc, buf

    @classmethod
    def perform(cls, client, buf):
        client.perform()
        client.close()

        return cls.parse_response(buf)

    @classmethod
    def parse_response(cls, buf):
        response = buf.getvalue()

        if CONTINUE_HEADER in response:
            response = response.split("\r\n\r\n", 1)[-1]

        headers, body = response.split("\r\n\r\n", 1)
        status, heads = headers.split("\r\n", 1)

        # NB: mimetools.Message too slow
        headers = dict([map(str.strip, h.split(":", 1))
                        for h in heads.split("\r\n") if h])

        proto, status, message = status.split(" ", 2)
        return int(status), message, headers, body

    @performer
    def get(self, url):
        return self.client(url)

    @performer
    def post(self, url, data=None):
        client, buf = self.client(url)

        client.setopt(pycurl.POST, True)
        data = data or ""
        client.setopt(pycurl.POSTFIELDS, data.encode(self.encoding))

        return client, buf

    @performer
    def delete(self, url, data=None):
        client, buf = self.client(url)

        client.setopt(pycurl.CUSTOMREQUEST, 'delete')

        return client, buf

    @performer
    def put(self, url, data=None):
        data = data or ""

        content = StringIO.StringIO(data.encode(self.encoding))
        client, buf = self.client(url)

        client.setopt(pycurl.PUT, True)
        client.setopt(pycurl.UPLOAD, True)
        client.setopt(pycurl.READFUNCTION, content.read)
        client.setopt(pycurl.INFILESIZE, len(data))

        return client, buf
