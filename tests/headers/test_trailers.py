from __future__ import unicode_literals

import pytest

from httoop.exceptions import InvalidHeader


@pytest.mark.parametrize('invalid', (b'content-length', b'Trailer', b'transfer-Encoding'))
def test_invalid_trailer(invalid, headers):
	headers.parse(b'Trailer: %s' % (invalid,))
	with pytest.raises(InvalidHeader):
		headers.elements('Trailer')
