import string

import pytest

from httoop.exceptions import InvalidLine


VALID_METHOD_CHARS = string.ascii_letters + string.digits + '$-_.'


def test_method_format(request_):
    assert f'{request_.method}' == 'GET'


def test_method_maxlength(request_):
    with pytest.raises(InvalidLine):
        request_.method.parse(b'A' * 21)
    request_.method.parse(b'A' * 20)


@pytest.mark.parametrize('char', list(VALID_METHOD_CHARS))
def test_method_valid_characters(request_, char):
    request_.parse(b'G%bET / HTTP/1.1' % char.encode('ASCII'))


@pytest.mark.parametrize('char', set(''.join(map(chr, range(256)))) - set(VALID_METHOD_CHARS))
def test_method_invalid_characters(request_, char):
    with pytest.raises(InvalidLine):
        request_.parse(b'G%bET / HTTP/1.1' % char.encode('ISO8859-1'))


def test_request_on_safe_method_containing_request_body():
    pass
