# -*- coding: utf-8 -*-
"""HTTP request and response body

.. seealso:: :rfc:`2616#section-4.3`
"""

from os.path import getsize
from six import text_type, binary_type, BytesIO
from io import BytesIO

from httoop.util import HTTPString

class Body(HTTPString):
	u"""A HTTP message body"""

	def __init__(self, body=None):
		self.body = BytesIO()
		if body is not None:
			self.set(body)

	def set(self, body):
		if not isinstance(body, (BytesIO, file)):
			if not body:
				body = BytesIO()
			elif isinstance(body, text_type):
				body = BytesIO(body.encode('utf-8'))
			elif isinstance(body, binary_type):
				body = BytesIO(body)
			elif isinstance(body, Body):
				body = body.body
		self.body = body

	def __bytes__(self):
		bytesio = self.body
		t = bytesio.tell()
		bytesio.seek(0)
		body = bytesio.read()
		bytesio.seek(t)

		if isinstance(bytesio, file) and bytesio.encoding is not None:
			body = body.encode(bytesio.encoding)

		return body

	def __nonzero__(self):
		return bool(len(self))

	def __len__(self):
		body = self.body

		if isinstance(body, file):
			return getsize(body.name)
		if isinstance(body, BytesIO):
			return len(body.getvalue())

		return len(bytes(self))

	def __repr__(self):
		return '<HTTP Body(%d)>' % len(self)

	def __get__(self, message, cls=None):
		if message is None:
			return self
		return message._Message__body

	def __set__(self, message, body):
		if message is body:
			return

		message.body.set(body)

