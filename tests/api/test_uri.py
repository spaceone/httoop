from __future__ import unicode_literals


def test_uri_set_string(request_):
	request_.uri = '/foo'
	assert request_.uri == '/foo'


def test_uri_set_bytes(request_):
	request_.uri = b'/foo'
	assert request_.uri == b'/foo'
