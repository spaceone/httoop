# -*- coding: utf-8 -*-
u"""Implements a state machine for the parsing process.
"""

CR = b'\r'
LF = b'\n'
CRLF = CR + LF

from httoop.messages import Request, Response
from httoop.headers import Headers
from httoop.exceptions import InvalidLine, InvalidHeader, InvalidURI, InvalidBody
from httoop.util import text_type
from httoop.statuses import BAD_REQUEST, NOT_IMPLEMENTED, LENGTH_REQUIRED, MOVED_PERMANENTLY, REQUEST_URI_TOO_LONG, HTTP_VERSION_NOT_SUPPORTED

import zlib

ServerProtocol = (1, 1)

class StateMachine(object):
	u"""A HTTP Parser"""

	def __init__(self):
		self.request = Request()
		self.response = Response()
		self.buffer = b''
		self.httperror = None

		# public events
		self.on_message = False
		self.on_requestline = False
		#self.on_method = False
		#self.on_uri = False
		#self.on_protocol = False
		self.on_headers = False
		self.on_body = False
		self.on_body_started = False
		self.on_trailers = True # will be set to false if trailers exists

		self.line_end = CRLF
		self.MAX_URI_LENGTH = 1024
		self.message_length = 0
		self.chunked = False

		self._raise_errors = False

	def error(self, httperror):
		u"""error an HTTP Error"""
		self.httperror = httperror
		self.on_message = True
		if self._raise_errors:
			raise self.httperror

	def state_changed(self, state):
		setattr(self, 'on_%s' % (state), True)

	def parse(self, data):
		u"""Appends the given data to the internal buffer and parses it as HTTP Request-Message.

			:param data:
				data to parse
			:type  data: bytes
		"""

		self.buffer = "%s%s" % (self.buffer, data)

		request = self.request
		line_end = self.line_end

		while True:
			if not self.on_requestline:

				if CRLF not in self.buffer:
					if LF not in self.buffer:
						# request line unfinished
						if len(self.buffer) > self.MAX_URI_LENGTH:
							self.error(REQUEST_URI_TOO_LONG(u'The maximum length of the request is %d' % self.MAX_URI_LENGTH))
						return
					self.line_end = line_end = LF

				requestline, self.buffer = self.buffer.split(line_end, 1)

				# parse request line
				try:
					request.parse(requestline)
				except InvalidLine as exc:
					return self.error(BAD_REQUEST(text_type(exc)))

				self.state_changed("requestline")

			if not self.on_headers:
				# empty headers?
				if self.buffer.startswith(line_end):
					self.buffer = self.buffer[len(line_end):]
					self.state_changed("headers")
					continue

				header_end = line_end+line_end

				if header_end not in self.buffer:
					# headers incomplete
					return

				headers, self.buffer = self.buffer.split(header_end, 1)

				# parse headers
				if headers:
					try:
						request.headers.parse(headers)
					except InvalidHeader as exc:
						return self.error(BAD_REQUEST(text_type(exc)))

				self.state_changed("headers")

			elif not self.on_body:
				if not self.on_body_started:
					# RFC 2616 Section 4.4
					# get message length

					self.state_changed("body_started")
					if request.protocol >= (1, 1) and 'Transfer-Encoding' in request.headers:
						# chunked transfer in HTTP/1.1
						te = request.headers['Transfer-Encoding'].lower()
						self.chunked = 'chunked' == te
						if not self.chunked:
							return self.error(NOT_IMPLEMENTED(u'Unknown HTTP/1.1 Transfer-Encoding: %s' % te))
					else:
						# Content-Length header defines the length of the message body
						try:
							self.message_length = int(request.headers.get("Content-Length", "0"))
							if self.message_length < 0:
								raise ValueError
						except ValueError:
							return self.error(BAD_REQUEST(u'Invalid Content-Length header.'))

				if self.chunked:
					if line_end not in self.buffer:
						# chunk size info not received yet
						return

					line, rest_chunk = self.buffer.split(line_end, 1)
					chunk_size = line.split(b";", 1)[0].strip()
					try:
						chunk_size = int(chunk_size, 16)
						if chunk_size < 0:
							raise ValueError
					except (ValueError, OverflowError):
						return self.error(BAD_REQUEST(u'Invalid chunk size: %s' % chunk_size))

					if len(rest_chunk) < (chunk_size + len(line_end)):
						# chunk not received completely
						# buffer is untouched
						return

					body_part, rest_chunk = rest_chunk[:chunk_size], rest_chunk[chunk_size:]
					if not rest_chunk.startswith(line_end):
						raise InvalidBody(u'chunk invalid terminator: [%s]' % self.buffer.decode('ISO8859-1'))

					request.body.write(body_part)

					self.buffer = rest_chunk[len(line_end):]

					if chunk_size == 0:
						# finished
						self.state_changed("body")

				elif self.message_length:
					request.body.write(self.buffer)
					self.buffer = b''

					blen = len(request.body)
					if blen == self.message_length:
						self.state_changed("body")
					elif blen < self.message_length:
						# the body is not yet received completely
						return
					elif blen > self.message_length:
						self.error(BAD_REQUEST(u'Body length mismatchs Content-Length header.'))
						return

				elif self.buffer:
					# request without Content-Length header but body
					self.error(LENGTH_REQUIRED(u'Missing Content-Length header.'))
					return
				else:
					# no message body
					self.state_changed("body")

			elif not self.on_trailers:
				if 'Trailer' in request.headers:
					trailer_end = line_end + line_end
					if trailer_end not in self.buffer:
						# not received yet
						return

					trailers, self.buffer = self.buffer.split(trailer_end, 1)
					request.trailers = Headers()
					try:
						request.trailers.parse(trailers)
					except InvalidHeader as exc:
						self.error(BAD_REQUEST(u'Invalid trailers: %s' % text_type(exc)))
						return
					for name in request.headers.values('Trailer'):
						value = request.trailers.pop(name, None)
						if value is not None:
							request.headers.append(name, value)
						else:
							# ignore
							pass
					if request.trailers:
						self.error(BAD_REQUEST(u'untold trailers: "%s"' % u'" ,"'.join(request.trailers.keys())))
					del request.trailers
				self.state_changed("trailers")
			elif not self.on_message:
				self.state_changed("message")
				request.body.seek(0)
			else:
				if self.buffer:
					return self.error(BAD_REQUEST(u'too much input'))
				break

class HTTP(StateMachine):
	def __init__(self, *args, **kwargs):
		super(HTTP, self).__init__(*args, **kwargs)
		self._decompress_obj = None

	def state_changed(self, state):
		super(HTTP, self).state_changed(state)
		request = self.request
		response = self.response
		if state == "requestline":
			# check if we speak the same major HTTP version
			if request.protocol.major != response.protocol.major or request.protocol.minor not in (0, 1):
				# the major HTTP version differs
				return self.error(HTTP_VERSION_NOT_SUPPORTED('The server only supports HTTP/1.0 and HTTP/1.1.'))

			# set correct response protocol version
			response.protocol = min(request.protocol, ServerProtocol)

			# sanitize request URI (./, ../, /.$, etc.)
			path = bytes(request.uri.path)
			request.uri.sanitize()
			if path != bytes(request.uri.path):
				return self.error(MOVED_PERMANENTLY(request.uri.path))

			# validate scheme if given
			if request.uri.scheme:
				if request.uri.scheme not in ('http', 'https'):
					return self.error(BAD_REQUEST('wrong scheme'))
			# FIXME: add these information
			#else:
			#	# set correct scheme, host and port
			#	request.uri.scheme = 'https' if self.server.secure else 'http'
			#	request.uri.host = self.local.host.name
			#	request.uri.port = self.local.host.port

			## set Server header
			#response.headers['Server'] = self.version

		if state == "headers":
			# check if Host header exists for > HTTP 1.0
			if request.protocol >= (1, 1) and not 'Host' in request.headers:
				return self.error(BAD_REQUEST('Missing Host header'))

			# set decompressor
			encoding = request.headers.get('content-encoding')
			if encoding == "gzip":
				self._decompress_obj = zlib.decompressobj(16+zlib.MAX_WBITS)
			elif encoding == "deflate":
				self._decompress_obj = zlib.decompressobj()

		if state == "message":
			# TODO: (re)move if RFC 2616 allows this (probably)
			# GET request with body
			if request.method in ('GET', 'HEAD', 'OPTIONS') and request.body:
				self.error(BAD_REQUEST('A %s request MUST NOT contain a request body.' % request.method))
				return
			# maybe decompress
			if self._decompress_obj is not None:
				try:
					request.body = self._decompress_obj.decompress(request.body.read())
				except zlib.error as exc:
					self.error(BAD_REQUEST('Invalid compressed bytes: %r' % (exc)))

	def prepare_response(self):
		u"""prepare for sending the response"""

		self.response.prepare()

		if self.request.method == 'HEAD':
			# RFC 2616 Section 9.4
			self.response.body = None

