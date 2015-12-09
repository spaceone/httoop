# -*- coding: utf-8 -*-
"""Uniform Resource Identifier

.. seealso:: :rfc:`3986`
"""

import re
from os.path import join

from httoop.exceptions import InvalidURI
from httoop.util import Unicode, _
from httoop.uri.percent_encoding import Percent
from httoop.uri.query_string import QueryString
from httoop.uri.type import URIType

# TODO: allow HTTP/1.0-';'-params?
# TODO: not able to have absolute paths


class URI(object):
	u"""Uniform Resource Identifier"""

	__metaclass__ = URIType
	__slots__ = ('scheme', 'username', 'password', 'host', '_port', 'path', 'query_string', 'fragment')

	SCHEMES = {}
	SCHEME = None
	PORT = None

	class _PercentAll(Percent):
		RESERVED_CHARS = b'%s %s' % (Percent.RESERVED_CHARS, ''.join(chr(x) for x in list(range(32)) + [127]))
	quote = _PercentAll.encode
	unquote = _PercentAll.decode

	@property
	def query(self):
		return tuple(QueryString.decode(self.query_string))

	@query.setter
	def query(self, query):
		self.query_string = QueryString.encode(query)

	@property
	def path_segments(self):
		return [Unicode.replace(p, u'%2f', u'/') for p in self.path.split(u'/')]

	@path_segments.setter
	def path_segments(self, path):
		self.path = u'/'.join(seq.replace(u'/', u'%2f') for seq in path)

	@property
	def uri(self):
		return b''.join(self._compose_uri_iter())

	@property
	def port(self):
		return self._port or self.PORT

	@port.setter
	def port(self, port):
		port = port or self.PORT
		if port:
			try:
				port = int(port)
				if not 0 <= int(port) <= 65535:
					raise ValueError
			except ValueError:
				raise InvalidURI(_(u'Invalid port: %r'), port)  # TODO: TypeError
		self._port = port

	def __init__(self, uri=None, *args, **kwargs):
		self.set(kwargs or args or uri or b'/')

	def join(self, relative):
		u"""Join a URI with another relative path

			.. todo:: test if os.path.join works with Windows

			.. todo:: implement safejoin, which normalizes
				the relative URI before joining
		"""
		relative = URI(relative)
		joined = URI(self)
		joined.path = join(joined.path, relative.path)
		joined.normalize()
		return joined

	def normalize(self):
		u"""normalize the URI

			makes it compareable

			.. seealso:: :rfc:`3986#section-6`
		"""
		self.scheme = self.scheme.lower()
		self.host = self.host.lower()

		if not self.port:
			self.port = self.PORT

		self.abspath()
		if not self.path.startswith(u'/') and self.host and self.scheme and self.path:
			self.path = u'/%s' % (self.path,)

	def abspath(self):
		"""Clear out any '..' and excessive slashes from the path

			>>> dangerous = (u'/./', u'/../', u'./', u'/.', u'../', u'/..', u'//')
			>>> uris = (URI(b'/foo/./bar/../baz//blah/.'), )
			>>> _ = [uri.abspath() for uri in uris]
			>>> all(all(d not in uri.path for d in dangerous) for uri in uris)
			True
			>>> u = URI(b'/foo/../bar/.'); u.abspath(); u.path == u'/bar/'
			True
		"""
		# Remove double forward-slashes from the path
		path = re.sub(br'\/{2,}', b'/', self.path)
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

	def set(self, uri):
		if isinstance(uri, Unicode):
			uri = uri.encode('UTF-8')  # FIXME

		if isinstance(uri, bytes):
			self.parse(uri)
		elif isinstance(uri, URI):
			self.tuple = uri.tuple
		elif isinstance(uri, tuple):
			self.tuple = uri
		elif isinstance(uri, dict):
			self.dict = uri
		else:
			raise TypeError

	@property
	def dict(self):
		return dict((key, getattr(self, key)) for key in self.__slots__)

	@dict.setter
	def dict(self, uri):
		for key in self.__slots__:
			setattr(self, key, uri.get(key, u''))

	@property
	def tuple(self):
		return tuple(getattr(self, key) for key in self.__slots__)

	@tuple.setter
	def tuple(self, tuple_):
		(self.scheme, self.username, self.password, self.host,
			self.port, self.path, self.query_string, self.fragment) = tuple_

	def parse(self, uri):
		r"""Parses a well formed absolute or relative URI.

			  foo://example.com:8042/over/there?name=ferret#nose
			  \_/   \______________/\_________/ \_________/ \__/
			   |           |            |            |        |
			scheme     authority       path        query   fragment
			   |   _____________________|__
			  / \ /                        \
			  urn:example:animal:ferret:nose

			https://username:password@[::1]:8090/some/path?query#fragment
			<scheme>://<username>:<password>@<host>:<port>/<path>?<query>#<fragment>
			[<scheme>:][//[<username>[:<password>]@][<host>][:<port>]/]<path>[?<query>][#<fragment>]
		"""

		if isinstance(uri, Unicode):
			try:
				uri = uri.encode('ascii')
			except UnicodeEncodeError:
				raise TypeError('URI must be ASCII bytes.')

		if type(self) is URI and b':' in uri:
			self.scheme = uri.split(b':', 1)[0].lower()
			if type(self) is not URI:
				return self.parse(uri)

		if uri and uri.strip(b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'):
			raise InvalidURI(_(u'Invalid URI: must consist of printable ASCII characters without whitespace.'))

		uri, __, fragment = uri.partition(b'#')
		uri, __, query_string = uri.partition(b'?')
		scheme, authority_exists, uri = uri.rpartition(b'://')
		if not authority_exists and uri.startswith(b'//'):
			uri = uri[2:]
			authority_exists = True
		if not authority_exists and b':' in uri:
			scheme, __, uri = uri.partition(b':')
		authority, path = b'', uri
		if authority_exists:
			authority, __, path = uri.partition(b'/')
			path = b'%s%s' % (__, path)
		userinfo, __, hostport = authority.rpartition(b'@')
		username, __, password = userinfo.partition(b':')
		if hostport.endswith(b']') and hostport.startswith(b'['):
			host, port = hostport, b''
		elif ':' in hostport:
			host, __, port = hostport.rpartition(b':')
		else:
			host, port = hostport, b''

		unquote = self.unquote
		path = u'/'.join([unquote(seq).replace(u'/', u'%2f') for seq in path.split(b'/')])

		try:
			scheme = scheme.decode('ascii').lower()
		except UnicodeDecodeError:
			raise InvalidURI(_(u'Invalid scheme: must be ASCII.'))

		if scheme and scheme.strip(u'abcdefghijklmnopqrstuvwxyz0123456789.-+'):
			raise InvalidURI(_(u'Invalid scheme: must only contain alphanumeric letters or plus, dash, dot.'))

		self.tuple = (
			scheme,
			unquote(username),
			unquote(password),
			unquote(host),
			port,
			path,
			QueryString.encode(QueryString.decode(query_string)),
			unquote(fragment)
		)

	def compose(self):
		return b''.join(self._compose_absolute_iter())

	def _compose_absolute_iter(self):
		u"""composes the whole URI"""
		scheme, username, password, host, port, path, _, fragment = self.tuple
		if scheme:
			yield self.quote(scheme)
			yield b':'
		authority = b''.join(self._compose_authority_iter())
		if authority:
			yield b'//'
		yield authority
		yield b''.join(self._compose_relative_iter())

	def _compose_authority_iter(self):
		if not self.host:
			return
		username, password, host, port, quote = self.username, self.password, self.host, self.port, self.quote
		if username:
			yield quote(username)
			if password:
				yield b':'
				yield quote(password)
			yield b'@'
		yield quote(host)
		if port and int(port) != self.PORT:
			yield b':%d' % int(port)

	def _compose_relative_iter(self):
		u"""Composes the relative URI beginning with the path"""
		path, query_string, quote, fragment = self.path, self.query_string, self.quote, self.fragment
		yield b'/'.join(map(quote, path.split(u'/')))
		if query_string:
			yield b'?'
			yield query_string
		if fragment:
			yield b'#'
			yield quote(fragment)

	def __eq__(self, other):
		u"""Compares the URI with another string or URI

			.. seealso:: :rfc:`2616#section-3.2.3`

			.. seealso:: :rfc:`3986#section-6`

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

	def __setattr__(self, name, value):
		if name.startswith('_'):
			return super(URI, self).__setattr__(name, value)

		if name == 'scheme' and value:
			self.__class__ = self.SCHEMES.get(value, URI)

		if name in self.__slots__:
			if isinstance(value, bytes):
				try:
					value = value.decode('UTF-8')
				except UnicodeDecodeError:
					value = value.decode('ISO8859-1')
			if value is None:
				pass
			elif not isinstance(value, Unicode):
				raise TypeError('%r must be string, not %s' % (name, type(value).__name__))

		super(URI, self).__setattr__(name, value)

	def __repr__(self):
		return '<URI(%s)>' % bytes(self)
