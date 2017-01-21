import pytest
from httoop.exceptions import InvalidHeader

LATIN_CHARS = bytes(bytearray(range(0x80, 0xff + 1)))
INVALID_HEADER_FIELD_NAMES = bytes(bytearray(range(0x00, 0x1F + 1))) + b"()<>@,;\\\\\"/\[\]?={} \t"

@pytest.mark.parametrize('invalid', INVALID_HEADER_FIELD_NAMES + LATIN_CHARS)
def test_parse_invalid_characters(invalid, request_):
	with pytest.raises(InvalidHeader):
		invalid = b'foo%sbaz: blub' % (invalid,)
		request_.headers.parse(invalid)


def test_set_header_with_colon(request_):
	with pytest.raises(InvalidHeader):
		request_.headers['foo:bar'] = 'baz'


#@pytest.mark.skip()
#def test_set_invalid_characters(request_):
#	for invalid in INVALID_HEADER_FIELD_NAMES:
#		name = b'foo%sbar' % (invalid,)
#		request_.headers[name] = 'baz'
#		assert name not in request_.headers
#	for invalid in LATIN_CHARS:
#		with pytest.raises(InvalidHeader):
#			name = b'foo%sbar' % (invalid,)
#			request_.headers[name] = 'baz'


@pytest.mark.parametrize('name', ('Content-Encoding', 'Transfer-Encoding'))
def test_invalid_codec(name, headers):
	headers.parse('%s: foo' % (name,))
	with pytest.raises(InvalidHeader):
		headers.elements(name)


def test_unknown_codec(headers):
	headers.parse('Content-Type: foo/bar')
	assert headers.elements('Content-Type')[0].codec is None
