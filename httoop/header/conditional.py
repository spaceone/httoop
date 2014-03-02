# -*- coding: utf-8 -*-

from httoop.header.element import HeaderElement


class ETag(HeaderElement):
	pass


class LastModified(HeaderElement):
	__name__ = 'Last-Modified'


class IfMatch(HeaderElement):
	__name__ = 'If-Match'


class IfModifiedSince(HeaderElement):
	__name__ = 'If-Modified-Since'


class IfNoneMatch(HeaderElement):
	__name__ = 'If-None-Match'


class IfUnmodifiedSince(HeaderElement):
	__name__ = 'If-Unmodified-Since'
