# -*- coding: utf-8 -*-
"""Security related header."""

import re
from typing import List

from httoop.header.element import HeaderElement
from httoop.uri.http import HTTPS
from httoop.util import integer


class ContentSecurityPolicy(HeaderElement):
	"""Content security policy (CSP).

	Prevent content injection vulnerabilities e.g. Cross Site Scripting.

	..seealso:: http://www.w3.org/TR/CSP2/
	"""

	__name__ = 'Content-Security-Policy'
	is_response_header = True

	RE_SPLIT = re.compile(b';')
	RE_PARAMS = re.compile(b'\\s+')

	def compose(self) -> bytes:
		return b'%s %s; ' % (self.value.encode('ISO8859-1'), b' '.join(self.params.keys()))


class ContentSecurityPolicyReportOnly(ContentSecurityPolicy):
	__name__ = 'Content-Security-Policy-Report-Only'
	is_response_header = True


class StrictTransportSecurity(HeaderElement):
	"""HTTP strict transport security (HSTS).

	Enforce secure connection.

	..seealso:: :rfc:`rfc6797`
	"""

	__name__ = 'Strict-Transport-Security'
	is_response_header = True

	@property
	def include_sub_domains(self) -> bool:
		return 'includesubdomains' in self.params

	@property
	def max_age(self) -> int:
		return integer(self.value.split(u'=', 1)[1])  # TODO: more generic parsing


class ContentTypeOptions(HeaderElement):
	"""Content Type options.

	"nosniff" forces user agents to strictly evaluate the Content-Type response header.
	"""

	__name__ = 'X-Content-Type-Options'
	is_response_header = True

	@property
	def nosniff(self) -> bool:
		return self == 'nosniff'


class FrameOptions(HeaderElement):
	"""Frame Options.

	(Dis)allow to display the resource in a HTML frameset/iframe.
	Prevents clickjacking attacks.

	..seealso:: :rfc:`7034`
	"""

	__name__ = 'X-Frame-Options'
	is_response_header = True

	RE_PARAMS = re.compile(b'\\s+')

	@property
	def deny(self) -> bool:
		return self.value.upper() == 'DENY'

	@property
	def same_origin(self) -> bool:
		return self.value.upper() == 'SAMEORIGIN'

	@property
	def allow_from(self) -> List[HTTPS]:
		if self.value.upper() == 'ALLOW-FROM':
			from httoop.uri import URI
			return [URI(uri) for uri in self.params.keys()]


class PermittedCrossDomainPolicies(HeaderElement):
	__name__ = 'X-Permitted-Cross-Domain-Policies'
	is_response_header = True


class PublicKeyPins(HeaderElement):
	"""Public Key Pinning Extension for HTTP (HPKP)."""

	__name__ = 'Public-Key-Pins'
	is_response_header = True


class XSSProtection(HeaderElement):
	"""Cross site scripting (XSS) protection.

	Enable cross site scripting filter in the user agent.
	"""

	__name__ = 'X-XSS-Protection'
	is_response_header = True

	@property
	def enabled(self) -> bool:
		return self == '1'

	@property
	def block(self) -> bool:
		return self.params.get('mode') == 'block'
