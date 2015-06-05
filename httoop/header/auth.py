# -*- coding: utf-8 -*-

from httoop.authentication import AuthRequestElement, AuthResponseElement, AuthInfoElement


class Authorization(AuthRequestElement):
	pass


class ProxyAuthenticate(AuthResponseElement):
	__name__ = 'Proxy-Authenticate'


class ProxyAuthorization(AuthRequestElement):
	__name__ = 'Proxy-Authorization'


class WWWAuthenticate(AuthResponseElement):
	__name__ = 'WWW-Authenticate'


class AuthenticationInfo(AuthInfoElement):
	__name__ = 'Authentication-Info'


class ProxyAuthenticationInfo(AuthInfoElement):
	__name__ = 'Proxy-Authentication-Info'


del AuthResponseElement, AuthRequestElement, AuthInfoElement
