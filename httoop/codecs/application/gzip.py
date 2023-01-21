# -*- coding: utf-8 -*-

from __future__ import absolute_import

import gzip
import io
import zlib

from httoop.codecs.codec import Codec
from httoop.exceptions import DecodeError, EncodeError
from httoop.util import _


class GZip(Codec):
	mimetype = 'application/gzip'

	compression_level = 6

	@classmethod
	def encode(cls, data: bytes, charset: None=None, mimetype: None=None) -> bytes:
		try:
			out = io.BytesIO()
			with gzip.GzipFile(fileobj=out, mode="w", compresslevel=cls.compression_level) as fd:
				fd.write(Codec.encode(data, charset))
			return out.getvalue()
		except zlib.error:  # pragma: no cover
			raise EncodeError(_(u'Invalid gzip data.'))

	@classmethod
	def decode(cls, data: bytes, charset: None=None, mimetype: None=None) -> str:
		try:
			with gzip.GzipFile(fileobj=io.BytesIO(data)) as fd:
				data = fd.read()
		except (zlib.error, IOError, EOFError):
			raise DecodeError(_(u'Invalid gzip data.'))
		return Codec.decode(data, charset)

	@classmethod
	def iterencode(cls, data, charset=None, mimetype=None):
		try:
			out = io.BytesIO()
			with gzip.GzipFile(fileobj=out, mode="w", compresslevel=cls.compression_level) as fd:
				for part in data:
					fd.write(Codec.encode(part, charset))
					yield out.getvalue()
					out.seek(0)
					out.truncate()
			yield out.getvalue()
		except zlib.error:  # pragma: no cover
			raise EncodeError(_(u'Invalid gzip data.'))

	@classmethod
	def iterdecode(cls, data, charset=None, mimetype=None):
		try:
			fd = io.BytesIO()
			with gzip.GzipFile(fileobj=fd) as gzfd:
				# FIXME: the gzip module cannot handle partial data
				#for part in data:
				#	fd.write(part)
				#	fd.seek(fd.tell() - length)
				#	fd.seek(fd.tell() - length)
				#	yield Codec.decode(gzfd.read(), charset)
				#yield Codec.decode(gzfd.read(), charset)
				for part in data:
					fd.write(part)
				fd.seek(0)
				yield Codec.decode(gzfd.read(), charset)
		except (zlib.error, IOError, EOFError):
			raise DecodeError(_(u'Invalid gzip data.'))
