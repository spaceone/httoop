# -*- coding: utf-8 -*-
"""HTTP URLs
	.. seealso:: :rfc:`2616#section-3.2`

	.. seealso:: :rfc:`2616#section-3.2.2`
"""

from httoop.uri.uri import URI
from httoop.util import Unicode, _
from httoop.exceptions import InvalidURI


class HTTP(URI):
	SCHEME = b'http'
	PORT = 80

	parse_relative = URI.parse  # TODO: implement
	def validate(self):
		if self.fragment:
			pass
		elif self.username:
			pass
		elif self.password:
			pass
		elif not self.path:
			pass
		elif self.path.startswith(b'//'):
			pass
		elif self.path != u'*' and self.path[0] != u'/':
			pass
		else:
			return
		raise InvalidURI(_(u'Invalid URI: %s'), Unicode(self))


class HTTPS(HTTP):
	SCHEME = b'HTTPS'
	PORT = 443
