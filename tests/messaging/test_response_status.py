import pytest

from httoop.exceptions import InvalidLine


@pytest.mark.parametrize('status', [
    b' OK',
    b'2_00 OK',
    b'2_0 OK',
    b' 200 OK',
    b'\v200 OK',
])
def test_invalid_status(response, status):
    with pytest.raises(InvalidLine):
        response.status.parse(status)
