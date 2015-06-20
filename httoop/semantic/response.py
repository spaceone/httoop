# -*- coding: utf-8 -*-
from httoop.semantic.message import ComposedMessage
from httoop.status import STATUSES
from httoop.date import Date


class ComposedResponse(ComposedMessage):

	def __init__(self, response, request):
		super(ComposedResponse, self).__init__()
		self.request = request
		self.response = self.message = response

	def prepare(self):
		u"""prepares the response for being ready for transmitting"""

		response = self.response
		request = self.request

		status = int(response.status)
		if status < 200 or status in (204, 205, 304):
			# 1XX, 204 NO_CONTENT, 205 RESET_CONTENT, 304 NOT_MODIFIED
			response.body = None

		self.chunked = self.chunked
		if not self.chunked:
			response.headers['Content-Length'] = bytes(len(response.body))

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

		if request is None:
			return

		if request.method == u'HEAD':
			response.body = None  # RFC 2616 Section 9.4

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
		response.headers.pop('Connection', None)

