# -*- coding: utf-8 -*-
"""HTTP request and response body

.. seealso:: :rfc:`2616#section-4.3`
"""

from os.path import getsize
from io import BytesIO # hmm, six implements StringIO for this, which is wrong...

from httoop.headers import Headers
from httoop.util import ByteString, text_type, binary_type

# TODO: implement a nice way to support files, BytesIO and iterables, with methods to write, truncate, tell, read, etc.
# We need to support the following cases:
# 	response.body = open(filename)
# 	response.body = u''
# 	response.body = b''
# 	response.body = ['this', 'is', 'a', 'chunk'] → if we want to send chunked output
# 	response.body = BytesIO('')

def get_bytes_from_unknown(unistr):
	for encoding in ('UTF-8', 'ISO8859-1'):
		try:
			return unistr.encode(encoding)
		except UnicodeEncodeError:
			pass

class Body(ByteString):
	u"""A HTTP message body"""

	@property
	def chunked(self):
		return isinstance(self, ChunkedBody)

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
				body = BytesIO(body.encode('UTF-8'))
			elif isinstance(body, binary_type):
				body = BytesIO(body)
			elif isinstance(body, Body):
				body = body.content
		self.content = body

	def __bytes__(self):
		bytesio = self.content
		if not hasattr(bytesio, 'tell'):
			return str(bytesio) # FIXME: don't allow dicts anymore
		t = bytesio.tell()
		bytesio.seek(0)
		body = bytesio.read()
		bytesio.seek(t)

		if isinstance(bytesio, file) and bytesio.encoding is not None:
			body = body.encode(bytesio.encoding)

		return body

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

		return len(bytes(self))

	# the file interface
	def close(self):
		return self.content.close()

	def flush(self):
		return self.content.flush()

	def read(self, *size):
		return self.content.read(*size[:1])

	def write(self, bytes_):
		return self.content.write(bytes_)

	def seek(self, offset, whence=0):
		return self.content.seek(offset, whence)

	def tell(self):
		return self.content.tell()

	def truncate(self, size=None):
		return self.content.truncate(size)

	def __repr__(self):
		return '<HTTP Body(%d)>' % len(self)

# TODO: add iterable to list, tuple
class ChunkedBody(Body):
	u"""A body which consists of an iterable (to support WSGI)
	"""

	def __init__(self, body=None):
		super(ChunkedBody, self).__init__(body)
		self.trailer = Headers()

	def parse(self, data):
		pass

	def set(self, body):
		if isinstance(body, (list, tuple)):
			self.content = body
		super(ChunkedBody, self).set(body)

	def __len__(self):
		body = self.content
		if isinstance(body, (list, tuple)):
			return len(body) # FIXME
		return super(ChunkedBody, self).__len__()

	def __bytes__(self):
		return self.compose()

	def __repr__(self):
		return '<ChunkedBody(%d)>' % len(self)

	def compose(self):
		while True:
			try:
				data = next(self)
				yield "%s\r\n%s\r\n" % (hex(len(data))[2:], data)
			except StopIteration:
				break
		if self.trailer is not None:
			yield b"0\r\n%s" % bytes(self.trailer)
		else:
			yield b"0\r\n\r\n"

