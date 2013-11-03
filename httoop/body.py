# -*- coding: utf-8 -*-
"""HTTP request and response body

.. seealso:: :rfc:`2616#section-4.3`
"""

from os.path import getsize
from io import BytesIO

from httoop.exceptions import InvalidBody
from httoop.headers import Headers
from httoop.util import IFile, Unicode
from httoop.meta import HTTPType


class Body(IFile):
	u"""A HTTP message body"""
	__metaclass__ = HTTPType

	@property
	def fileable(self):
		return all(hasattr(self.content, method) for method in ('read', 'write', 'close'))

	MAX_CHUNK_SIZE = 4069

	def __init__(self, body=None, encoding=None):
		# TODO: should we add something like self.mimetype?
		# or a ContentType HeaderField instance which describes
		# the content type (and then also self.encoding)
		self.content = BytesIO()
		self.encoding = encoding

		self.chunked = False
		self.trailer = Headers()

		if body is not None:
			self.set(body)

		self.__iter = None

	def set(self, body):
		if not body:
			body = BytesIO()
		elif isinstance(body, (BytesIO, file)):
			pass
		elif isinstance(body, Unicode):
			body = BytesIO(body.encode(self.encoding or 'UTF-8'))
		elif isinstance(body, bytes):
			body = BytesIO(body)
		elif isinstance(body, Body):
			body = body.content
		elif not hasattr(body, '__iter__'):
			raise InvalidBody('Could not convert data structure of this type')
		self.content = body

	def parse(self, data):
		pass

	def compose(self):
		return b''.join(self.__iter__())

	def __bytes__(self):
		return b''.join(self.__compose_iter())

	def __unicode__(self):
		body = bytes(self)
		for encoding in (self.encoding or 'UTF-8', 'UTF-8', 'ISO8859-1'):
			try:
				return body.decode(encoding)
			except UnicodeDecodeError:
				pass

	def __nonzero__(self):
		return bool(len(self))

	def __len__(self):
		body = self.content

		if isinstance(body, file):
			return getsize(body.name)
		if isinstance(body, BytesIO):
			return len(body.getvalue())

		return len(b''.join(self.__compose_iter()))

	def __iter__(self):
		if self.chunked:
			return self.__compose_chunked_iter()
		return self.__compose_iter()

	def __next__(self):
		if self.__iter is None:
			self.__iter = self.__iter__()
		try:
			return next(self.__iter)
		except StopIteration:
			self.__iter = None
			raise
	next = __next__

	def __compose_chunked_iter(self):
		for data in self.__compose_iter():
			yield "%s\r\n%s\r\n" % (hex(len(data))[2:], data)
		if self.trailer:
			yield b"0\r\n%s" % bytes(self.trailer)
		else:
			yield b"0\r\n\r\n"

	def __compose_iter(self):
		if self.fileable:
			return self.__compose_file_iter()
		return self.__compose_iterable_iter()

	def __compose_file_iter(self, chunksize=MAX_CHUNK_SIZE):
		t = self.tell()
		self.seek(0)

		# real files in python3 have an encoding attribute
		encoding = getattr(self.content, 'encoding', None)

		data = self.read(chunksize)
		while data:
			if encoding is not None:
				data = data.encode(encoding)
			yield data
			data = self.read(chunksize)

		self.seek(t)

	def __compose_iterable_iter(self):
		for data in self.content:
			if isinstance(data, Unicode):
				for encoding in (self.encoding or 'UTF-8', 'UTF-8'):
					try:
						data = data.encode(encoding)
						break
					except UnicodeEncodeError:
						pass
			elif not isinstance(data, bytes):
				raise InvalidBody()
			yield data

	def __repr__(self):
		return '<HTTP Body(%d)>' % len(self)
