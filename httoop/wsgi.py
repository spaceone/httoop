# -*- coding: utf-8 -*-
"""Web Server Gateway Interface

.. seealso:: `PEP 333 <http://www.python.org/dev/peps/pep-0333/>`_
"""

__all__ = ['WSGI']

import sys
import os

from httoop.body import ChunkedBody


class WSGIBody(ChunkedBody):
	u"""A Body for WSGI requests and responses"""

	def __init__(self, wsgi, body=None, encoding=None):
		super(WSGIBody, self).__init__(body, encoding)
		self.wsgi = wsgi

	def write(self, bytes_):
		return super(WSGIBody, self).write(bytes_)

	def read(self, bytes_):
		return super(WSGIBody, self).read(bytes_)


class WSGI(object):
	u"""A mixin class which implements the WSGI interface"""

	def __init__(self, *args, **kwargs):
		super(WSGI, self).__init__(*args, **kwargs)
		self.wsgi_version = (1, 0)
		self.errors = sys.stderr
		self.multithread = False
		self.multiprocess = False
		self.run_once = False
		self.server_name = bytes(self.request.uri.host)
		self.server_port = bytes(self.request.uri.port)
		self.os_environ = os.environ

	def __call__(self, application):
		def start_response(status, response_headers, exc_info=None):
			self.response.status = status
			self.response.headers.update(dict(response_headers))
			return self.response.body.write

		environ = self._get_environ()

		self.response.body = WSGIBody(self)

		self.start_response(application(environ, start_response))

	def start_response(self, response_body):
		self.response.body = response_body

	def _get_environ(self):
		environ = {}
		environ.update(dict(self.os_environ.items()))
		environ.update(dict([('HTTP_%s' % name.upper(), value) for name, value in self.request.headers.iteritems()]))
		environ.update({
			'REQUEST_METHOD': bytes(self.request.method),
			'SCRIPT_NAME': b'',
			'PATH_INFO': bytes(self.request.uri.path),
			'QUERY_STRING': bytes(self.request.uri.query_string),
			'CONTENT_TYPE': self.request.headers.get('Content-Type'),
			'CONTENT_LENGTH': self.request.headers.get('Content-Length'),
			'SERVER_NAME': self.server_name,
			'SERVER_PORT': self.server_port,
			'SERVER_PROTOCOL': bytes(self.request.protocol),
			'wsgi.version': self.wsgi_version,
			'wsgi.url_scheme': bytes(self.request.uri.scheme),
			'wsgi.input': self.request.body,
			'wsgi.errors': self.errors,
			'wsgi.multithread': self.multithread,
			'wsgi.multiprocess': self.multiprocess,
			'wsgi.run_once': self.run_once,
		})
		return environ
