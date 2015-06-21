import pytest

from httoop.exceptions import InvalidLine


def test_response_protocol_with_http1_0_request_():
	pass


def test_request_protocol_with_invalid_name(request_):
	with pytest.raises(InvalidLine):
		request_.protocol.parse('HTCPCP/1.1')
