# -*- coding: utf-8 -*-
"""HTTP header elements

.. seealso:: :rfc:`2616#section-2.2`

.. seealso:: :rfc:`2616#section-4.2`

.. seealso:: :rfc:`2616#section-14`
"""
__all__ = ['HEADER', 'HeaderElement']

import re
# TODO: parse encoded words like =?UTF-8?B?…?= (RFC 2047); seealso quopri; '=?utf-8?q?=E2=86=92?='.decode('quopri')
# TODO: unify the use of unicode / bytes

from httoop.util import CaseInsensitiveDict, iteritems, Unicode
from httoop.exceptions import InvalidHeader
from httoop.codecs import lookup

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

	def __init__(self, value, params=None):
		self.value = bytes(value)
		self.params = params or {}
		self.sanitize()

	def sanitize(self):
		pass

	def __cmp__(self, other):
		return cmp(self.value, getattr(other, 'value', other))

	def __lt__(self, other):
		return self.value < getattr(other, 'value', other)

	def __bytes__(self):
		return self.compose()

	def __unicode__(self):
		return bytes(self).decode('ISO8859-1')

	if str is bytes:
		__str__ = __bytes__
	else:
		__str__ = __unicode__

	def compose(self):
		params = [b'; %s' % self.formatparam(k, v) for k, v in iteritems(self.params)]
		return b'%s%s' % (self.value, ''.join(params))

	@staticmethod
	def parseparams(elementstr):
		"""Transform 'token;key=val' to ('token', {'key': 'val'})."""
		# FIXME: quoted strings may contain ";"
		# Split the element into a value and parameters. The 'value' may
		# be of the form, "token=token", but we don't split that here.
		atoms = [x.strip() for x in elementstr.split(';') if x.strip()] or ['']

		initial_value = atoms.pop(0)
		params = dict((key.strip(), value.strip().strip('"')) for key, _, value in (atom.partition('=') for atom in atoms))

		return initial_value, params

	@classmethod
	def parse(cls, elementstr):
		"""Construct an instance from a string of the form 'token;key=val'."""
		ival, params = cls.parseparams(elementstr)
		return cls(ival, params)

	@classmethod
	def split(cls, fieldvalue):
		# FIXME: quoted strings may contain ","
		# TODO: elements which aren't comma separated
		return fieldvalue.split(',')

	@classmethod
	def join(cls, values):
		return b', '.join(values)

	@classmethod
	def formatparam(cls, param, value=None, quote=1):
		"""Convenience function to format and return a key=value pair.

		This will quote the value if needed or if quote is true.
		"""
		if value:
			if quote or cls.RE_TSPECIALS.search(value):
				value = value.replace('\\', '\\\\').replace('"', r'\"')
				return '%s="%s"' % (param, value)
			else:
				return '%s=%s' % (param, value)
		else:
			return param

	def __repr__(self):
		return '<%s(%r)>' % (self.__class__.__name__, self.value)


class MimeType(object):
	u"""
		.. seealso:: rfc:`2046`

		.. seealso:: rfc:`3023`
	"""

	@property
	def codec(self):
		return lookup(self.value, False) or lookup(self.mimetype, False)

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


class AcceptElement(HeaderElement):
	"""An Accept element with quality value

		.. seealso:: :rfc:`2616#section-3.9`

	"""

	# RFC 2616 Section 3.9
	RE_Q_SEPARATOR = re.compile(r'; *q *= *(?:(?:0(?:\.[0-9]{3})?)|(?:1(?:\.00?0?)?))')

	@property
	def quality(self):
		"""The quality of this value."""
		val = self.params.get("q", "1")
		if isinstance(val, HeaderElement):
			val = val.value
		return float(val)

	def sanitize(self):
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

	def __cmp__(self, other):
		if not isinstance(other, AcceptElement):
			other = AcceptElement(other)
		diff = cmp(self.quality, other.quality)
		if diff == 0:
			diff = cmp(str(self), str(other))
		# reverse
		return {-1: 1, 0: 0, 1: -1}.get(diff, diff)

	def __eq__(self, other):
		if not isinstance(other, AcceptElement):
			other = AcceptElement(other)
		return other.value == self.value and other.quality == self.quality

	def __lt__(self, other):
		if not isinstance(other, AcceptElement):
			other = AcceptElement(other)
		if self.quality == other.quality:
			return str(self) < str(other)
		else:
			return self.quality < other.quality


class CodecElement(object):

	@property
	def codec(self):
		encoding = self.value
		try:
			encoding = self.CODECS[encoding]
			if not isinstance(encoding, (bytes, Unicode)):
				return encoding
			return lookup(encoding)
		except KeyError:
			raise InvalidHeader(u'Unknown %s: %r' % (self.__name__, encoding.decode('ISO8859-1')))

	def __init__(self, value, params=None):
		super(CodecElement, self).__init__(value.lower(), params)

	def sanitize(self):
		self.codec
