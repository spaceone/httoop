# -*- coding: utf-8 -*-
"""Web Server Gateway Interface

.. seealso:: `PEP 333 <http://www.python.org/dev/peps/pep-0333/>`_
"""

import sys
import os

from httoop.messages import Body
from httoop.util import iteritems

__all__ = ('WSGI',)


class WSGIBody(Body):  # pragma: no cover
	u"""A Body for WSGI requests and responses"""

	def write(self, bytes_):
		return super(WSGIBody, self).write(bytes_)

	def read(self, *size):
		return super(WSGIBody, self).read(*size)


class WSGI(object):  # pragma: no cover
	u"""A mixin class which implements the WSGI interface"""

	def __init__(self, use_path_info=False, *args, **kwargs):
		super(WSGI, self).__init__(*args, **kwargs)
		self.use_path_info = use_path_info
		self.wsgi_version = (1, 0)
		self.errors = sys.stderr
		self.multithread = False
		self.multiprocess = False
		self.run_once = False
		self.server_name = bytes(self.request.uri.host)
		self.server_port = bytes(self.request.uri.port)
		self.environ = os.environ

		self.request.body.__class__ = WSGIBody
		self.response.body.__class__ = WSGIBody
		self.response.chunked = True

	def __call__(self, application):
		def start_response(status, response_headers, exc_info=None):
			self.response.status = status
			self.response.headers.update(dict(response_headers))
			return self.response.body.write

		environ = self._get_environ()

		self.start_response(application(environ, start_response))

	def start_response(self, response_body):
		if response_body:
			self.response.body = response_body

	def _get_environ(self):
		environ = {}
		environ.update(dict(self.environ.items()))
		environ.update(dict([
			('HTTP_%s' % name.upper().replace('-', '_'), value)
			for name, value in iteritems(self.request.headers)
		]))
		environ.update({
			'REQUEST_METHOD': bytes(self.request.method),
			'SCRIPT_NAME': b'',
			'PATH_INFO': bytes(self.request.uri.path),
			'REQUEST_URI': bytes(self.request.uri.path),
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

	def from_environ(self, environ=None):
		environ = os.environ if environ is None else environ
		environ = environ.copy()

		for name, value in list(environ.items()):
			if name.startswith('HTTP_'):
				environ.pop(name)
				self.request.headers[name[5:].replace('_', '-')] = value

		self.request.method = environ.pop('REQUEST_METHOD')
		if self.use_path_info:
			self.request.uri.path = environ.pop('PATH_INFO')
		else:
			self.request.uri.path = environ.pop('REQUEST_URI')
		self.request.uri.scheme = environ.pop('REQUEST_SCHEME')
		self.request.uri.query_string = environ.pop('QUERY_STRING')
		if 'CONTENT_TYPE' in environ:
			self.request.headers['Content-Type'] = environ.pop('CONTENT_TYPE')
		if 'CONTENT_LENGTH' in environ:
			self.request.headers['Content-Length'] = environ.pop('CONTENT_LENGTH')
		self.server_name = environ.pop('SERVER_NAME', None)
		self.server_address = environ.pop('SERVER_ADDR', None)
		self.server_port = environ.pop('SERVER_PORT', None)
		self.request.protocol = environ.pop('SERVER_PROTOCOL')
		self.wsgi_version = environ.pop('wsgi.version')
		self.request.uri.scheme = environ.pop('wsgi.url_scheme')
		self.request.body = environ.pop('wsgi.input').read()
		self.request.body.seek(0)
		self.errors = environ.pop('wsgi.errors')
		self.multithread = environ.pop('wsgi.multithread')
		self.multiprocess = environ.pop('wsgi.multiprocess')
		self.run_once = environ.pop('wsgi.run_once')
		self.remote_address = environ.pop('REMOTE_ADDR')
		self.remote_port = environ.pop('REMOTE_PORT')

		self.environ = environ
