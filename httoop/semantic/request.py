# -*- coding: utf-8 -*-
from contextlib import contextmanager

from httoop.version import UserAgentHeader
from httoop.date import Date
from httoop.semantic.message import ComposedMessage
from httoop.uri import URI


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
				self.message.headers['Content-Length'] = str(len(self.message.body))

			if self.message.body.mimetype and 'Content-Type' not in self.message.headers:
				self.message.headers['Content-Type'] = bytes(self.message.body.mimetype)

		if 'Host' not in self.message.headers and self.message.uri.host:
			self.message.headers['Host'] = bytes(self.message.uri.host)

		if self.message.method in ('PUT', 'POST') and self.message.body:
			if 'Date' not in self.message.headers:
				self.message.headers['Date'] = bytes(Date())  # RFC 2616 Section 14.18

		if self.message.method == u'TRACE':
			self.message.headers.pop('Cookie', None)
			self.message.headers.pop('WWW-Authenticate', None)

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

	@contextmanager
	def _composing(self):
		with self.relative_uri(), super(ComposedRequest, self)._composing():
			yield

	@contextmanager
	def relative_uri(self):
		with self.absolute_uri():
			self.message.uri.scheme = None
			self.message.uri.host = None
			self.message.uri.port = None
			yield

	@contextmanager
	def absolute_uri(self):
		try:
			uri = URI(self.message.uri)
			self.message.uri = URI(uri)
			self.message.uri.fragment = None
			self.message.uri.username = None
			self.message.uri.password = None
			yield
		finally:
			self.message.uri = uri
