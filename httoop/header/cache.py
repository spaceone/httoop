# -*- coding: utf-8 -*-

from httoop.header.element import HeaderElement


class Age(HeaderElement):
	pass


class CacheControl(HeaderElement):
	__name__ = 'Cache-Control'


class Expires(HeaderElement):
	pass


class Pragma(HeaderElement):
	pass


class Vary(HeaderElement):
	pass


class Warning(HeaderElement):  # pylint: disable=W0622
	pass
