# -*- coding: utf-8 -*-
u"""Implements a state machine for the parsing process.
"""

from __future__ import absolute_import

CR = b'\r'
LF = b'\n'
CRLF = CR + LF
NOT_RECEIVED_YET = True

from httoop.messages import Message
from httoop.header import Headers
from httoop.exceptions import InvalidLine, InvalidHeader, InvalidBody, InvalidURI, Invalid
from httoop.util import Unicode
from httoop.status import BAD_REQUEST, NOT_IMPLEMENTED


class StateMachine(object):
	u"""A protocol state machine which supports pipelining and
		parses HTTP messages by turning them into appropriate objects."""

	Message = Message  # subclass provides the type

	def __init__(self):
		self.buffer = bytearray()
		self.message = None

	def _reset_state(self):
		self.message = self.Message()

		self.trailers = None
		self.line_end = CRLF
		self.message_length = None
		self.chunked = False

		self.state = dict(
			startline=False,
			protocol=False,
			headers=False,
			body=False
		)

	def on_message_started(self):
		self._reset_state()

	def on_startline_complete(self):
		self.state['protocol'] = True
		self.on_protocol_complete()

	def on_method_complete(self):
		pass

	def on_uri_complete(self):
		pass

	def on_protocol_complete(self):
		pass

	def on_headers_complete(self):
		self.set_body_content_encoding()
		self.set_body_content_type()

	def on_body_complete(self):
		self.message.body.seek(0)
		self.set_content_length()

	def on_message_complete(self):
		message = self.message
		self.message = None
		return message

	def parse(self, data):
		u"""Appends the given data to the internal buffer
			and parses it as HTTP Request-Messages.

			:param data:
				data to parse
			:type  data: bytes
		"""
		self.buffer.extend(data)
		try:
			return tuple(x for x in self._parse() if x is not None)
		except (InvalidHeader, InvalidLine, InvalidURI) as exc:
			raise BAD_REQUEST(Unicode(exc))

	def _parse(self):
		while self.buffer:
			if self.message is None:
				yield self.on_message_started()
			state = self.state
			if not state['startline']:
				if self.parse_startline():
					return
				state['startline'] = True
				yield self.on_startline_complete()

			if not state['headers']:
				if self.parse_headers():
					return
				state['headers'] = True
				yield self.on_headers_complete()

			if not state['body']:
				if self.parse_body():
					return
				state['body'] = True
				yield self.on_body_complete()

			yield self.on_message_complete()

	def parse_startline(self):
		if CRLF not in self.buffer:
			if LF not in self.buffer:
				return NOT_RECEIVED_YET
			self.line_end = LF

		requestline, self.buffer = self.buffer.split(self.line_end, 1)

		# parse request line
		try:
			self.message.parse(bytes(requestline))
		except (InvalidLine, InvalidURI) as exc:
			raise BAD_REQUEST(Unicode(exc))

	def parse_headers(self):
		# empty headers?
		if self.buffer.startswith(self.line_end):
			self.buffer = self.buffer[len(self.line_end):]
			return False

		header_end = self.line_end + self.line_end

		if header_end not in self.buffer:
			# headers incomplete
			return NOT_RECEIVED_YET

		headers, self.buffer = self.buffer.split(header_end, 1)

		# parse headers
		if headers:
			try:
				self.message.headers.parse(bytes(headers))
			except InvalidHeader as exc:
				raise BAD_REQUEST(Unicode(exc))

	def parse_body(self):
		if self.message_length is None and not self.chunked:
			self.determine_message_length()

		if self.chunked:
			return self.parse_chunked_body()
		elif self.message_length:
			return self.parse_body_with_message_length()
		else:
			return False  # no message body

	def determine_message_length(self):
		# RFC 2616 Section 4.4
		# get message length

		# TODO: check if both is set
		message = self.message
		if 'Transfer-Encoding' in message.headers and message.protocol >= (1, 1):
			# chunked transfer in HTTP/1.1
			te = message.headers['Transfer-Encoding'].lower()
			self.chunked = 'chunked' == te
			if not self.chunked:
				raise NOT_IMPLEMENTED(u'Unknown HTTP/1.1 Transfer-Encoding: %r' % te)
		else:
			# Content-Length header defines the length of the message body
			try:
				self.message_length = int(message.headers.get("Content-Length", "0"))
				if self.message_length < 0:
					self.message_length = None
					raise ValueError
			except ValueError:
				raise BAD_REQUEST(u'Invalid Content-Length header.')

	def parse_body_with_message_length(self):
		body, self.buffer = self.buffer[:self.message_length], self.buffer[self.message_length:]
		self.message.body.parse(bytes(body))

		blen = len(body)
		unfinished = blen < self.message_length
		self.message_length -= blen

		if unfinished:
			# the body is not yet received completely
			return NOT_RECEIVED_YET

	def parse_chunked_body(self):
		if self.line_end not in self.buffer:
			# chunk size info not received yet
			return NOT_RECEIVED_YET

		chunk_size, rest_chunk = self.__parse_chunk_size()

		if len(rest_chunk) < (len(self.line_end) + chunk_size):
			# chunk not received completely
			return NOT_RECEIVED_YET

		body_part, rest_chunk = rest_chunk[:chunk_size], rest_chunk[chunk_size:]
		self.message.body.parse(bytes(body_part))
		self.buffer = rest_chunk

		if chunk_size == 0:
			return self.parse_trailers()

		if not rest_chunk.startswith(self.line_end):
			raise InvalidBody(u'Invalid chunk terminator: %r' % repr(rest_chunk[:2]))
		self.buffer = self.buffer[len(self.line_end):]

		# next chunk
		return self.parse_chunked_body()

	def __parse_chunk_size(self):
		line, rest_chunk = self.buffer.split(self.line_end, 1)
		chunk_size = line.split(b";", 1)[0].strip()
		try:
			chunk_size = int(bytes(chunk_size), 16)
			if chunk_size < 0:
				raise ValueError
		except (ValueError, OverflowError):
			raise BAD_REQUEST(u'Invalid chunk size: %r' % chunk_size.decode('ISO8859-1'))
		else:
			return chunk_size, rest_chunk

	def parse_trailers(self):
		# TODO: the code is exactly the same as parse_headers but
		# we have to make sure no invalid header fields are send (only values told in Trailer header allowed)
		if self.buffer.startswith(self.line_end):
			self.buffer = self.buffer[len(self.line_end):]
			return False # no trailers

		trailer_end = self.line_end + self.line_end
		if trailer_end not in self.buffer:
			# not received yet
			return NOT_RECEIVED_YET

		trailers, self.buffer = self.buffer.split(trailer_end, 1)
		self.trailers = Headers()
		try:
			self.trailers.parse(bytes(trailers))
		except InvalidHeader as exc:
			raise BAD_REQUEST(u'Invalid trailers: %r' % Unicode(exc))

		self.merge_trailer_into_header()
		return False

	def merge_trailer_into_header(self):
		message = self.message
		for name in message.headers.values('Trailer'):
			value = self.trailers.pop(name, None)
			if value is not None:
				message.headers.append(name, value)
			else:
				# ignore
				pass
		if self.trailers:
			msg_trailers = u'" ,"'.join(self.trailers.keys())
			raise BAD_REQUEST(u'untold trailers: "%s"' % msg_trailers)
		del self.trailers

	def set_body_content_encoding(self):
		if 'Content-Encoding' in self.message.headers:
			try:
				self.message.body.content_encoding = self.message.headers.element('Content-Encoding')
				self.message.body.content_encoding.codec
			except Invalid as exc:
				raise NOT_IMPLEMENTED('%s' % (exc,))

	def set_body_content_type(self):
		if 'Content-Type' in self.message.headers:
			self.message.body.mimetype = self.message.headers.element('Content-Type')

	def set_content_length(self):
		if 'Content-Length' not in self.message.headers:
			self.message.headers['Content-Length'] = bytes(len(self.message.body))
		if self.chunked:
			self.message.headers.pop('Transfer-Encoding')  # FIXME: there could be other transfer codings as well, only pop out chunked!
