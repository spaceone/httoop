import pytest

from httoop.exceptions import InvalidLine


def test_response_protocol_with_http1_0_request_():
    pass


def test_response_protocol_with_http1_1_request_():
    pass


def test_response_protocol_with_http1_1_request_and_http1_0_server():
    pass


def test_response_protocol_with_http0_9_request_():
    pass


def test_response_protocol_with_http2_0_request_():
    pass


@pytest.mark.parametrize('protocol', [
    b'HTTP/ 1.1',
    b'HTTP/1_1.1',
    b'HTTP/1.a',
    b'HTTP/1.1a',
    b'HTTP/1.1\t',
])
def test_invalid_protocol(response, protocol):
    with pytest.raises(InvalidLine):
        response.protocol.parse(protocol)
