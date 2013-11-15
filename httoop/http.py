# -*- coding: utf-8 -*-
u"""HTTP - implements and realizes the HTTP rules"""

from httoop.messages import Response, Protocol
from httoop.parser import StateMachine
from httoop.statuses import MOVED_PERMANENTLY, BAD_REQUEST
from httoop.statuses import HTTP_VERSION_NOT_SUPPORTED

import zlib

ServerProtocol = Protocol((1, 1))


# TODO: split into HTTP10, HTTP11
class HTTP(StateMachine):
	def __init__(self, *args, **kwargs):
		super(HTTP, self).__init__(*args, **kwargs)
		self.response = Response()
		self._decompress_obj = None

	def on_protocol_complete(self):
		super(HTTP, self).on_protocol_complete()
		request = self.request
		response = self.response

		# check if we speak the same major HTTP version
		if request.protocol > ServerProtocol:
			# the major HTTP version differs
			raise HTTP_VERSION_NOT_SUPPORTED('The server only supports HTTP/1.0 and HTTP/1.1.')

		# set correct response protocol version
		response.protocol = min(request.protocol, ServerProtocol)

	def on_uri_complete(self):
		super(HTTP, self).on_uri_complete()
		request = self.request

		# sanitize request URI (./, ../, /.$, etc.)
		path = request.uri.path
		request.uri.normalize()
		if path != request.uri.path:
			raise MOVED_PERMANENTLY(request.uri.path.encode('UTF-8'))

		# validate scheme if given
		if request.uri.scheme:
			if request.uri.scheme not in ('http', 'https'):
				raise BAD_REQUEST('Invalid URL: wrong scheme')
		#else:  # FIXME: add these information
		#	# set correct scheme, host and port
		#	request.uri.scheme = 'https' if self.server.secure else 'http'
		#	request.uri.host = self.local.host.name
		#	request.uri.port = self.local.host.port

		## set Server header
		#response.headers.setdefault('Server', self.version)

	def on_headers_complete(self):
		super(HTTP, self).on_headers_complete()
		request = self.request

		# check if Host header exists for > HTTP 1.0
		if request.protocol >= (1, 1) and not 'Host' in request.headers:
			raise BAD_REQUEST('Missing Host header')

		# set decompressor
		encoding = request.headers.get('Content-Encoding')
		if encoding == "gzip":
			self._decompress_obj = zlib.decompressobj(16 + zlib.MAX_WBITS)
		elif encoding == "deflate":
			self._decompress_obj = zlib.decompressobj()

		if 'Content-Type' in request.headers:
			request.body.mimetype = request.headers.element('Content-Type')

	def on_message_complete(self):
		super(HTTP, self).on_message_complete()
		request = self.request

		# TODO: (re)move if RFC 2616 allows this (probably)
		# GET request with body
		if request.method in ('GET', 'HEAD', 'OPTIONS') and request.body:
			raise BAD_REQUEST('A %s request MUST NOT contain a request body.' % request.method)

		# maybe decompress
		if self._decompress_obj is not None:
			try:
				request.body = self._decompress_obj.decompress(request.body.read())
			except zlib.error as exc:
				raise BAD_REQUEST('Invalid compressed bytes: %r' % (exc))

	def prepare_response(self):
		u"""prepare for sending the response"""

		self.response.prepare(self.request)
