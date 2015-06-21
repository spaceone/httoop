import pytest
from httoop.exceptions import InvalidHeader


@pytest.mark.parametrize('invalid', ('content-length', 'Trailer', 'transfer-Encoding'))
def test_invalid_trailer(invalid, headers):
	headers.parse('Trailer: %s' % (invalid,))
	with pytest.raises(InvalidHeader):
		headers.elements('Trailer')
