# -*- coding: utf-8 -*-
u"""Implements a state machine for the parsing process.
"""

CR = b'\r'
LF = b'\n'
CRLF = CR + LF

from httoop.messages import Request, Response
from httoop.headers import Headers
from httoop.exceptions import InvalidLine, InvalidHeader, InvalidBody, InvalidURI, Invalid
from httoop.util import Unicode
from httoop.statuses import (
	BAD_REQUEST, NOT_IMPLEMENTED, LENGTH_REQUIRED,
	HTTPStatusException, REQUEST_URI_TOO_LONG,
	MOVED_PERMANENTLY, HTTP_VERSION_NOT_SUPPORTED
)
from httoop import ServerProtocol, ServerHeader


class StateMachine(object):
	u"""A HTTP protocol state machine parsing messages and turn them into
		appropriate objects."""

	def __init__(self):
		self.request = Request()
		self.response = Response()
		self.buffer = b''  # TODO: use bytearray
		self.httperror = None

		# public events
		self.on_message = False
		self.on_requestline = False
		self.on_method = False
		self.on_uri = False
		self.on_protocol = False
		self.on_headers = False
		self.on_body = False
		self.on_body_started = False
		self.on_trailers = True  # will be set to false if trailers exists

		self.line_end = CRLF
		self.MAX_URI_LENGTH = 1024
		self.message_length = 0
		self.chunked = False

		self._raise_errors = True

	def error(self, httperror):
		u"""error an HTTP Error"""
		self.httperror = httperror
		self.on_message = True

	def state_changed(self, state):
		setattr(self, 'on_%s' % (state), True)
		getattr(self, 'on_%s_complete' % (state), lambda: None)()

	def on_requestline_complete(self):
		self.state_changed('method')
		self.state_changed('uri')
		self.state_changed('protocol')

	def on_method_complete(self):
		pass

	def on_uri_complete(self):
		self.sanitize_request_uri()
		self.validate_request_uri_scheme()
		self.set_server_header()
		# TODO: set default URI scheme, host, port

	def on_protocol_complete(self):
		self.check_request_protocol()
		self.set_response_protocol()

	def on_headers_complete(self):
		self.check_host_header_exists()
		self.set_body_content_encoding()
		self.set_body_content_type()

	def on_message_complete(self):
		self.check_methods_without_body()

	def parse(self, data):
		u"""Appends the given data to the internal buffer
			and parses it as HTTP Request-Message.

			:param data:
				data to parse
			:type  data: bytes
		"""
		self.buffer = "%s%s" % (self.buffer, data)
		try:
			while True:
				if not self.on_requestline:
					if self.parse_requestline():
						return
					self.state_changed("requestline")

				if not self.on_headers:
					if self.parse_headers():
						return
					self.state_changed("headers")

				if not self.on_body:
					if self.parse_body():
						return
					self.state_changed("body")

				if not self.on_trailers:
					if self.parse_trailers():
						return
					self.state_changed("trailers")

				if not self.on_message:
					self.state_changed("message")
					self.request.body.seek(0)

				if self.buffer:
					raise BAD_REQUEST(u'too much input')

				break
		except HTTPStatusException as httperror:
			self.error(httperror)
			if self._raise_errors:
				raise

	def parse_requestline(self):
		request = self.request
		msg_max_uri = u'The maximum length of the request is %d' % self.MAX_URI_LENGTH
		if CRLF not in self.buffer:
			if LF not in self.buffer:
				if len(self.buffer) > self.MAX_URI_LENGTH:
					raise REQUEST_URI_TOO_LONG(msg_max_uri)
				# request line unfinished
				return True
			self.line_end = LF

		requestline, self.buffer = self.buffer.split(self.line_end, 1)

		# parse request line
		try:
			request.parse(requestline)
		except (InvalidLine, InvalidURI) as exc:
			raise BAD_REQUEST(Unicode(exc))

	def parse_headers(self):
		request = self.request
		# empty headers?
		if self.buffer.startswith(self.line_end):
			self.buffer = self.buffer[len(self.line_end):]
			self.state_changed("headers")
			return False

		header_end = self.line_end + self.line_end

		if header_end not in self.buffer:
			# headers incomplete
			return True

		headers, self.buffer = self.buffer.split(header_end, 1)

		# parse headers
		if headers:
			try:
				request.headers.parse(headers)
			except InvalidHeader as exc:
				raise BAD_REQUEST(Unicode(exc))

	def parse_body(self):
		request = self.request
		if not self.on_body_started:
			# RFC 2616 Section 4.4
			# get message length

			self.state_changed("body_started")
			if request.protocol >= (1, 1) and 'Transfer-Encoding' in request.headers:
				# chunked transfer in HTTP/1.1
				te = request.headers['Transfer-Encoding'].lower()
				self.chunked = 'chunked' == te
				if not self.chunked:
					raise NOT_IMPLEMENTED(u'Unknown HTTP/1.1 Transfer-Encoding: %s' % te)
			else:
				# Content-Length header defines the length of the message body
				try:
					self.message_length = int(request.headers.get("Content-Length", "0"))
					if self.message_length < 0:
						raise ValueError
				except ValueError:
					raise BAD_REQUEST(u'Invalid Content-Length header.')

		if self.chunked:
			if self.line_end not in self.buffer:
				# chunk size info not received yet
				return True

			line, rest_chunk = self.buffer.split(self.line_end, 1)
			chunk_size = line.split(b";", 1)[0].strip()
			try:
				chunk_size = int(chunk_size, 16)
				if chunk_size < 0:
					raise ValueError
			except (ValueError, OverflowError):
				raise BAD_REQUEST(u'Invalid chunk size: %s' % chunk_size)

			if len(rest_chunk) < (chunk_size + len(self.line_end)):
				# chunk not received completely
				# buffer is untouched
				return True

			body_part, rest_chunk = rest_chunk[:chunk_size], rest_chunk[chunk_size:]
			if not rest_chunk.startswith(self.line_end):
				msg_inv_chunk = self.buffer.decode('ISO8859-1')
				raise InvalidBody(u'chunk invalid terminator: [%r]' % msg_inv_chunk)

			request.body.parse(body_part)

			self.buffer = rest_chunk[len(self.line_end):]

			if chunk_size == 0:
				# finished
				return False

		elif self.message_length:
			request.body.parse(self.buffer)
			self.buffer = b''

			blen = len(request.body)
			if blen == self.message_length:
				return False
			elif blen < self.message_length:
				# the body is not yet received completely
				return True
			elif blen > self.message_length:
				raise BAD_REQUEST(u'Body length mismatchs Content-Length header.')

		elif self.buffer:
			# request without Content-Length header but body
			raise LENGTH_REQUIRED(u'Missing Content-Length header.')
		else:
			# no message body
			return False

	def parse_trailers(self):
		request = self.request
		if 'Trailer' not in request.headers:
			return False

		trailer_end = self.line_end + self.line_end
		if trailer_end not in self.buffer:
			# not received yet
			return True

		trailers, self.buffer = self.buffer.split(trailer_end, 1)
		request.trailers = Headers()
		try:
			request.trailers.parse(trailers)
		except InvalidHeader as exc:
			raise BAD_REQUEST(u'Invalid trailers: %s' % Unicode(exc))
		for name in request.headers.values('Trailer'):
			value = request.trailers.pop(name, None)
			if value is not None:
				request.headers.append(name, value)
			else:
				# ignore
				pass
		if request.trailers:
			msg_trailers = u'" ,"'.join(request.trailers.keys())
			raise BAD_REQUEST(u'untold trailers: "%s"' % msg_trailers)
		del request.trailers

	def check_request_protocol(self):
		# check if we speak the same major HTTP version
		if self.request.protocol > ServerProtocol:
			# the major HTTP version differs
			raise HTTP_VERSION_NOT_SUPPORTED('The server only supports HTTP/1.0 and HTTP/1.1.')

	def set_response_protocol(self):
		# set correct response protocol version
		self.response.protocol = min(self.request.protocol, ServerProtocol)

	def sanitize_request_uri(self):
		path = self.request.uri.path
		self.request.uri.normalize()
		if path != self.request.uri.path:
			raise MOVED_PERMANENTLY(self.request.uri.path.encode('UTF-8'))

	def validate_request_uri_scheme(self):
		if self.request.uri.scheme:
			if self.request.uri.scheme not in ('http', 'https'):
				raise BAD_REQUEST('Invalid URL: wrong scheme')

	def set_server_header(self):
		self.response.headers.setdefault('Server', ServerHeader)

	def check_host_header_exists(self):
		if self.request.protocol >= (1, 1) and not 'Host' in self.request.headers:
			raise BAD_REQUEST('Missing Host header')

	def set_body_content_encoding(self):
		if 'Content-Encoding' in self.request.headers:
			self.request.body.content_encoding = self.request.headers.element('Content-Encoding')

			try:
				self.request.body.content_encoding.codec
			except Invalid as exc:
				raise NOT_IMPLEMENTED('%s' % (exc,))

	def set_body_content_type(self):
		if 'Content-Type' in self.request.headers:
			self.request.body.mimetype = self.request.headers.element('Content-Type')

	def check_methods_without_body(self):
		if self.request.method.safe and self.request.body:
			raise BAD_REQUEST('A %s request is considered as safe and MUST NOT contain a request body.' % self.request.method)

	def prepare_response(self):
		u"""prepare for sending the response"""

		self.response.prepare(self.request)
