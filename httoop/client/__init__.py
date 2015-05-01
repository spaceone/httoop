# -*- coding: utf-8 -*-
from httoop import UserAgentHeader
from httoop.parser import StateMachine
from httoop.date import Date
from httoop.messages import Response
from httoop.composer import ComposedMessage


class ClientStateMachine(StateMachine):

	Message = Response


class ComposedRequest(ComposedMessage):

	USER_AGENT = UserAgentHeader

	def __init__(self, request):
		self.message = request

	def prepare(self):
		if self.message.method.safe:
			self.message.body = None
			self.chunked = False

		self.chunked = self.chunked
		self.close = self.close

		if self.message.body:
			if not self.chunked:
				self.message.headers['Content-Length'] = bytes(len(self.message.body))

			if self.message.body.mimetype and 'Content-Type' not in self.message.headers:
				self.message.headers['Content-Type'] = bytes(self.message.body.mimetype)

		if 'Host' not in self.message.headers and self.message.uri.host:
			self.message.headers['Host'] = bytes(self.message.uri.host)

		if self.message.method in ('PUT', 'POST') and self.message.body:
			if 'Date' not in self.message.headers:
				self.message.headers['Date'] = bytes(Date())  # RFC 2616 Section 14.18

		self.message.headers.setdefault('User-Agent', self.USER_AGENT)
		self.message.headers.setdefault('Accept', '*/*')

	@property
	def close(self):
		return self.message.headers.get('Connection') == 'close'

	@close.setter
	def close(self, close):
		if close:
			self.message.headers['Connection'] = 'close'
		else:
			self.message.headers.pop('Connection', None)
