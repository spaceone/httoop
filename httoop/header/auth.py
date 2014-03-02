# -*- coding: utf-8 -*-

from httoop.header.element import HeaderElement


class Authorization(HeaderElement):
	pass


class ProxyAuthenticate(HeaderElement):
	__name__ = 'Proxy-Authenticate'


class ProxyAuthorization(HeaderElement):
	__name__ = 'Proxy-Authorization'


class WWWAuthenticate(HeaderElement):
	__name__ = 'WWW-Authenticate'
