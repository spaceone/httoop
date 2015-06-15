import pytest
from httoop.exceptions import InvalidHeader

def test_invalid_trailer(headers):
	for invalid in ('content-length', 'Trailer', 'transfer-Encoding'):
		headers.parse('Trailer: %s' % (invalid,))
		with pytest.raises(InvalidHeader):
			headers.elements('Trailer')
