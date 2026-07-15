"""Security related header."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from httoop.header.element import HeaderElement
from httoop.util import integer


if TYPE_CHECKING:
    from httoop.uri.http import HTTPS


class ContentSecurityPolicy(HeaderElement, name='Content-Security-Policy'):
    """
    Content security policy (CSP).

    Prevent content injection vulnerabilities e.g. Cross Site Scripting.

    ..seealso:: http://www.w3.org/TR/CSP2/
    """

    is_response_header = True

    RE_SPLIT = re.compile(rb';')
    RE_PARAMS = re.compile(rb'\\s+')

    def compose(self) -> bytes:
        return b'%s %s; ' % (self.value.encode('ISO8859-1'), b' '.join(self.params.keys()))


class ContentSecurityPolicyReportOnly(ContentSecurityPolicy, name='Content-Security-Policy-Report-Only'):

    is_response_header = True


class StrictTransportSecurity(HeaderElement, name='Strict-Transport-Security'):
    """
    HTTP strict transport security (HSTS).

    Enforce secure connection.

    ..seealso:: :rfc:`rfc6797`
    """

    is_response_header = True

    @property
    def include_sub_domains(self) -> bool:
        return 'includesubdomains' in self.params

    @property
    def max_age(self) -> int:
        return integer(self.value.split('=', 1)[1])  # TODO: more generic parsing


class ContentTypeOptions(HeaderElement, name='X-Content-Type-Options'):
    """
    Content Type options.

    "nosniff" forces user agents to strictly evaluate the Content-Type response header.
    """

    is_response_header = True

    @property
    def nosniff(self) -> bool:
        return self == 'nosniff'


class FrameOptions(HeaderElement, name='X-Frame-Options'):
    """
    Frame Options.

    (Dis)allow to display the resource in a HTML frameset/iframe.
    Prevents clickjacking attacks.

    ..seealso:: :rfc:`7034`
    """

    is_response_header = True

    RE_PARAMS = re.compile(rb'\\s+')

    @property
    def deny(self) -> bool:
        return self.value.upper() == 'DENY'

    @property
    def same_origin(self) -> bool:
        return self.value.upper() == 'SAMEORIGIN'

    @property
    def allow_from(self) -> list[HTTPS] | None:
        if self.value.upper() == 'ALLOW-FROM':
            from httoop.uri import URI  # noqa: PLC0415

            return [URI(uri) for uri in self.params]
        return None


class PermittedCrossDomainPolicies(HeaderElement, name='X-Permitted-Cross-Domain-Policies'):

    is_response_header = True


class PublicKeyPins(HeaderElement, name='Public-Key-Pins'):
    """Public Key Pinning Extension for HTTP (HPKP)."""

    is_response_header = True


class XSSProtection(HeaderElement, name='X-XSS-Protection'):
    """
    Cross site scripting (XSS) protection.

    Enable cross site scripting filter in the user agent.
    """

    is_response_header = True

    @property
    def enabled(self) -> bool:
        return self == '1'

    @property
    def block(self) -> bool:
        return self.params.get('mode') == 'block'
