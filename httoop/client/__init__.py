# -*- coding: utf-8 -*-
from httoop.messages import Response
from httoop.parser import StateMachine


class ClientStateMachine(StateMachine):

	Message = Response

	def on_headers_complete(self):
		super(ClientStateMachine, self).on_headers_complete()
		self.remove_invalid_headers()

	def remove_invalid_headers(self):
		if self.request.method == u'CONNECT':
			self.message.headers.pop('Transfer-Encoding', None)
			self.message.headers.pop('Content-Length', None)
