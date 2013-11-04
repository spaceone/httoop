# -*- coding: utf-8 -*-
u"""Implements a state machine for the parsing process.
"""

CR = b'\r'
LF = b'\n'
CRLF = CR + LF

from httoop.messages import Request
from httoop.headers import Headers
from httoop.exceptions import InvalidLine, InvalidHeader, InvalidBody, InvalidURI
from httoop.util import Unicode
from httoop.statuses import BAD_REQUEST, NOT_IMPLEMENTED, LENGTH_REQUIRED
from httoop.statuses import HTTPStatusException, REQUEST_URI_TOO_LONG


class StateMachine(object):
	u"""A HTTP Parser"""

	def __init__(self):
		self.request = Request()
		self.buffer = b''
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

	def on_message_complete(self):
		pass

	def on_headers_complete(self):
		pass

	def on_requestline_complete(self):
		self.state_changed('method')
		self.state_changed('uri')
		self.state_changed('protocol')

	def on_method_complete(self):
		pass

	def on_uri_complete(self):
		pass

	def on_protocol_complete(self):
		pass

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
