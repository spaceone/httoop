# -*- coding: utf-8 -*-

from httoop.authentication import AuthRequestElement, AuthResponseElement, AuthInfoElement
from httoop.header.element import _HopByHopElement, _ListElement


class Authorization(AuthRequestElement):
	is_request_header = True


class ProxyAuthenticate(_ListElement, _HopByHopElement, AuthResponseElement):
	__name__ = 'Proxy-Authenticate'
	is_response_header = True


class ProxyAuthorization(_HopByHopElement, AuthRequestElement):
	__name__ = 'Proxy-Authorization'
	is_request_header = True


class WWWAuthenticate(_ListElement, AuthResponseElement):
	__name__ = 'WWW-Authenticate'
	is_response_header = True


class AuthenticationInfo(AuthInfoElement):
	__name__ = 'Authentication-Info'
	is_response_header = True


class ProxyAuthenticationInfo(_HopByHopElement, AuthInfoElement):
	__name__ = 'Proxy-Authentication-Info'
	is_response_header = True


del AuthResponseElement, AuthRequestElement, AuthInfoElement
