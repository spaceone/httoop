# -*- coding: utf-8 -*-
"""Uniform Resource Identifier

.. seealso:: :rfc:`3986`
"""

from httoop.exceptions import InvalidURI

# TODO: from compat
try:
	import urlparse
except ImportError:
	import urllib.parse as urlparse  # NOQA

# TODO: think about the naming.. this is atm an HTTP URL
class URI(object):
	u"""Uniform Resource Identifier
		.. seealso:: :rfc:`3986`
	"""
	def __init__(self, uri=None):
		self.parse(uri or '')

	def parse(self, uri):
		u"""currently only a wrapper for urlparse

			.. todo::
				sanitizing (../, ./, //, %00)
		"""
		self.uri = uri
		if uri.startswith('//'):
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

		if self.uri.startswith('//'):
			self.path = '/%s' % self.path

		self.validate_http_uri()

	def validate_http_uri(self):
		if not self.fragment and\
			not self.username and\
			not self.password and\
			self.path and\
			(self.path[0] == '/' or self.path == '*'):
				raise InvalidURI(self.uri)

	# this is ripped from url-parse project which is MIT licensed
	def abspath(self):
		"""Clear out any '..' and excessive slashes from the path"""
		# Remove double forward-slashes from the path
		path = re.sub(b'\/{2,}', b'/', self.path)
		# With that done, go through and remove all the relative references
		unsplit = []
		for part in path.split(b'/'):
			# If we encounter the parent directory, and there's
			# a segment to pop off, then we should pop it off.
			if part == b'..' and (not unsplit or unsplit.pop() is not None):
				pass
			elif part != b'.':
				unsplit.append(part)

		# With all these pieces, assemble!
		if self.path.endswith(b'.'):
			# If the path ends with a period, then it refers to a directory,
			# not a file path
			self.path = b'/'.join(unsplit) + b'/'
		else:
			self.path = b'/'.join(unsplit)
		return self

	def sanitize(self):
		return self.abspath()
