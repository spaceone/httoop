# -*- coding: utf-8 -*-
"""Web Server Gateway Interface

.. seealso:: `PEP 333 <http://www.python.org/dev/peps/pep-0333/>`_
"""

__all__ = ['WSGI']

import sys
import os

from httoop.messages import Body
from httoop.util import iteritems


class WSGIBody(Body):
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
		self.environ = os.environ

		self.request._Request__body = WSGIBody(self)
		self.response._Response__body = WSGIBody(self)
		self.response.chunked = True

	def __call__(self, application):
		def start_response(status, response_headers, exc_info=None):
			self.response.status = status
			self.response.headers.update(dict(response_headers))
			return self.response.body.write

		environ = self._get_environ()

		self.start_response(application(environ, start_response))

	def start_response(self, response_body):
		self.response.body = response_body

	def _get_environ(self):
		environ = {}
		environ.update(dict(self.environ.items()))
		environ.update(dict([('HTTP_%s' % name.upper().replace('-', '_'), value)
			for name, value in iteritems(self.request.headers)]))
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

	def from_environ(self, environ=os.environ):
		environ = environ.copy()

		for name, value in iteritems(environ):
			if name.startswith('HTTP_'):
				self.request.headers[name[5:].replace('_', '-')] = value

		self.request.body = environ['REQUEST_METHOD']
		self.request.uri.path = environ['PATH_INFO']
		self.request.uri.query_string = environ['QUERY_STRING']
		self.request.headers['Content-Type'] = environ.get('CONTENT_TYPE')
		self.request.headers['Content-Length'] = environ.get('Content-Length')
		self.server_name = environ.get('SERVER_NAME')
		self.server_port = environ.get('SERVER_PORT')
		self.request.protocol = environ['SERVER_PROTOCOL']
		self.wsgi_version = environ['wsgi.version']
		self.request.uri.scheme = environ['wsgi.url_scheme']
		self.request.body = environ['wsgi.input']
		self.errors = environ['wsgi.errors']
		self.multithread = environ['wsgi.multithread']
		self.multiprocess = environ['wsgi.multiprocess']
		self.run_once = environ['wsgi.run_once']

		self.environ = environ
