# -*- coding: utf-8 -*-

from httoop.header.element import HeaderElement


class _DateComparable(object):
	from httoop.date import Date
	def sanitize(self):
		self.value = self.Date.parse(self.value)

class ETag(HeaderElement):
	pass


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
