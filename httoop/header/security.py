# -*- coding: utf-8 -*-
"""Security related header"""

import re

from httoop.header.element import HeaderElement


class ContentSecurityPolicy(HeaderElement):
	"""Content security policy (CSP).

		Prevent content injection vulnerabilities e.g. Cross Site Scripting.

		..seealso:: http://www.w3.org/TR/CSP2/
	"""

	__name__ = 'Content-Security-Policy'
	is_response_header = True

	RE_SPLIT = re.compile(b';')
	RE_PARAMS = re.compile(b'\\s+')

	def compose(self):
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
	def include_sub_domains(self):
		return 'includeSubDomains' in self.params


class ContentTypeOptions(HeaderElement):
	"""Content Type options.

		"nosniff" forces user agents to strictly evaluate the Content-Type response header.
	"""

	__name__ = 'X-Content-Type-Options'
	is_response_header = True

	@property
	def nosniff(self):
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
	def deny(self):
		return self.value == 'DENY'

	@property
	def same_origin(self):
		return self.value == 'SAMEORIGIN'

	@property
	def allow_from(self):
		if self.value == 'ALLOW-FROM':
			return self.params


class PermittedCrossDomainPolicies(HeaderElement):
	__name__ = 'X-Permitted-Cross-Domain-Policies'
	is_response_header = True


class PublicKeyPins(HeaderElement):
	"""Public Key Pinning Extension for HTTP (HPKP)"""
	__name__ = 'Public-Key-Pins'
	is_response_header = True


class XSSProtection(HeaderElement):
	"""Cross site scripting (XSS) protection.

		Enable cross site scripting filter in the user agent.
	"""

	__name__ = 'X-XSS-Protection'
	is_response_header = True

	@property
	def enabled(self):
		return self == '1'

	@property
	def block(self):
		return self.params.get('mode') == 'block'
