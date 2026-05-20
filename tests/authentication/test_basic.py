import base64

import pytest

from httoop.exceptions import InvalidHeader
from httoop.header import Authorization, WWWAuthenticate


def test_basic_www_authenticate(headers):
    www_auth = WWWAuthenticate('Basic', {'realm': 'simple'})
    assert bytes(www_auth) in {b'Basic realm="simple"', b'Basic realm=simple'}
    headers.parse(b'WWW-Authenticate: %s' % www_auth)
    assert headers.elements('WWW-Authenticate')[0].realm == 'simple'


def test_basic_authorization(headers):
    auth = Authorization('Basic', {'username': 'admin', 'password': '12345'})
    assert bytes(auth) == b'Basic YWRtaW46MTIzNDU='
    headers.parse(b'Authorization: %s' % auth)
    elem = headers.element('Authorization')
    assert elem.params['username'] == b'admin'
    assert elem.params['password'] == b'12345'
    assert elem.scheme == 'basic'
    assert elem.username == 'admin'
    assert elem.password == '12345'
    elem.username = 'test'
    elem.password = 'test'
    assert elem.username == 'test'
    assert elem.password == 'test'


@pytest.mark.parametrize('invalid,username,password', [
    (base64.b64encode(b'username:pass:word'), b'username', b'pass:word'),
    (base64.b64encode(b'username:'), b'username', b''),
    (base64.b64encode(b'user\nname:password'), b'user\nname', b'password'),
    (base64.b64encode(b'username:pass\nword'), b'username', b'pass\nword'),
    # TODO: different encodings
])
def test_valid_headers(headers, invalid, username, password):
    headers.parse(b'Authorization: Basic %s' % (invalid,))
    elem = headers.element('Authorization')
    assert elem.params['username'] == username
    assert elem.params['password'] == password
    headers.clear()


@pytest.mark.parametrize('invalid', [
    b'foo',
    b'Zm9v',
    'föo'.encode('latin1'),
    base64.b64encode(b':password'),
    base64.b64encode(b'username:password') + b'"$"_'
])
def test_invalid_headers(headers, invalid):
    headers.parse(b'Authorization: Basic %s' % (invalid,))
    with pytest.raises(InvalidHeader):
        headers.element('Authorization')
    headers.clear()
