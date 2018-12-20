import pytest

from httoop.exceptions import InvalidLine


def test_method_maxlength(request_):
	with pytest.raises(InvalidLine):
		request_.method.parse('A' * 21)


def test_method_valid_characters(request_):
	with pytest.raises(InvalidLine):
		request_.parse('G\x01ET / HTTP/1.1')


def test_request_on_safe_method_containing_request_body():
	pass
