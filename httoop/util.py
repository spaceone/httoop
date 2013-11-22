# -*- coding: utf-8 -*-
u"""Utilities for python2/3 compatibility"""

__all__ = [
	'PY3', 'Unicode', 'BytesIO', 'iteritems',
	'to_unicode', 'to_ascii', 'get_bytes_from_unknown',
	'IFile', 'partial', 'formatdate', 'parsedate'
]

import sys
from functools import partial

PY3 = sys.version_info[0] == 3

try:
	Unicode = unicode
except NameError:
	Unicode = str

from io import BytesIO

try:
	from email.utils import formatdate, parsedate
	formatdate = partial(formatdate, usegmt=True)
except ImportError:
	from rfc822 import formatdate, parsedate


def iteritems(d, **kw):
	return iter(getattr(d, 'items' if PY3 else 'iteritems')(**kw))


def to_unicode(string):
	if isinstance(string, type):
		# FIXME FIXME: CaseInsensitiveDict is also used for Header elements
		return string
	if string is None:
		return u''
	if isinstance(string, bytes):
		try:
			return string.decode('UTF-8')
		except UnicodeDecodeError:
			return string.decode('ISO8859-1')
	return Unicode(string)


def to_ascii(string):
	if isinstance(string, Unicode):
		return string.encode('ascii', 'ignore')
	return bytes(string).decode('ascii', 'ignore').encode('ascii')


def get_bytes_from_unknown(unistr):
	for encoding in ('UTF-8', 'ISO8859-1'):
		try:
			return unistr.encode(encoding)
		except UnicodeEncodeError:
			pass


def if_has(func):
	def _decorated(self, *args, **kwargs):
		if hasattr(self.content, func.__name__):
			return func(self, *args, **kwargs)
		return False
	return _decorated


class IFile(object):
	u"""The file interface"""
	__slots__ = ('content')

	@if_has
	def close(self):
		return self.content.close()

	@if_has
	def flush(self):
		return self.content.flush()

	@if_has
	def read(self, *size):
		return self.content.read(*size[:1])

	@if_has
	def readline(self, *size):
		return self.content.readline(*size[:1])

	@if_has
	def readlines(self, *size):
		return self.content.readlines(*size[:1])

	@if_has
	def write(self, bytes_):
		return self.content.write(bytes_)

	@if_has
	def writelines(self, sequence_of_strings):
		return self.content.writelines(sequence_of_strings)

	@if_has
	def seek(self, offset, whence=0):
		return self.content.seek(offset, whence)

	@if_has
	def tell(self):
		return self.content.tell()

	@if_has
	def truncate(self, size=None):
		return self.content.truncate(size)


class CaseInsensitiveDict(dict):
	"""A case-insensitive dict subclass optimized for HTTP header use.

		Each key is stored as case insensitive ascii
		Each value is stored as unicode
	"""

	def __init__(self, *args, **kwargs):
		d = dict(*args, **kwargs)
		for key, value in iteritems(d):
			dict.__setitem__(self, to_ascii(key).title(), to_unicode(value))
		dict.__init__(self)

	def __getitem__(self, key):
		return dict.__getitem__(self, to_ascii(key).title())

	def __setitem__(self, key, value):
		dict.__setitem__(self, to_ascii(key).title(), to_unicode(value))

	def __delitem__(self, key):
		dict.__delitem__(self, to_ascii(key).title())

	def __contains__(self, key):
		return dict.__contains__(self, to_ascii(key).title())

	def get(self, key, default=None):
		return dict.get(self, to_ascii(key).title(), default)

	def update(self, E):
		for k in E.keys():
			self[to_ascii(k).title()] = to_unicode(E[k])

	def setdefault(self, key, x=None):
		key = to_ascii(key).title()
		try:
			return dict.__getitem__(self, key)
		except KeyError:
			self[key] = to_unicode(x)
			return dict.__getitem__(self, key)

	def pop(self, key, default=None):
		return dict.pop(self, to_ascii(key).title(), default)

	@classmethod
	def fromkeys(cls, seq, value=None):
		newdict = cls()
		for k in seq:
			newdict[k] = to_unicode(value)
		return newdict
