# -*- coding: utf-8 -*-

from httoop.header.element import HeaderElement


class _DateComparable(object):
	from httoop.date import Date
	def sanitize(self):
		self.value = self.Date.parse(self.value)

class ETag(HeaderElement):

	def __eq__(self, other):
		if not isinstance(other, ETag):
			other = self.__class__(other)
		return other.value == self.value or other.value == '*'


class LastModified(_DateComparable, HeaderElement):
	__name__ = 'Last-Modified'


class IfMatch(HeaderElement):
	__name__ = 'If-Match'


class IfModifiedSince(_DateComparable, HeaderElement):
	__name__ = 'If-Modified-Since'


class IfNoneMatch(HeaderElement):
	__name__ = 'If-None-Match'


class IfUnmodifiedSince(_DateComparable, HeaderElement):
	__name__ = 'If-Unmodified-Since'
