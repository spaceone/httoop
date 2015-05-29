# -*- coding: utf-8 -*-
"""HTTP request and response body

.. seealso:: :rfc:`2616#section-4.3`
"""

from os.path import getsize
from io import BytesIO

from httoop.header import Headers
from httoop.util import IFile, Unicode
from httoop.meta import HTTPSemantic


class Body(IFile):
	u"""A HTTP message body

		This class is capable of handling HTTP Transfer-Encoding
		and Content-Encoding as defined in RFC 2616.

		It provides an interface which makes it possible to use either
		unicode, bytes, bytearray, file, file-like objects (e.g. from the
		codecs module) or any iterable returning bytes/unicode as type
		for the content.

		The encode and decode methods can also control the automatic en/decoding of
		the content using the codec specified in the MIME media type.
	"""
	__metaclass__ = HTTPSemantic
	__slots__ = (
		'content', 'data', '__iter', 'headers', 'trailer',
		'content_codec', 'transfer_codec'
	)

	MAX_CHUNK_SIZE = 4096

	@property
	def fileable(self):
		u"""Flag whether the set content provides the file interface"""
		return all(hasattr(self.content, method) for method in ('read', 'write', 'close'))

	@property
	def encoding(self):
		return self.mimetype.charset or 'UTF-8'

	@encoding.setter
	def encoding(self, charset):
		mimetype = self.mimetype
		mimetype.charset = charset
		self.mimetype = mimetype

	@property
	def mimetype(self):
		u"""Represents the MIME media type of the content"""
		return self.headers.element('Content-Type')

	@mimetype.setter
	def mimetype(self, mimetype):
		self.headers['Content-Type'] = bytes(mimetype)

	@property
	def content_encoding(self):
		return self.headers.element('Content-Encoding')

	@content_encoding.setter
	def content_encoding(self, value):
		if value:
			self.headers['Content-Encoding'] = bytes(value)
			self.content_codec = None  #self.content_encoding.iterdecode()
		else:
			self.headers.pop('Content-Encoding', None)
			self.content_codec = None

	@property
	def transfer_encoding(self):
		return self.headers.element('Transfer-Enconding')

	@transfer_encoding.setter
	def transfer_encoding(self, transfer_encoding):
		if transfer_encoding:
			self.headers['Transfer-Enconding'] = bytes(transfer_encoding)
			self.transfer_codec = None  #self.transfer_encoding.iterdecode()
		else:
			self.headers.pop('Transfer-Encoding', None)
			self.transfer_codec = None

	@property
	def chunked(self):
		if not self.transfer_encoding:
			return False
		return 'chunked' == self.transfer_encoding.value

	@chunked.setter
	def chunked(self, chunked):
		self.transfer_encoding = 'chunked' if chunked else None

	def __init__(self, content=None, mimetype=None):
		self.data = None
		self.__iter = None
		self.content = BytesIO()
		self.headers = Headers()
		self.trailer = Headers()
		self.transfer_codec = None
		self.content_codec = None

		self.mimetype = mimetype or b'text/plain; charset=UTF-8'
		self.set(content)

	def encode(self, *data):
		u"""Encode the object in :attr:`data` if a codec for the mimetype exists"""
		codec = self.mimetype.codec
		if codec:
			if self.data is None and not data:
				return
			data = data[0] if data else self.data
			value = codec.encode(data, self.encoding, self.mimetype)
			self.set(value)
			self.data = data

	def iterencode(self, *data):
		codec = self.mimetype.codec
		if codec:
			data = data[0] if data else self.data
			value = codec.iterencode(data, self.encoding, self.mimetype)
			self.set(value)
			self.data = data

	def decode(self, *data):
		u"""Decodes the body content if a codec for the mimetype exists.
			Stores the decoded object in :attr:`data`
		"""
		codec = self.mimetype.codec
		if data:
			self.set(data[0])
		if codec:
			self.data = codec.decode(self.__content_bytes(), self.encoding, self.mimetype)

	def compress(self):
		u"""Applies the Content-Encoding codec to the content"""
		codec = self.content_codec
		if codec:
			self.set(codec.encode(self.__content_bytes()))

	def set(self, content):
		if isinstance(content, Body):
			self.mimetype = content.mimetype
			self.data = content.data
			self.chunked = content.chunked
			self.trailer = content.trailer
			self.content = content.content
			return

		self.data = None
		if not content:
			content = BytesIO()
		elif isinstance(content, (BytesIO, file)):
			if content.closed:
				raise TypeError('I/O operation on closed file.')
		elif isinstance(content, Unicode):
			content = BytesIO(content.encode(self.encoding))
		elif isinstance(content, bytes):
			content = BytesIO(content)
		elif isinstance(content, bytearray):
			content = BytesIO(bytes(content))
		elif not hasattr(content, '__iter__'):
			raise TypeError('Content must be iterable.')
		self.content = content

	def parse(self, data):
		if self.transfer_codec:
			data = self.transfer_codec.decode(data)

		if self.content_codec:
			data = self.transfer_codec.decode(data)

		self.write(data)

	def compose(self):
		return b''.join(self.__iter__())

	def close(self):
		super(Body, self).close()
		if isinstance(self.content, (file, BytesIO)):
			self.set('')

	def __unicode__(self):
		return self.__content_bytes().decode(self.encoding)

	def __iter__(self):
		u"""Iterates over the content applying Content-Encoding and Transfer-Encoding"""
		data = self.__content_iter()
		for codec in (self.content_codec, self.transfer_codec):
			if codec:
				data = (codec.encode(d) for d in data)
		if self.chunked:
			data = self.__compose_chunked_iter(data)
		return data

	def __compose_chunked_iter(self, iterable):
		for data in iterable:
			if not data:
				continue
			yield b"%x\r\n%s\r\n" % (len(data), data)
		if self.trailer:
			yield b"0\r\n%s" % bytes(self.trailer)
		else:
			yield b"0\r\n\r\n"

	def __content_bytes(self):
		return b''.join(self.__content_iter())

	def __content_iter(self):
		encoding = self.encoding
		iterable = self.__iterable()

		t = self.tell()
		self.seek(0)

		try:
			for data in iterable:
				if isinstance(data, Unicode):
					data = data.encode(encoding)
				elif not isinstance(data, bytes):
					raise TypeError('Iterable contained non-bytes')
				yield data
		finally:
			self.seek(t)

	def __iterable(self):
		if self.fileable:
			return self.__iter_fileable()
		return self.content

	def __iter_fileable(self, chunksize=MAX_CHUNK_SIZE):
		data = self.read(chunksize)
		while data:
			yield data
			data = self.read(chunksize)

#	def __copy__(self):
#		body = self.__class__(self.__content_bytes())
#		body.mimetype = self.mimetype
#		body.data = self.data
#		body.transfer_encoding = self.transfer_encoding
#		body.content_encoding = self.content_encoding
#		return body

	def __bool__(self):
		return bool(len(self))

	def __len__(self):
		body = self.content

		if isinstance(body, file):  # FIXME: py3
			return getsize(body.name)
		if isinstance(body, BytesIO):
			return len(body.getvalue())

		content = self.__content_bytes()
		self.set(content)
		return len(content)

	def __next__(self):
		if self.__iter is None:
			self.__iter = self.__iter__()
		try:
			return next(self.__iter)
		except StopIteration:
			self.__iter = None
			raise
	next = __next__
