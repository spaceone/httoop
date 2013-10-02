# -*- coding: utf-8 -*-
"""Uniform Resource Identifier

.. seealso:: :rfc:`3986`
"""

from httoop.exceptions import InvalidURI
from httoop.util import ByteString, urlparse

import re


# TODO: think about the naming.. this is atm an HTTP URL
class URI(ByteString):
	u"""Uniform Resource Identifier

		.. seealso:: :rfc:`3986`

		.. seealso:: :rfc:`2616#section-3.2`

		.. seealso:: :rfc:`2616#section-3.2.2`

	"""
	def __init__(self, uri=None):
		self.parse(uri or '')

	def parse(self, uri):
		u"""currently only a wrapper for urlparse

			.. todo::
				sanitizing (../, ./, //, %00)
		"""
		self.uri = uri
		# TODO: remove this? A URI MUST NOT start with //
		if uri.startswith('//'):
			uri = uri[1:]  # FIXME: //foo would result in a wrong result

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
		if self.fragment:
			pass
		elif self.username:
			pass
		elif self.password:
			pass
		elif not self.path:
			pass
		elif (self.path != '*' and self.path[0] != '/'):
			pass
		else:
			return
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

	def set(self, uri):
		if not isinstance(uri, URI):
			self.parse(uri)
		else:
			# don't parse again because it might was sanitize()d
			self.__dict__.update(dict(
				uri=uri.uri,
				scheme=uri.scheme.lower(),
				netloc=uri.netloc,
				username=uri.username,
				password=uri.password,
				host=uri.host.lower(),
				port=uri.port,
				path=uri.path or '',
				query_string=uri.query_string,
				fragment=uri.fragment
			))

	def __eq__(self, other):
		# TODO: RFC 2616 Section 3.2.3
		pass

	def __bytes__(self):
		# TODO: we don't know if we need to get the abspath or a relpath
		return self.path

	def __repr__(self):
		return '<URI(host=%r, path=%r)>' % (self.host, self.path)
