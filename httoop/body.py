# -*- coding: utf-8 -*-
"""utilities for HTTP bodies"""

import os.path
from circuits.six import PY3, string_types, binary_type
from io import IOBase

class HTTPBody(object):
	u"""A HTTP message body

		We are internally saving the value as list which
		is faster to iterate over if we are responding in chunks
		(useful if we ever want to support WSGI)
	"""
	value = None

	def __init__(self, value=None):
		if value is None:
			value = []
		self.value = value

	def set(self, body):
		if isinstance(body, string_types):
			if body:
				body = [body]
			else:
				body = []
		elif body is None:
			body = []

		self.value = body

	def __unicode__(self):
		return bytes(self).decode('utf-8')

	def __bytes__(self):
		_body = self.value
		body = None
		if isinstance(_body, (IOBase, file)):
			body = _body.read()
			_body.seek(0)
		elif isinstance(_body, list):
			body = b''.join([b if isinstance(b, binary_type) else b.encode('utf-8') for b in _body])
		elif isinstance(_body, string_types):
			body = _body
		else:
			# should not happen, this is dangerous
			if isinstance(_body, dict):
				body = repr(_body)
			else:
				body = _body

		if not isinstance(body, binary_type):
			body = body.encode('utf-8')

		return body

	def __str__(self):
		if PY3:
			return self.__unicode__()
		else:
			return self.__bytes__()

	def __nonzero__(self):
		return bool(self.value)

	def __len__(self):
		body = self.value
		if body is None:
			return 0

		if isinstance(body, file):
			return os.path.getsize(body.name)
		if isinstance(body, IOBase):
			return len(body.getvalue()) # already bytes

		return len(bytes(self))

