# -*- coding: utf-8 -*-

from httoop.header.element import HeaderElement


class Age(HeaderElement):

	is_response_header = True


class CacheControl(HeaderElement):
	__name__ = 'Cache-Control'

	is_request_header = True
	is_response_header = True


class Expires(HeaderElement):

	is_response_header = True


class Pragma(HeaderElement):

	is_response_header = True


class Vary(HeaderElement):

	is_response_header = True


class Warning(HeaderElement):  # pylint: disable=W0622

	is_response_header = True
