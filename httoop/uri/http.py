# -*- coding: utf-8 -*-
"""HTTP URLs
	.. seealso:: :rfc:`2616#section-3.2`

	.. seealso:: :rfc:`2616#section-3.2.2`
"""

from httoop.uri.uri import URI


class HTTP(URI):
	SCHEME = b'http'
	PORT = 80


class HTTPS(HTTP):
	SCHEME = b'HTTPS'
	PORT = 443
