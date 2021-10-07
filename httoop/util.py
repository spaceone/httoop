# -*- coding: utf-8 -*-
u"""Utilities for python2/3 compatibility"""

from __future__ import absolute_import

import codecs
import sys
from email.generator import _make_boundary as make_boundary
from functools import partial

try:
	from email.utils import parsedate_tz as parsedate
except ImportError:  # pragma: no cover
	from rfc822 import parsedate_tz as parsedate

try:
	from email.Header import decode_header
except ImportError:  # pragma: no cover
	from email.header import decode_header

try:
	from itertools import izip
except ImportError:  # pragma: no cover
	izip = zip

try:
	from base64 import decodebytes as decode_base64, encodebytes as encode_base64
except ImportError:  # pragma: no cover
	from base64 import decodestring as decode_base64, encodestring as encode_base64

PY3 = sys.version_info[0] == 3

try:
	Unicode = unicode
except NameError:  # pragma: no cover
	Unicode = str


def _(x):
	return x


__all__ = [
	'PY3', 'Unicode', 'iteritems',
	'to_unicode', 'decode_header',
	'IFile', 'partial', 'parsedate', 'izip',
	'CaseInsensitiveDict',
	'sanitize_encoding', 'make_boundary', '_',
	'encode_base64', 'decode_base64',
	'integer',
]

KNOWN_ENCODINGS = {
	'cp1254', 'cp949', 'cp865', 'cp1257', 'euc_jp', 'cp1250', 'mac-cyrillic', 'mac-latin2', 'cp866', 'cp857',
	'tis-620', 'hp-roman8', 'iso8859-15', 'iso8859-1', 'mac-turkish', 'utf-32', 'cp1252', 'cp861', 'euc_jis_2004',
	'iso8859-6', 'utf-7', 'gb18030', 'iso2022_kr', 'shift_jisx0213', 'shift_jis_2004', 'utf-32-be', 'cp855',
	'utf-8', 'iso8859-2', 'koi8-r', 'iso8859-14', 'cp1251', 'iso8859-11', 'cp424', 'ascii', 'euc_jisx0213',
	'cp863', 'iso2022_jp_ext', 'euc_kr', 'iso2022_jp_2004', 'cp869', 'gb2312', 'utf-16', 'utf-32-le', 'mac-roman',
	'iso8859-10', 'uu', 'iso2022_jp', 'johab', 'cp950', 'cp852', 'iso2022_jp_2', 'iso8859-8', 'cp775', 'shift_jis',
	'utf-16-be', 'cp1255', 'cp1253', 'mac-iceland', 'utf-16-le', 'cp437', 'cp864', 'cp1258', 'cp862', 'cp860',
	'cp850', 'gbk', 'cp858', 'iso8859-3', 'iso8859-4', 'mac-greek', 'iso2022_jp_1', 'ptcp154', 'iso8859-7',
	'iso8859-5', 'cp500', 'iso8859-13', 'iso8859-9', 'cp1256', 'iso8859-16', 'cp932', 'iso2022_jp_3'
}


def sanitize_encoding(encoding):
	try:
		name = codecs.lookup(encoding).name
		if name not in KNOWN_ENCODINGS:
			raise LookupError
	except LookupError:
		return
	return name


def iteritems(d, **kw):
	return iter(getattr(d, 'items' if PY3 else 'iteritems')(**kw))


def to_unicode(string):
	if string is None:
		return u''
	if isinstance(string, bytes):
		try:
			return string.decode('UTF-8')
		except UnicodeDecodeError:
			return string.decode('ISO8859-1')
	return Unicode(string)


def if_has(func):
	def _decorated(self, *args, **kwargs):
		if hasattr(self.fd, func.__name__):
			return func(self, *args, **kwargs)
		return False
	return _decorated


def integer(number, *args):
	"""In Python 3 int() is broken.
	>>> int(bytearray(b'1_0'))
	Traceback (most recent call last):
		...
	ValueError:
	"""
	num = int(number, *args)
	if isinstance(number, str) and '_' in number or isinstance(number, (bytes, bytearray)) and b' ' in number:
		raise ValueError()
	return num


class IFile(object):
	u"""The file interface"""
	__slots__ = ('fd')

	@property
	def name(self):
		return getattr(self.fd, 'name', None)

	@if_has
	def close(self):
		return self.fd.close()

	@if_has
	def flush(self):
		return self.fd.flush()

	@if_has
	def read(self, *size):
		return self.fd.read(*size[:1])

	@if_has
	def readline(self, *size):
		return self.fd.readline(*size[:1])

	@if_has
	def readlines(self, *size):
		return self.fd.readlines(*size[:1])

	@if_has
	def write(self, bytes_):
		return self.fd.write(bytes_)

	@if_has
	def writelines(self, sequence_of_strings):
		return self.fd.writelines(sequence_of_strings)

	@if_has
	def seek(self, offset, whence=0):
		return self.fd.seek(offset, whence)

	@if_has
	def tell(self):
		return self.fd.tell()

	@if_has
	def truncate(self, size=None):
		return self.fd.truncate(size)


class CaseInsensitiveDict(dict):
	"""A case-insensitive dict subclass optimized for HTTP header use.

		Each key is stored as case insensitive ascii
		Each value is stored as unicode
	"""

	__slots__ = ()

	@staticmethod
	def formatkey(key):
		return to_unicode(key).title()

	@staticmethod
	def formatvalue(value):
		return value

	def __init__(self, *args, **kwargs):
		d = dict(*args, **kwargs)
		for key, value in iteritems(d):
			dict.__setitem__(self, self.formatkey(key), self.formatvalue(value))
		dict.__init__(self)

	def __getitem__(self, key):
		return dict.__getitem__(self, self.formatkey(key))

	def __setitem__(self, key, value):
		dict.__setitem__(self, self.formatkey(key), self.formatvalue(value))

	def __delitem__(self, key):
		dict.__delitem__(self, self.formatkey(key))

	def __contains__(self, key):
		return dict.__contains__(self, self.formatkey(key))

	def get(self, key, default=None):
		return dict.get(self, self.formatkey(key), default)

	def update(self, E):
		for key in E.keys():
			self[self.formatkey(key)] = self.formatvalue(E[key])

	def setdefault(self, key, x=None):
		key = self.formatkey(key)
		try:
			return dict.__getitem__(self, key)
		except KeyError:
			self[key] = self.formatvalue(x)
			return dict.__getitem__(self, key)

	def pop(self, key, default=None):
		return dict.pop(self, self.formatkey(key), default)

	@classmethod
	def fromkeys(cls, seq, value=None):
		return cls(dict((key, value) for key in seq))


class ByteUnicodeDict(CaseInsensitiveDict):

	@staticmethod
	def formatkey(key):
		return key if isinstance(key, bytes) else key.encode('UTF-8')


class _Translateable(object):

	def __init__(self, message, *args, **kwargs):
		self.message = message
		self._args = args
		self._kwargs = kwargs
		super(_Translateable, self).__init__(message, args, kwargs)

	def translate(self):
		return self.message % (self._kwargs or self._args)

	def __unicode__(self):
		return self.translate()

	def __bytes__(self):
		return Unicode(self).encode('unicode_escape')

	__str__ = __unicode__ if PY3 else __bytes__
