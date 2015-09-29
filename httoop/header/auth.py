# -*- coding: utf-8 -*-

from httoop.authentication import AuthRequestElement, AuthResponseElement, AuthInfoElement
from httoop.header.element import _HopByHopElement


class Authorization(AuthRequestElement):
	pass


class ProxyAuthenticate(_HopByHopElement, AuthResponseElement):
	__name__ = 'Proxy-Authenticate'


class ProxyAuthorization(_HopByHopElement, AuthRequestElement):
	__name__ = 'Proxy-Authorization'


class WWWAuthenticate(AuthResponseElement):
	__name__ = 'WWW-Authenticate'


class AuthenticationInfo(AuthInfoElement):
	__name__ = 'Authentication-Info'


class ProxyAuthenticationInfo(_HopByHopElement, AuthInfoElement):
	__name__ = 'Proxy-Authentication-Info'


del AuthResponseElement, AuthRequestElement, AuthInfoElement
