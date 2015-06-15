import pytest

from httoop.exceptions import InvalidLine


def test_response_protocol_with_http1_0_request():
	pass


def test_request_protocol_with_invalid_name(request):
	with pytest.raises(InvalidLine):
		request.protocol.parse('HTCPCP/1.1')
