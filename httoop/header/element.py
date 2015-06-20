# -*- coding: utf-8 -*-
"""HTTP header elements

.. seealso:: :rfc:`2616#section-2.2`

.. seealso:: :rfc:`2616#section-4.2`

.. seealso:: :rfc:`2616#section-14`
"""
__all__ = ['HEADER', 'HeaderElement']

import re

from httoop.util import CaseInsensitiveDict, iteritems, decode_rfc2231
from httoop.exceptions import InvalidHeader
from httoop._percent import Percent

# a mapping of all headers to HeaderElement classes
HEADER = CaseInsensitiveDict()


class HeaderType(type):

	def __new__(mcs, name, bases, dict_):
		__all__.append(name)
		name = dict_.get('__name__', name)
		return super(HeaderType, mcs).__new__(mcs, name, bases, dict_)


class HeaderElement(object):
	u"""An element (with parameters) from an HTTP header's element list."""

	__metaclass__ = HeaderType

	# Regular expression that matches `special' characters in parameters, the
	# existance of which force quoting of the parameter value.
	RE_TSPECIALS = re.compile(r'[ \(\)<>@,;:\\"/\[\]\?=]')
	RE_SPLIT = re.compile(',(?=(?:[^"]*"[^"]*")*[^"]*$)')
	RE_PARAMS = re.compile(';(?=(?:[^"]*"[^"]*")*[^"]*$)')

	def __init__(self, value, params=None):
		self.value = bytes(value)
		self.params = params or {}
		self.sanitize()

	def sanitize(self):
		pass

	def __lt__(self, other):
		return self.value < getattr(other, 'value', other)

	def __gt__(self, other):
		return self.value > getattr(other, 'value', other)

	def __eq__(self, other):
		return self.value == getattr(other, 'value', other)

	def __ne__(self, other):
		return not self == other

	def __bytes__(self):
		return self.compose()

	def __unicode__(self):
		return bytes(self).decode('ISO8859-1')

	if str is bytes:
		__str__ = __bytes__
	else:  # pragma: no cover
		__str__ = __unicode__

	def compose(self):
		params = [b'; %s' % self.formatparam(k, v) for k, v in iteritems(self.params)]
		return b'%s%s' % (self.value, ''.join(params))

	@classmethod
	def parseparams(cls, elementstr):
		"""Transform 'token;key=val' to ('token', {'key': 'val'})."""
		# Split the element into a value and parameters. The 'value' may
		# be of the form, "token=token", but we don't split that here.
		atoms = [x.strip() for x in cls.RE_PARAMS.split(elementstr) if x.strip()] or ['']

		value = atoms.pop(0)
		_unescape = cls.unescape_param
		params = ((key.strip().lower(), _unescape(val.strip())) for key, _, val in (atom.partition('=') for atom in atoms))
		params = cls._rfc2231_and_continuation_params(params)
		# TODO: prefer foo* parameter when both are provided

		return value, dict(params)

	@classmethod
	def unescape_param(cls, value):
		quoted = value.startswith(b'"') and value.endswith(b'"')
		if quoted:
			value = re.sub(r'\\(?!\\)', '', value.strip(b'"'))
		else:
			if cls.RE_TSPECIALS.search(value):
				raise InvalidHeader('Unquoted param containing TSPECIALS')
		return value, quoted

	@classmethod
	def _rfc2231_and_continuation_params(cls, params):
		count = set()
		continuations = dict()
		for key, (value, quoted) in params:
			if key in count:
				raise InvalidHeader('Parameter given twice: %r' % (key.decode('ISO8859-1'),))
			count.add(key)
			if '*' in key:
				if key.endswith('*') and not quoted:
					encoding, language, value_ = decode_rfc2231(value.encode('ISO8859-1'))
					if not encoding:
						yield key, value
						continue
					key, value = key[:-1], Percent.decode(value_, encoding)
				key_, asterisk, num = key.rpartition('*')
				if asterisk:
					try:
						if num != '0' and num.startswith('0'):
							raise ValueError
						num = int(num)
					except ValueError:
						yield key, value
						continue
					continuations.setdefault(key_, {})[num] = value
					continue
			yield key, value

		for key, lines in iteritems(continuations):
			value = b''
			for i in xrange(len(lines)):
				try:
					value += lines.pop(i)
				except KeyError:
					break
			if not key:
				raise InvalidHeader('...')
			if value:
				yield key, value
			for k, v in iteritems(lines):
				yield '%s*%d' % (key, k), v

	@classmethod
	def parse(cls, elementstr):
		"""Construct an instance from a string of the form 'token;key=val'."""
		ival, params = cls.parseparams(elementstr)
		return cls(ival, params)

	@classmethod
	def split(cls, fieldvalue):
		return cls.RE_SPLIT.split(fieldvalue)

	@classmethod
	def join(cls, values):
		return b', '.join(values)

	@classmethod
	def sorted(cls, elements):
		return elements

	@classmethod
	def merge(cls, elements, others):
		return cls.join([bytes(x) for x in cls.sorted(elements + others)])

	@classmethod
	def formatparam(cls, param, value=None, quote=False):
		"""Convenience function to format and return a key=value pair.

		This will quote the value if needed or if quote is true.
		"""
		if value:
			value = bytes(value)
			if quote or cls.RE_TSPECIALS.search(value):
				value = value.replace('\\', '\\\\').replace('"', r'\"')
				return '%s="%s"' % (param, value)
			else:
				return '%s=%s' % (param, value)
		else:
			return param

	def __repr__(self):
		return '<%s(%r, %r)>' % (self.__class__.__name__, self.value, self.params)


class MimeType(object):
	u"""
		.. seealso:: rfc:`2046`

		.. seealso:: rfc:`3023`
	"""

	@property
	def mimetype(self):
		return '%s/%s' % (self.type, self.subtype_wo_vendor)

	@property
	def type(self):
		return self.value.split('/', 1)[0]

	@type.setter
	def type(self, type_):
		self.value = '%s/%s' % (type_, self.subtype)

	@property
	def subtype(self):
		return (self.value.split('/', 1) + [b''])[1]

	@subtype.setter
	def subtype(self, subtype):
		self.value = '%s/%s' % (self.type, subtype)

	# TODO: official name
	@property
	def subtype_wo_vendor(self):
		return self.subtype.split('+', 1).pop()

	@subtype_wo_vendor.setter
	def subtype_wo_vendor(self, subtype_wo_vendor):
		self.subtype = '%s+%s' % (self.vendor, subtype_wo_vendor)

	@property
	def vendor(self):
		if b'+' in self.subtype:
			return self.subtype.split('+', 1)[0]
		return b''

	@vendor.setter
	def vendor(self, vendor):
		self.subtype = '%s+%s' % (vendor, self.subtype_wo_vendor)

	@property
	def version(self):
		return self.params.get('version', '')

	@version.setter
	def version(self, version):
		self.params['version'] = version


class _AcceptElement(HeaderElement):
	"""An Accept element with quality value

		.. seealso:: :rfc:`2616#section-3.9`

	"""

	# RFC 2616 Section 3.9
	RE_Q_SEPARATOR = re.compile(r';\s*q\s*=\s*')

	@property
	def quality(self):
		"""The quality of this value."""
		val = self.params.get("q", "1")
		if isinstance(val, HeaderElement):
			val = val.value
		if val:
			return float(val)

	def sanitize(self):
		super(_AcceptElement, self).sanitize()
		try:
			self.quality
		except ValueError:
			raise InvalidHeader(u'Quality value must be float.')

	@classmethod
	def parse(cls, elementstr):
		qvalue = None
		# The first "q" parameter (if any) separates the initial
		# media-range parameter(s) (if any) from the accept-params.
		atoms = cls.RE_Q_SEPARATOR.split(elementstr, 1)
		media_range = atoms.pop(0).strip()
		if atoms:
			# The qvalue for an Accept header can have extensions. The other
			# headers cannot, but it's easier to parse them as if they did.
			qvalue = HeaderElement.parse(atoms[0].strip())

		media_type, params = cls.parseparams(media_range)
		if qvalue is not None:
			params["q"] = qvalue

		return cls(media_type, params)

	@classmethod
	def sorted(cls, elements):
		return list(sorted(elements, reverse=True))

	def __eq__(self, other):
		if not isinstance(other, _AcceptElement):
			other = _AcceptElement(other)
		return other.value == self.value and other.quality == self.quality

	def __lt__(self, other):
		if not isinstance(other, _AcceptElement):
			other = _AcceptElement(other)
		if self.quality == other.quality:
			return str(self) < str(other)
		else:
			return self.quality < other.quality
