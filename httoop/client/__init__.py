# -*- coding: utf-8 -*-
from httoop.parser import StateMachine
from httoop.date import Date
from httoop.messages import Response


class ClientStateMachine(StateMachine):

	Message = Response

	def prepare(self):
		if self.method.safe:
			self.body = None
			self.chunked = False

		self.chunked = self.chunked
		self.close = self.close

		if self.body and not self.chunked:
			self.headers['Content-Length'] = bytes(len(self.body))

		if 'Host' not in self.headers and self.uri.host:
			self.headers['Host'] = bytes(self.uri.host)

		if self.method in ('PUT', 'POST') and self.body:
			self.headers['Date'] = bytes(Date())  # RFC 2616 Section 14.18

	@property
	def close(self):
		return self.headers.get('Connection') == 'close'

	@close.setter
	def close(self, close):
		if close:
			self.headers['Connection'] = 'close'
		else:
			self.headers.pop('Connection', None)
