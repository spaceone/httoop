# -*- coding: utf-8 -*-
from httoop.date import Date
from httoop.exceptions import InvalidHeader
from httoop.messages.body import Body
from httoop.semantic.message import ComposedMessage
from httoop.status import STATUSES
from httoop.util import izip, make_boundary


class ComposedResponse(ComposedMessage):

	def __init__(self, response, request):
		super(ComposedResponse, self).__init__()
		self.request = request
		self.response = self.message = response

	def prepare(self):
		u"""prepares the response for being ready for transmitting"""

		response = self.response

		status = int(response.status)
		if status < 200 or status in (204, 205, 304):
			# 1XX, 204 NO_CONTENT, 205 RESET_CONTENT, 304 NOT_MODIFIED
			response.body = None

		if 'Content-Encoding' in response.headers:
			response.body.content_encoding = response.headers.element('Content-Encoding')
			self.chunked = True  # TODO: workaround for not calculate Content-Length again

		self.chunked = self.chunked
		if not self.chunked:
			response.headers['Content-Length'] = str(len(response.body)).encode('ASCII')

		response.headers['Date'] = bytes(Date())  # RFC 2616 Section 14.18

		# remove header which should not occur along with this status
		if status in STATUSES:
			for header in STATUSES[status].header_to_remove:
				response.headers.pop(header, None)

		if status == 405:
			response.headers.setdefault('Allow', 'GET, HEAD')

		self.close = self.close

		if 'Content-Type' not in response.headers and response.body.mimetype and response.body:
			response.headers['Content-Type'] = bytes(response.body.mimetype)

		if response.status == 200 and response.body.fileable and not self.chunked and 'Etag' in response.headers or 'Last-Modified' in response.headers:
			response.headers.setdefault('Accept-Ranges', b'bytes')

		self.prepare_ranges()

		if response.status == 416:
			response.headers.set_element('Content-Range', 'bytes', None, response.headers.get('Content-Length'))

		if self.request.method == u'TRACE':
			response.headers.pop('Set-Cookie', None)

		if self.request.method == u'HEAD':
			response.body = None  # RFC 2616 Section 9.4

	def prepare_ranges(self):
		if not all(self.range_conditions()):
			return False

		try:
			range_ = self.request.headers.element('Range')
		except InvalidHeader:
			self.response.status = 416
			return False
		else:
			return self.prepare_range(range_)

	def range_conditions(self):
		response = self.response
		yield response.protocol >= (1, 1)
		yield self.request.protocol >= (1, 1)
		yield response.status == 200
		yield 'Range' in self.request.headers
		yield self.request.method in (u'GET', )
		yield response.headers.element('Accept-Ranges') == 'bytes'
		yield not self.chunked
		yield response.body
		yield response.body.fileable

	def prepare_range(self, range_):
		response = self.response
		content_length = response.headers.get('Content-Length')
		response.status = 206
		range_body = range_.get_range_content(response.body.fd)
		if len(range_.ranges) == 1:
			response.headers.set_element('Content-Range', 'bytes', range_.ranges[0], content_length)
			response.body = range_body
		else:
			content_type = response.headers.get('Content-Type')
			response.body = None
			response.headers['Content-Type'] = response.headers.create_element('Content-Type', 'multipart/byteranges', {'boundary': make_boundary()})
			response.body.mimetype = response.headers['Content-Type']
			response.body.encode(self.multipart_byteranges(range_body, range_, content_length, content_type))

		response.headers['Content-Length'] = str(len(response.body)).encode('ASCII')  # FIXME: len(response.body) causes the whole body to be generated
		return True

	def multipart_byteranges(self, range_body, range_, content_length, content_type):
		for content, byterange in izip(range_body, range_.ranges):
			body = Body(content)
			body.headers['Content-Type'] = content_type
			body.headers.set_element('Content-Range', 'bytes', byterange, content_length)
			yield body

	@property
	def close(self):
		return any(self.__close_constraints())

	def __close_constraints(self):
		response = self.response
		# TODO: 100 Continue
		# 413 Request Entity Too Large
		# RFC 2616 Section 10.4.14
		yield response.status == 413

		yield response.headers.get('Connection') == 'close'

		yield response.protocol < (1, 1)

	@close.setter
	def close(self, close):
		response = self.response
		if close:
			if response.protocol >= (1, 1):
				response.headers['Connection'] = 'close'
				return
		else:
			if response.protocol < (1, 1):
				response.headers['Connection'] = 'keep-alive'
				return
		if response.headers.get('Connection') == 'close':
			response.headers.pop('Connection', None)
