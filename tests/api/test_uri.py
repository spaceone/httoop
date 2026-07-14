import pytest

from httoop import Request
from httoop.exceptions import InvalidURI


def test_uri_set_string(request_: Request):
    request_.uri = '/foo'
    assert request_.uri == '/foo'


def test_uri_set_bytes(request_: Request):
    request_.uri = b'/foo'
    assert request_.uri == b'/foo'


def test_uri_set_dict(request_: Request):
    uri = {
        'scheme': 'http',
        'username': 'username',
        'password': 'password',
        'host': 'host',
        'port': 8090,
        'path': '/path',
        'query_string': 'query=string',
        'fragment': 'fragment',
    }
    request_.uri = uri
    assert request_.uri.dict == uri
    assert request_.uri == uri
    assert bytes(request_.uri) == b'http://username:password@host:8090/path?query=string#fragment'


def test_set_invalid_uri_nonascii(request_: Request):
    with pytest.raises(InvalidURI):
        request_.uri = '/fooäbar'
    with pytest.raises(InvalidURI):
        request_.uri = '/fooäbar'.encode('latin-1')
    with pytest.raises(InvalidURI):
        request_.uri = '/fooäbar'.encode()


def test_set_invalid_uri(request_: Request):
    with pytest.raises(TypeError):
        request_.uri = 1
    with pytest.raises(TypeError):
        request_.uri.path = 1


def test_set_latin1_bytes_uri_path(request_: Request):  # just for code coverage... behvaior is stupid
    request_.uri.path = b'/foo\xffbar'
    assert bytes(request_.uri) == b'/foo%C3%BFbar'


@pytest.mark.xfail
def test_uri_path_segments(request_: Request):
    request_.uri.parse(b'/fo%2fbar/baz%2Fblub')
    assert request_.uri.path_segments == ['', 'fo/bar', 'baz/blub']
    request_.uri.path_segments = ['', 'my/path', 'segments']
    assert bytes(request_.uri) == b'/my%2fpath/segments'
