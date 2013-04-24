# -*- coding: utf-8 -*-
"""HTTP headers

.. seealso:: :rfc:`2616#section-4.2`

.. seealso:: :rfc:`2616#section-14`
"""

__all__ = ['Headers', 'HeaderElement']

import re
from httoop.util import CaseInsensitiveDict, ByteString, iteritems
from httoop.exceptions import InvalidHeader

# TODO: cleanup
# FIXME: python3 support

# ripped from cherrypy, which is MIT

# Regular expression that matches `special' characters in parameters, the
# existance of which force quoting of the parameter value.
RE_TSPECIALS = re.compile(r'[ \(\)<>@,;:\\"/\[\]\?=]')
RE_Q_SEPARATOR = re.compile(r'; *q *=')

class Headers(ByteString, CaseInsensitiveDict):
	# disallowed bytes for HTTP header field names
	HEADER_RE = re.compile(b"[\x00-\x1F\x7F()<>@,;:\\\\\"/\[\]?={} \t\x80-\xFF]")

	def elements(self, key):
		"""Return a sorted list of HeaderElements for the given header."""
		return header_elements(key, self.get(key))

	def get_all(self, name):
		"""Return a list of all the values for the named field."""
		return [val.strip() for val in self.get(name, '').split(',')]

	def __str__(self):
		return self.compose()

	def __bytes__(self):
		# TODO: remove, this is the job of compose
		return str(self).encode('iso8859-1')

	def values(self, key=None):
		# if key is set return a ordered list of element values
		# TODO: may move this into another method because values is a dict name
		if key is None:
			return super(Headers, self).values()
		return [e.value for e in self.elements(key)]

	def append(self, key, value):
		if not key in self:
			self[key] = value
		else:
			self[key] = ", ".join([self[key], value])

	def add_header(self, _name, _value, **_params):
		"""Extended header setting.

		_name is the header field to add. keyword arguments can be used to set
		additional parameters for the header field, with underscores converted
		to dashes. Normally the parameter will be added as key="value" unless
		value is None, in which case only the key will be added.

		Example:

		h.add_header('content-disposition', 'attachment', filename='bud.gif')

		Note that unlike the corresponding 'email.Message' method, this does
		*not* handle '(charset, language, value)' tuples: all values must be
		strings or None.
		"""
		parts = []
		if _value is not None:
			parts.append(_value)
		for k, v in list(_params.items()):
			k = k.replace('_', '-')
			if v is None:
				parts.append(k)
			else:
				parts.append(_formatparam(k, v))
		self.append(_name, "; ".join(parts))

	def validate(self):
		u"""validates all header elements"""
		for name in self:
			self.elements(name)

	def parse(self, data):
		r"""parses HTTP headers

			:param data:
				the header string containing headers separated by "\r\n"
				without trailing "\r\n"
			:type  data: bytes
		"""

		lines = data.split(b'\r\n')

		# parse headers into key/value pairs paying attention
		# to continuation lines.
		while lines:
			# Parse initial header name : value pair.
			curr = lines.pop(0)
			if b':' not in curr:
				raise InvalidHeader("invalid line %s" % curr.strip())

			name, value = curr.split(":", 1)
			name = name.rstrip(" \t")

			if self.HEADER_RE.search(name):
				raise InvalidHeader("invalid header name %s" % name)

			name, value = name.strip(), [value.lstrip()]

			# Consume value continuation lines
			while lines and lines[0].startswith((" ", "\t")):
				value.append(lines.pop(0)[1:])
			value = b''.join(value).rstrip()

			# store new header value
			self.append(name, value)

	def compose(self):
		# TODO: implement this idea, adpat CaseInsensitiveDict to store values as unicode in python2
		#headers = b''
		#for name, field in iteritems(self):
		#	try:
		#		field = field.encode('utf-8')
		#	except UnicodeDecodeError:
		#		field = field.encode('iso8859-1')
		#	headers += b'%s: %s\r\n' % (name.encode('ascii'), field)
		#headers += b'\r\n'
		#return headers
		return b'%s\r\n' % b''.join(b'%s: %s\r\n' % (k, v) for k, v in iteritems(self))

	def __repr__(self):
		return "<HTTP Headers(%s)>" % repr(list(self.items()))

def _formatparam(param, value=None, quote=1):
	"""Convenience function to format and return a key=value pair.

	This will quote the value if needed or if quote is true.
	"""
	if value is not None and len(value) > 0:
		if quote or RE_TSPECIALS.search(value):
			value = value.replace('\\', '\\\\').replace('"', r'\"')
			return '%s="%s"' % (param, value)
		else:
			return '%s=%s' % (param, value)
	else:
		return param

def header_elements(fieldname, fieldvalue):
	"""Return a sorted HeaderElement list.

	Returns a sorted HeaderElement list
	from a comma-separated header string.
	"""

	if not fieldvalue:
		return []

	Element = headerfields.get(fieldname, HeaderElement)

	result = []
	for element in fieldvalue.split(","):
		result.append(Element.from_str(element))

	return list(reversed(sorted(result)))
	# TODO: remove the reversed() (fix in AcceptElement)

headerfields = CaseInsensitiveDict()

# TODO: remove this function?
def init():
	headerfields.update({
		'TE': AcceptElement,
		'Accept': AcceptElement,
		'Accept-Charset': AcceptElement,
		'Accept-Language': AcceptElement,
		'Accept-Encoding': AcceptElement,
		'Accept-Ranges': AcceptElement,
		'Age': Age,
		'Allow': Allow,
		'Authorization': Authorization,
		'Cache-Control': CacheControl,
		'Connection': Connection,
		'Content-Encoding': ContentEncoding,
		'Content-Language': ContentLanguage,
		'Content-Length': ContentLength,
		'Content-Location': ContentLocation,
		'Content-MD5': ContentMD5,
		'Content-Range': ContentRange,
		'Content-Type': ContentType,
		'Date': Date,
		'ETag': ETag,
		'Expect': Expect,
		'Expires': Expires,
		'From': From,
		'Host': Host,
		'If-Match': IfMatch,
		'If-Modified-Since': IfModifiedSince,
		'If-None-Match': IfNoneMatch,
		'If-Unmodified-Since': IfUnmodifiedSince,
		'LastModified': LastModified,
		'Location': Location,
		'Max-Forwards': MaxForwards,
		'Pragma': Pragma,
		'Proxy-Authenticate': ProxyAuthenticate,
		'Proxy-Authorization': ProxyAuthorization,
		'Range': Range,
		'Referer': Referer,
		'Retry-After': RetryAfter,
		'Server': Server,
		'Trailer': Trailer,
		'Transfer-Encoding': TransferEncoding,
		'Upgrade': Upgrade,
		'User-Agent': UserAgent,
		'Vary': Vary,
		'Via': Via,
		'Warning': Warning,
		'WWW-Authenticate': WWWAuthenticate
	})

class HeaderElement(object):
	"""An element (with parameters) from an HTTP header's element list."""

	def __init__(self, value, params=None):
		self.value = value
		if params is None:
			params = {}
		self.params = params

	def __cmp__(self, other):
		return cmp(self.value, other.value)

	def __lt__(self, other):
		return self.value < other.value

	def __str__(self):
		p = [";%s=%s" % (k, v) for k, v in self.params.iteritems()] # FIXME: py3
		return "%s%s" % (self.value, "".join(p))

	def parse(elementstr):
		"""Transform 'token;key=val' to ('token', {'key': 'val'})."""
		# Split the element into a value and parameters. The 'value' may
		# be of the form, "token=token", but we don't split that here.
		atoms = [x.strip() for x in elementstr.split(";") if x.strip()]
		if not atoms:
			initial_value = ''
		else:
			initial_value = atoms.pop(0).strip()
		params = {}
		for atom in atoms:
			atom = [x.strip() for x in atom.split("=", 1) if x.strip()]
			key = atom.pop(0)
			if atom:
				val = atom[0]
			else:
				val = ""
			params[key] = val
		return initial_value, params
	parse = staticmethod(parse)

	@classmethod
	def from_str(cls, elementstr):
		"""Construct an instance from a string of the form 'token;key=val'."""
		ival, params = cls.parse(elementstr)
		return cls(ival, params)

# TODO: rename e.g. into QualityElement
class AcceptElement(HeaderElement):
	"""An element (with parameters) from an Accept* header's element list.

	AcceptElement objects are comparable; the more-preferred object will be
	"less than" the less-preferred object. They are also therefore sortable;
	if you sort a list of AcceptElement objects, they will be listed in
	priority order; the most preferred value will be first. Yes, it should
	have been the other way around, but it's too late to fix now.
	"""

	@classmethod
	def from_str(cls, elementstr):
		qvalue = None
		# The first "q" parameter (if any) separates the initial
		# media-range parameter(s) (if any) from the accept-params.
		atoms = RE_Q_SEPARATOR.split(elementstr, 1)
		media_range = atoms.pop(0).strip()
		if atoms:
			# The qvalue for an Accept header can have extensions. The other
			# headers cannot, but it's easier to parse them as if they did.
			qvalue = HeaderElement.from_str(atoms[0].strip())

		media_type, params = cls.parse(media_range)
		if qvalue is not None:
			params["q"] = qvalue
		return cls(media_type, params)

	def qvalue(self):
		val = self.params.get("q", "1")
		if isinstance(val, HeaderElement):
			val = val.value
		return float(val)
	qvalue = property(qvalue, doc="The qvalue, or priority, of this value.")

	def __cmp__(self, other):
		diff = cmp(self.qvalue, other.qvalue)
		if diff == 0:
			diff = cmp(str(self), str(other))
		return diff

	def __lt__(self, other):
		if self.qvalue == other.qvalue:
			return str(self) < str(other)
		else:
			return self.qvalue < other.qvalue

# TODO: add Accept-*

class Age(HeaderElement):
	pass

class Allow(HeaderElement):
	pass

class Authorization(HeaderElement):
	pass

class CacheControl(HeaderElement):
	pass

class Connection(HeaderElement):
	pass

class ContentEncoding(HeaderElement):
	pass

class ContentLanguage(HeaderElement):
	pass

class ContentLength(HeaderElement):
	pass

class ContentLocation(HeaderElement):
	pass

class ContentMD5(HeaderElement):
	pass

class ContentRange(HeaderElement):
	pass

class ContentType(HeaderElement):
	pass

class Date(HeaderElement):
	pass

class ETag(HeaderElement):
	pass

class Expect(HeaderElement):
	pass

class Expires(HeaderElement):
	pass

class From(HeaderElement):
	pass

class Host(HeaderElement):
	pass

class IfMatch(HeaderElement):
	pass

class IfModifiedSince(HeaderElement):
	pass

class IfNoneMatch(HeaderElement):
	pass

class IfRange(HeaderElement):
	pass

class IfUnmodifiedSince(HeaderElement):
	pass

class LastModified(HeaderElement):
	pass

class Location(HeaderElement):
	pass

class MaxForwards(HeaderElement):
	pass

class Pragma(HeaderElement):
	pass

class ProxyAuthenticate(HeaderElement):
	pass

class Range(HeaderElement):
	pass

class Referer(HeaderElement):
	pass

class RetryAfter(HeaderElement):
	pass

class Server(HeaderElement):
	pass

class TE(HeaderElement):
	pass

class Trailer(HeaderElement):
	pass

class TransferEncoding(HeaderElement):
	pass

class Upgrade(HeaderElement):
	pass

class UserAgent(HeaderElement):
	pass

class Vary(HeaderElement):
	pass

class Via(HeaderElement):
	pass

class Warning(HeaderElement):
	pass

class WWWAuthenticate(HeaderElement):
	pass

