# -*- coding: utf-8 -*-
"""Uniform Resource Identifier

.. seealso:: :rfc:`3986`
"""

import re
from os.path import join

from httoop.exceptions import InvalidURI
from httoop.util import ByteString, Unicode
from httoop.codecs import CODECS, Percent

DEFAULT_PORTS = {'http': 80, 'https': 443}
QueryString = CODECS['application/x-www-form-urlencoded']

# TODO: allow params?


# TODO: abstracter: URI, HTTP11_URL, HTTP10URL
class URI(ByteString):
	u"""Uniform Resource Identifier

		.. seealso:: :rfc:`3986`

		.. seealso:: :rfc:`2616#section-3.2`

		.. seealso:: :rfc:`2616#section-3.2.2`

	"""

	quote = Percent.encode
	unquote = Percent.decode

	@property
	def uri(self):  # deprecated
		return Unicode(self)

	@property
	def query(self):
		return tuple(QueryString.decode(self.query_string))

	@query.setter
	def query(self, query):
		self.query_string = QueryString.encode(query)

	@property
	def path_segments(self):
		return list(map(Unicode.replace, self.path.split(u'/'), u'%2f', u'/'))

	@path_segments.setter
	def path_segments(self, path):
		self.path = u'/'.join(seq.replace(u'/', u'%2f') for seq in path)

	def __init__(self, uri=None):
		self.query = {}
		self.set(uri or b'/')
		self.normalize()

	def normalize(self):
		self.scheme = self.scheme.lower()
		self.host = self.host.lower()
		if not self.port and self.scheme in DEFAULT_PORTS:
			self.port = DEFAULT_PORTS[self.scheme]
		if not self.path:
			self.path = u'/'
		self.abspath()

	def join(self, relative):
		relative = URI(relative)
		joined = URI(self)
		joined.path = join(joined.path, relative.path)
		joined.abspath()
		return joined

	def validate_http_request_uri(self):  # TODO: remove
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
		raise InvalidURI(Unicode(self))

	def sanitize(self):  # TODO: remove
		"""
			.. todo::
				sanitizing (non visible chars, %00)
		"""

	def set(self, uri):
		if isinstance(uri, Unicode):
			uri = uri.encode('UTF-8')

		if isinstance(uri, bytes):
			self.parse(uri)
		elif isinstance(uri, URI):
			self.tuple = uri.tuple
		elif isinstance(uri, tuple):
			self.tuple = uri
		elif isinstance(uri, dict):
			self.dict = uri
		else:
			raise InvalidURI()  # TypeError

	@property
	def dict(self):
		return dict(
			scheme=self.scheme,
			username=self.username,
			password=self.password,
			host=self.host,
			port=self.port,
			path=self.path,
			query_string=self.query_string,
			fragment=self.fragment
		)

	@dict.setter
	def dict(self, dict_):
		self.__dict__.update(dict_)  # FIXME

	@property
	def tuple(self):
		return (
			self.scheme,
			self.username,
			self.password,
			self.host,
			self.port and int(self.port) or b'',
			self.path,
			self.query_string,
			self.fragment
		)

	@tuple.setter
	def tuple(self, tuple_):
		(self.scheme, self.username, self.password, self.host,
			self.port, self.path, self.query_string, self.fragment) = tuple_

	def parse(self, uri):
		# <scheme>://<username>:<password>@<host>:<port>/<path>?<query>#<fragment>
		if uri == b'*':
			self.path = u'*'
			return
		if not uri:
			raise InvalidURI(u'')

		uri, _, fragment = uri.partition(b'#')
		uri, _, query_string = uri.partition(b'?')
		scheme, scheme_exists, uri = uri.rpartition(b'://')
		if not scheme_exists and uri.startswith(b'//'):
			uri = uri[2:]
		netloc, _, path = uri.partition(b'/')
		path = b'/%s' % path
		credentials, _, hostport = netloc.rpartition(b'@')
		username, _, password = credentials.partition(b':')
		host, _, port = hostport.partition(b':')
		if port:
			if not port.isdigit() or not (0 <= int(port) <= 65535):
				raise InvalidURI('Invalid port: %r' % (port))
			port = int(port)
		else:
			port = u''

		unquote = URI.unquote
		path = u'/'.join([unquote(seq).replace(u'/', u'%2f') for seq in path.split(b'/')])

		self.tuple = (
			scheme.decode('ascii'),
			unquote(username),
			unquote(password),
			unquote(host),
			port,
			path,
			query_string,
			unquote(fragment)
		)

	def compose(self):
		return b''.join(self.compose_iter())

	def compose_iter(self):
		quote = URI.quote
		scheme, username, password, host, port, path, query_string, fragment = self.tuple
		if path == u'*':
			yield b'*'
			return
		if scheme:
			yield quote(scheme)
			yield b'://'
		elif host:
			yield b'//'
		if host:
			if username:
				yield quote(username)
				if password:
					yield b':'
					yield quote(password)
				yield b'@'
			yield quote(host)
			if port and int(port) != DEFAULT_PORTS.get(scheme):
				yield b':%d' % int(port)
		if path:
			yield b'/'.join(map(quote, path.split(u'/')))
		else:
			yield b'/'
		if query_string:
			yield b'?'
			yield query_string
		if fragment:
			yield b'#'
			yield quote(fragment)

	# this is ripped from url-parse project which is MIT licensed
	def abspath(self):
		"""Clear out any '..' and excessive slashes from the path
			>>> dangerous = (u'/./', u'/../', u'./', u'/.', u'../', u'/..', u'//')
			>>> uris = (URI(b'/foo/./bar/../baz//blah/.'), )
			>>> all(all(d not in uri.path for d in dangerous) for uri in uris)
			True
			>>> URI(b'/foo/../bar/.').path == u'/bar/'
			True
		"""
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

	def __eq__(self, other):
		u"""Compares the URI with another string or URI

			.. seealso: :rfc:`2616#section-3.2.3`

			>>> u1 = URI(b'http://abc.com:80/~smith/home.html')
			>>> u2 = b'http://ABC.com/%7Esmith/home.html'
			>>> u3 = URI(b'http://ABC.com:/%7esmith/home.html')
			>>> u1 == u2 == u3
			True
		"""
		self_, other = URI(self), URI(other)
		self_.normalize()
		other.normalize()

		return self_.tuple == other.tuple

	def __bytes__(self):
		return self.compose()

	def __repr__(self):
		return '<URI(%s)>' % bytes(self)
