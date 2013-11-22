# -*- coding: utf-8 -*-
"""HTTP request and response body

.. seealso:: :rfc:`2616#section-4.3`
"""

from os.path import getsize
from io import BytesIO

from httoop.exceptions import InvalidBody
from httoop.headers import Headers
from httoop.header import ContentType
from httoop.codecs import CODECS
from httoop.util import IFile, Unicode
from httoop.meta import HTTPSemantic


class Body(IFile):
	u"""A HTTP message body"""
	__metaclass__ = HTTPSemantic
	__slots__ = ('content', 'data', '_mimetype', 'chunked', '__iter', 'trailer')

	MAX_CHUNK_SIZE = 4096

	@property
	def fileable(self):
		return all(hasattr(self.content, method) for method in ('read', 'write', 'close'))

	@property
	def encoding(self):
		return self.mimetype.charset or 'UTF-8'

	@encoding.setter
	def encoding(self, charset):
		self.mimetype.charset = charset

	@property
	def mimetype(self):
		return self._mimetype

	@mimetype.setter
	def mimetype(self, mimetype):
		self._mimetype = ContentType.from_str(bytes(mimetype))

	@property
	def codec(self):
		codec = None
		if self.mimetype.vendor:
			codec = CODECS.get(self.mimetype.value)
		return codec or CODECS.get(self.mimetype.mimetype)

	def __init__(self, body=None, mimetype=None):
		self.content = BytesIO()
		self.mimetype = mimetype or b'text/plain; charset=UTF-8'
		self.data = None

		self.chunked = False
		self.trailer = Headers()

		if body is not None:
			self.set(body)

		self.__iter = None

	def set(self, body):
		if isinstance(body, Body):
			self.mimetype = body.mimetype
			self.data = body.data
			self.chunked = body.chunked
			self.trailer = body.trailer
			self.content = body.content
			return
		if not body:
			body = BytesIO()
		elif isinstance(body, (BytesIO, file)):
			pass
		elif isinstance(body, Unicode):
			body = BytesIO(body.encode(self.encoding))
		elif isinstance(body, bytes):
			body = BytesIO(body)
		elif not hasattr(body, '__iter__'):
			raise InvalidBody('Could not convert data structure of this type')
		self.content = body

	def parse(self, data):
		self.write(data)

	def encode(self):
		codec = self.codec
		if codec:
			value = codec.encode(self.data, self.encoding)
			self.set(value)

	def decode(self):
		codec = self.codec
		if codec:
			self.data = codec.decode(bytes(self), self.encoding)

	def compose(self):
		return b''.join(self.__iter__())

	def __bytes__(self):
		return b''.join(self.__compose_iter())

	def __unicode__(self):
		body = bytes(self)
		for encoding in (self.encoding, 'UTF-8', 'ISO8859-1'):
			try:
				return body.decode(encoding)
			except UnicodeDecodeError:
				pass

	def __bool__(self):
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
				for encoding in (self.encoding, 'UTF-8'):
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
