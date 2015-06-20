# -*- coding: utf-8 -*-
from httoop.parser import StateMachine, NOT_RECEIVED_YET
from httoop.status import (
	BAD_REQUEST, LENGTH_REQUIRED, URI_TOO_LONG,
	MOVED_PERMANENTLY, HTTP_VERSION_NOT_SUPPORTED, SWITCHING_PROTOCOLS
)
from httoop.messages import Request, Response
from httoop.version import ServerProtocol, ServerHeader


class ServerStateMachine(StateMachine):

	Message = Request
	HTTP2 = None

	def __init__(self, scheme, host, port):
		super(ServerStateMachine, self).__init__()
		self.MAX_URI_LENGTH = float('inf')  # 8000
		self._default_scheme = scheme
		self._default_host = host
		self._default_port = port
		self.request = None
		self.response = None

	def on_message_started(self):
		super(ServerStateMachine, self).on_message_started()
		self.response = Response()
		self.request = self.message
		self.state.update(dict(
			method=False,
			uri=False
		))

	def on_message_complete(self):
		request = super(ServerStateMachine, self).on_message_complete()
		response = self.response
		self.request = None
		self.response = None
		return (request, response)

	def parse_startline(self):
		state = super(ServerStateMachine, self).parse_startline()
		if state is NOT_RECEIVED_YET:
			self._check_uri_max_length(self.buffer)

	def on_startline_complete(self):
		self.state['method'] = True
		self.on_method_complete()

		self.state['uri'] = True
		self.on_uri_complete()

		super(ServerStateMachine, self).on_startline_complete()

	def on_uri_complete(self):
		super(ServerStateMachine, self).on_uri_complete()
		self.sanitize_request_uri_path()
		self.validate_request_uri_scheme()
		self.set_server_response_header()

	def on_protocol_complete(self):
		super(ServerStateMachine, self).on_protocol_complete()
		self.check_request_protocol()
		self.set_response_protocol()

	def on_headers_complete(self):
		self.check_host_header_exists()
		super(ServerStateMachine, self).on_headers_complete()

	def on_body_complete(self):
		super(ServerStateMachine, self).on_body_complete()
		self.check_message_without_body_containing_data()
		self.check_methods_without_body()

	def check_request_protocol(self):
		# check if we speak the same major HTTP version
		if self.message.protocol > ServerProtocol:
			# the major HTTP version differs
			raise HTTP_VERSION_NOT_SUPPORTED('The server only supports HTTP/1.0 and HTTP/1.1.')

	def set_response_protocol(self):
		# set appropriate response protocol version
		self.response.protocol = min(self.message.protocol, ServerProtocol)

	def _check_uri_max_length(self, uri):
		if len(uri) > self.MAX_URI_LENGTH:
			raise URI_TOO_LONG(
				u'The maximum length of the request is %d' % self.MAX_URI_LENGTH
			)

	def sanitize_request_uri_path(self):
		path = self.message.uri.path
		self.message.uri.normalize()
		if path != self.message.uri.path:
			raise MOVED_PERMANENTLY(self.message.uri.path.encode('UTF-8'))

	def validate_request_uri_scheme(self):
		if self.message.uri.scheme:
			if self.message.uri.scheme not in ('http', 'https'):
				raise BAD_REQUEST('Invalid URL: wrong scheme')
		else:
			self.message.uri.scheme = self._default_scheme
			self.message.uri.host = self._default_host
			self.message.uri.port = self._default_port

	def set_server_response_header(self):
		self.response.headers.setdefault('Server', ServerHeader)

	def check_host_header_exists(self):
		if self.message.protocol >= (1, 1) and 'Host' not in self.message.headers:
			raise BAD_REQUEST('Missing Host header')

	def check_message_without_body_containing_data(self):
		if self.buffer and 'Content-Length' not in self.message.headers and not self.chunked:
			# request without Content-Length header but body
			raise LENGTH_REQUIRED(u'Missing Content-Length header.')

	def check_methods_without_body(self):
		if self.message.method.safe and self.message.body:
			raise BAD_REQUEST('A %s request is considered as safe and MUST NOT contain a request body.' % self.message.method)

	def check_http2_upgrade(self):
		def is_http2_upgrade():
			connection = self.message.headers.values('Connection')
			yield 'Upgrade' in connection
			yield 'HTTP2-Settings' in connection
			yield 'Upgrade' in self.message.headers
			yield self.message.headers.element('Upgrade') == 'h2c'
			yield 'HTTP2-Settings' in self.message.headers
			yield self.message.headers.element('HTTP2-Settings')
		if all(is_http2_upgrade()):
			if self.HTTP2 is None:
				return
			self.response.headers['Upgrade'] = 'h2c'
			self.response.headers['Connection'] = 'Upgrade'
			self.__class__ = self.HTTP2
			raise SWITCHING_PROTOCOLS()
