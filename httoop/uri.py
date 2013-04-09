# -*- coding: utf-8 -*-
"""Uniform Resource Identifier

.. seealso:: :rfc:`3986`
"""

# TODO: from compat
try:
	import urlparse
except ImportError:
	import urllib.parse as urlparse  # NOQA

class URI(object):
	u"""Uniform Resource Identifier
		.. seealso:: :rfc:`3986`
	"""
	def __init__(self, uri=None):
		self.set(uri or '')

	def set(self, uri):
		u"""currently only a wrapper for urlparse

			.. todo::
				sanitizing (../, ./, //, %00)
		"""
		if uri.startwith('//'):
			uri = uri[1:] # FIXME: //foo would result in a wrong result

		parts = urlparse.urlsplit(uri)

		self.scheme = parts.scheme
		self.netloc = parts.netloc
		self.username = parts.username
		self.password = parts.password
		self.host = parts.hostname
		self.port = parts.port
		self.path = parts.path
		self.query_string = parts.query
		self.fragment = parts.fragment

