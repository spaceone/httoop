from httoop.authentication import AuthInfoElement, AuthRequestElement, AuthResponseElement
from httoop.header.element import _HopByHopElement, _ListElement


class Authorization(AuthRequestElement):
    is_request_header = True


class ProxyAuthenticate(_ListElement, _HopByHopElement, AuthResponseElement, name='Proxy-Authenticate'):

    is_response_header = True


class ProxyAuthorization(_HopByHopElement, AuthRequestElement, name='Proxy-Authorization'):

    is_request_header = True


class WWWAuthenticate(_ListElement, AuthResponseElement, name='WWW-Authenticate'):

    is_response_header = True


class AuthenticationInfo(AuthInfoElement, name='Authentication-Info'):

    is_response_header = True


class ProxyAuthenticationInfo(_HopByHopElement, AuthInfoElement, name='Proxy-Authentication-Info'):

    is_response_header = True


del AuthResponseElement, AuthRequestElement, AuthInfoElement
