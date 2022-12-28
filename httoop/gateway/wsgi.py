# -*- coding: utf-8 -*-
"""Web Server Gateway Interface

.. seealso:: `PEP 333 <http://www.python.org/dev/peps/pep-0333/>`_
"""

from httoop.messages import Body
from httoop.six import PY2, reraise
from httoop.util import iteritems

__all__ = ('WSGI', )


class WSGIBody(Body):
	u"""A Body for WSGI requests and responses"""

	__slots__ = ()

	def write(self, bytes_):
		return super(WSGIBody, self).write(bytes_)

	def read(self, *size):
		return super(WSGIBody, self).read(*size)


class WSGI(object):
	u"""A mixin class which implements the WSGI interface"""

	def __init__(self, environ=None, use_path_info=False, *args, **kwargs):
		self.use_path_info = use_path_info
		super(WSGI, self).__init__()
		self.exc_info = None

		# defaults which will be overriden by set_environ()!
		self.script_name = ''
		self.path_info = ''
		self.server_name = self.request.uri.host.encode()
		self.server_address = None
		self.server_port = str(self.request.uri.port).encode()
		self.wsgi_version = (1, 0)
		self.errors = None
		self.multithread = False
		self.multiprocess = False
		self.run_once = True
		self.remote_address = None
		self.remote_port = None

		self.environ = environ or {}
		self.set_environ(self.environ)
		self.headers_set = False
		self.headers_sent = False

		self.request.body.__class__ = WSGIBody
		self.response.body.__class__ = WSGIBody

	def start_response(self):
		pass

	def __call__(self, application):
		def write(data):
			if not self.headers_set:
				raise RuntimeError("write() before start_response()")
			elif not self.headers_sent:
				self.start_response()
				self.headers_sent = True
			return self.response.body.write(data)

		def start_response(status, response_headers, exc_info=None):
			if exc_info and self.headers_sent:
				try:
					reraise(exc_info[0], exc_info[1], exc_info[2])
				finally:
					exc_info = None  # avoid dangling circular ref
			elif self.headers_set:
				raise RuntimeError("start_response() must be called only once!")
			self.headers_set = True
			self.exc_info = exc_info
			self.response.status.parse(status.encode('ISO8859-1'))

			for name, value in response_headers:
				self.response.headers.append(name, value)
			return write

		raw_result = application(self.get_environ(), start_response)
		if WSGIBody(raw_result).generator:
			# self.response.body.headers = self.response.headers
			self.response.headers['Transfer-Encoding'] = 'chunked'
			self.response.body.chunked = True

		result = iter([raw_result] if isinstance(raw_result, (bytes, str)) else raw_result)
		for data in result:
			if data:
				break
		else:
			write(b'')  # send headers now if body was empty
			return

		def buffered(data):
			try:
				yield data
				for data in result:
					if data:
						yield data
			finally:
				if hasattr(result, 'close'):
					result.close()
		self.response.body = buffered(data)
		return raw_result

	def get_environ(self):
		environ = {}
		environ.update(dict(self.environ.items()))
		environ.update(dict([
			('HTTP_%s' % name.upper().replace('-', '_'), value)
			for name, value in iteritems(self.request.headers)
			if name.lower() not in ('content-type', 'content-length')
		]))
		environ.update({
			'REQUEST_METHOD': bytes(self.request.method),
			'SCRIPT_NAME': b'',
			'REQUEST_URI': self.request.uri.path.encode('ISO8859-1'),
			'PATH_INFO': self.path_info or self.request.uri.path.encode('ISO8859-1'),
			'QUERY_STRING': self.request.uri.query_string.encode('ISO8859-1'),
			'CONTENT_TYPE': self.request.headers.get('Content-Type', b''),
			'CONTENT_LENGTH': self.request.headers.get('Content-Length', b''),
			'SERVER_NAME': self.server_name,
			'SERVER_PORT': self.server_port,
			'SERVER_PROTOCOL': bytes(self.request.protocol),
			'wsgi.version': self.wsgi_version,
			'wsgi.url_scheme': self.request.uri.scheme.encode('ascii'),
			'wsgi.input': self.request.body,
			'wsgi.errors': self.errors,
			'wsgi.multithread': self.multithread,
			'wsgi.multiprocess': self.multiprocess,
			'wsgi.run_once': self.run_once,
		})
		if not PY2:
			environ = dict((key, value.decode('ISO8859-1') if isinstance(value, bytes) else value) for key, value in environ.items())
		return environ

	def set_environ(self, environ):
		environ = environ.copy()

		for name, value in list(environ.items()):
			if name.startswith('HTTP_'):
				environ.pop(name)
				self.request.headers[name[5:].replace('_', '-')] = value
		if 'CONTENT_TYPE' in environ:
			self.request.headers['Content-Type'] = environ.pop('CONTENT_TYPE')
		if 'CONTENT_LENGTH' in environ:
			self.request.headers['Content-Length'] = environ.pop('CONTENT_LENGTH')

		self.server_name = environ.pop('SERVER_NAME', None)
		self.server_address = environ.pop('SERVER_ADDR', None)
		self.server_port = environ.pop('SERVER_PORT', None)

		self.request.method = environ.pop('REQUEST_METHOD', 'GET')
		self.script_name = environ.pop('SCRIPT_NAME', '')
		self.path_info = environ.pop('PATH_INFO', '')
		self.request.uri = environ.pop('REQUEST_URI', '')
		if self.use_path_info:
			self.request.uri.path = self.path_info
		else:
			self.request.uri.host = self.server_name  # could also be Host header?!
			self.request.uri.port = self.server_port
		self.request.uri.scheme = environ.pop('REQUEST_SCHEME', environ.pop('wsgi.url_scheme', 'http'))
		self.request.uri.query_string = environ.pop('QUERY_STRING', '')
		self.request.protocol = environ.pop('SERVER_PROTOCOL', 'HTTP/1.1')
		self.response.protocol = self.request.protocol
		self.wsgi_version = environ.pop('wsgi.version', (1, 0))
		self.request.body = environ.pop('wsgi.input', None)
		self.request.body.seek(0)
		self.errors = environ.pop('wsgi.errors', None)
		self.multithread = environ.pop('wsgi.multithread', False)
		self.multiprocess = environ.pop('wsgi.multiprocess', False)
		self.run_once = environ.pop('wsgi.run_once', True)
		self.remote_address = environ.pop('REMOTE_ADDR', None)
		self.remote_port = environ.pop('REMOTE_PORT', None)
		self.environ = environ
