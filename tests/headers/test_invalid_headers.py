import pytest
from httoop.exceptions import InvalidHeader


def test_invalid_codec(headers):
	for name in ('Content-Encoding', 'Transfer-Encoding'):
		headers.parse('%s: foo' % (name,))
		with pytest.raises(InvalidHeader):
			headers.elements(name)


def test_unknown_codec(headers):
	headers.parse('Content-Type: foo/bar')
	assert headers.elements('Content-Type')[0].codec is None
