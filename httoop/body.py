# -*- coding: utf-8 -*-
"""HTTP request and response body

.. seealso:: :rfc:`2616#section-4.3`
"""

from os.path import getsize
from io import BytesIO  # hmm, six implements StringIO for this, which is wrong...

from httoop.exceptions import InvalidBody
from httoop.headers import Headers
from httoop.util import ByteString, IFile, text_type, binary_type, get_bytes_from_unknown, file_generator


class Body(IFile, ByteString):
	u"""A HTTP message body"""

	@property
	def chunked(self):
		return isinstance(self, ChunkedBody)

	@property
	def fileable(self):
		return all(hasattr(self.content, method) for method in ('read', 'write', 'close'))

	def __init__(self, body=None, encoding=None):
		self.content = BytesIO()
		self.encoding = encoding

		if body is not None:
			self.set(body)

	def set(self, body):
		if not isinstance(body, (BytesIO, file)):
			if not body:
				body = BytesIO()
			elif isinstance(body, text_type):
				body = BytesIO(body.encode(self.encoding or 'UTF-8'))
			elif isinstance(body, binary_type):
				body = BytesIO(body)
			elif isinstance(body, Body):
				body = body.content
			elif not hasattr(body, '__iter__'):
				raise InvalidBody() # TODO: description
		self.content = body

	def compose(self):
		if not self.fileable:
			return b''.join(self.content)  # TODO: map(any_to_bytes, self.content)

		t = self.tell()
		self.seek(0)
		body = self.read()
		self.seek(t)

		if getattr(self.content, 'encoding', None) is not None:
			# we have a real file here
			body = body.encode(self.content.encoding)

		return body

	def __bytes__(self):
		return self.compose()

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

		return len(Body.compose(self))

	def __iter__(self):
		if isinstance(self.content, file):
			# don't iterate over every single byte
			return file_generator(self.content)
		if hasattr(self.content, '__iter__'):
			return self.content.__iter__
		return [Body.compose(self)].__iter__

	def __repr__(self):
		return '<HTTP Body(%d)>' % len(self)


class ChunkedBody(Body):
	u"""A body which can consists of any iterable"""

	def __init__(self, body=None, encoding=None):
		super(ChunkedBody, self).__init__(body, encoding)
		self.trailer = Headers()

	def parse(self, data):
		pass

	def compose(self):
		while True:
			try:
				data = next(self.content)
				yield "%s\r\n%s\r\n" % (hex(len(data))[2:], data)
			except StopIteration:
				break
		if self.trailer:
			yield b"0\r\n%s" % bytes(self.trailer)
		else:
			yield b"0\r\n\r\n"

	def __repr__(self):
		return '<ChunkedBody(%d)>' % len(self)
