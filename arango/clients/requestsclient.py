import logging

try:
    import requests
except ImportError:
    raise ImportError(
        "Please, install ``requests`` library to use this client")

from .base import RequestsBase

__all__ = ("RequestsClient",)

logger = logging.getLogger("arango.requests")


class RequestsClient(RequestsBase):

    """
    If no PyCURL bindings available or
    client forced by hands. Quite useful for PyPy.
    """
    _config = {}
    headers = {}
    sess = requests.Session()

    def updateauth(self):
        if self.headers.get('Authorization', None):
            self.sess.headers.update(
                {'Authorization': self.headers['Authorization']})

    def config(self, **kwargs):
        self._config.update(kwargs)

    def get(self, url, **kwargs):
        self.updateauth()
        r = self.sess.get(url, **self._config)

        return self.build_response(
            r.status_code,
            r.reason,
            r.headers,
            r.text)

    def post(self, url, data=None):
        self.updateauth()
        if data is None:
            data = ""

        r = self.sess.post(url, data=data, **self._config)

        return self.build_response(
            r.status_code,
            r.reason,
            r.headers,
            r.text)

    def put(self, url, data=None):
        self.updateauth()
        if data is None:
            data = ""

        r = self.sess.put(url, data=data, **self._config)

        return self.build_response(
            r.status_code,
            r.reason,
            r.headers,
            r.text)

    def delete(self, url, data=None):
        self.updateauth()
        r = self.sess.delete(url, **self._config)

        return self.build_response(
            r.status_code,
            r.reason,
            r.headers,
            r.text)
