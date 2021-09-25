# -*- coding: utf-8 -*-

from httoop.date import Date
from httoop.exceptions import InvalidDate
from httoop.header.element import HeaderElement


class _DateComparable(object):

	Date = Date

	def sanitize(self):
		super(_DateComparable, self).sanitize()
		self.value = self.Date.parse(self.value.encode('ASCII', 'replace'))

	def __eq__(self, other):
		if not isinstance(other, Date):
			if isinstance(other, _DateComparable):
				other = int(other)
			try:
				other = Date(other)
			except InvalidDate:
				return False
		return self.value == other

	def __int__(self):
		return int(self.value)


class ETag(HeaderElement):

	is_response_header = True

	def __eq__(self, other):
		if not isinstance(other, ETag):
			other = self.__class__(other)
		return other.value == self.value or other.value == '*'


class LastModified(_DateComparable, HeaderElement):
	__name__ = 'Last-Modified'
	is_response_header = True


class IfMatch(HeaderElement):
	__name__ = 'If-Match'
	is_request_header = True


class IfModifiedSince(_DateComparable, HeaderElement):
	__name__ = 'If-Modified-Since'
	is_request_header = True


class IfNoneMatch(HeaderElement):
	__name__ = 'If-None-Match'
	is_request_header = True


class IfUnmodifiedSince(_DateComparable, HeaderElement):
	__name__ = 'If-Unmodified-Since'
	is_request_header = True
