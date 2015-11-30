# -*- coding: utf-8 -*-
from httoop.parser import StateMachine
from httoop.messages import Response


class ClientStateMachine(StateMachine):

	Message = Response

	def on_headers_complete(self):
		self.remove_invalid_headers()

	def remove_invalid_headers(self):
		if self.request.method == u'CONNECT':
			self.response.headers.pop('Transfer-Encoding', None)
			self.response.headers.pop('Content-Length', None)
