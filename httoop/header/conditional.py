# -*- coding: utf-8 -*-

from httoop.header.element import HeaderElement
from httoop.date import Date
from httoop.exceptions import InvalidDate


class _DateComparable(object):

	Date = Date

	def sanitize(self):
		super(_DateComparable, self).sanitize()
		self.value = self.Date.parse(self.value)

	def __eq__(self, other):
		#super(_DateComparable, self).__eq__(other)
		if not isinstance(other, Date):
			try:
				other = Date(other)
			except InvalidDate:
				return False
		return self.value == other


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
