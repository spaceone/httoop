# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from httoop.exceptions import InvalidURI

import pytest


def test_uri_set_string(request_):
	request_.uri = '/foo'
	assert request_.uri == '/foo'


def test_uri_set_bytes(request_):
	request_.uri = b'/foo'
	assert request_.uri == b'/foo'


def test_uri_set_dict(request_):
	uri = {
		'scheme': 'http',
		'username': 'username',
		'password': 'password',
		'host': 'host',
		'port': 8090,
		'path': '/path',
		'query_string': 'query=string',
		'fragment': 'fragment'}
	request_.uri = uri
	assert request_.uri.dict == uri
	assert request_.uri == uri
	assert bytes(request_.uri) == b'http://username:password@host:8090/path?query=string#fragment'


def test_set_invalid_uri_nonascii(request_):
	with pytest.raises(InvalidURI):
		request_.uri = u'/fooäbar'
	with pytest.raises(InvalidURI):
		request_.uri = u'/fooäbar'.encode('latin-1')
	with pytest.raises(InvalidURI):
		request_.uri = u'/fooäbar'.encode('utf-8')


def test_set_invalid_uri(request_):
	with pytest.raises(TypeError):
		request_.uri = 1
	with pytest.raises(TypeError):
		request_.uri.path = 1


def test_set_latin1_bytes_uri_path(request_):  # just for code coverage... behvaior is stupid
	request_.uri.path = b'/foo\xffbar'
	assert bytes(request_.uri) == b'/foo%C3%BFbar'


@pytest.mark.xfail()
def test_uri_path_segments(request_):
	request_.uri.parse(b'/fo%2fbar/baz%2Fblub')
	assert request_.uri.path_segments == [u'', u'fo/bar', u'baz/blub']
	request_.uri.path_segments = [u'', u'my/path', u'segments']
	assert bytes(request_.uri) == b'/my%2fpath/segments'
