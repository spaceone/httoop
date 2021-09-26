from __future__ import unicode_literals

import pytest

from httoop import six
from httoop.exceptions import InvalidHeader

LATIN_CHARS = bytes(bytearray(range(0x80, 0xff + 1)))
INVALID_HEADER_FIELD_NAMES = bytes(bytearray(range(0x00, 0x1F + 1))) + b"()<>@,;\\\\\"/\\[\\]?={} \t"


@pytest.mark.parametrize('invalid', six.iterbytes(INVALID_HEADER_FIELD_NAMES + LATIN_CHARS))
def test_parse_invalid_characters(invalid, request_):
	with pytest.raises(InvalidHeader):
		invalid = b'foo%sbaz: blub' % (six.int2byte(invalid),)
		request_.headers.parse(invalid)


def test_set_header_with_colon(request_):
	with pytest.raises(InvalidHeader):
		request_.headers['foo:bar'] = 'baz'


#@pytest.mark.skip()
#def test_set_invalid_characters(request_):
#	for invalid in six.iterbytes(INVALID_HEADER_FIELD_NAMES):
#		name = b'foo%sbar' % (six.int2byte(invalid),)
#		request_.headers[name] = 'baz'
#		assert name not in request_.headers
#	for invalid in six.iterbytes(LATIN_CHARS):
#		with pytest.raises(InvalidHeader):
#			name = b'foo%sbar' % (six.int2byte(invalid),)
#			request_.headers[name] = 'baz'


@pytest.mark.parametrize('name', (b'Content-Encoding', b'Transfer-Encoding'))
def test_invalid_codec(name, headers):
	headers.parse(b'%s: foo' % (name,))
	with pytest.raises(InvalidHeader):
		headers.elements(name)


def test_unknown_codec(headers):
	headers.parse(b'Content-Type: foo/bar')
	assert headers.elements('Content-Type')[0].codec is None


def test_unknown_charset(headers):
	headers.parse(b"Foo: bar; filename*=BAR-8''foo.html")
	with pytest.raises(InvalidHeader):
		headers.get_element('foo')


def test_invalid_qvalue_accept(headers):
	headers.parse(b'Accept: foo/bar; q=a')
	with pytest.raises(InvalidHeader) as exc:
		headers.elements('Accept')
	assert 'Quality value must be float' in str(exc.value)


def test_invalid_encoding_rfc2047(headers):
	headers.parse(b'Foo: =?utf-8?b?xxx?=')
	with pytest.raises(InvalidHeader):
		headers['Foo']
	headers.parse(b'Bar: =?utf-8?b?=l?=')
	with pytest.raises(InvalidHeader):
		headers['Bar']
