from __future__ import unicode_literals

import pytest


def test_quality_parameter_in_accept_header(headers):
	headers.parse(b'Accept: application/json; q=0.2, text/plain, text/html; q=0.5, *; q=0')
	assert headers.values('Accept') == ['text/plain', 'text/html', 'application/json', '*/*']


def test_comparing_accept(headers):
	headers.parse(b'Accept: application/json; q=0.2, text/plain, text/html; q=0.5, *; q=0')
	headers.elements('Accept')[0] < 'text/html'
	headers.elements('Accept')[0] < '*'


@pytest.mark.parametrize('header_name', ['Accept', 'Content-Type'])
def test_mimetype_element(headers, header_name):
	headers[header_name] = 'text/html'
	h = headers.get_element(header_name)
	assert h.type == 'text'
	assert h.subtype == 'html'
	assert not h.version
	assert not h.vendor
	h.type = 'application'
	h.subtype = 'json'
	assert h == 'application/json'
	h.subtype_wo_vendor = 'xml'
	h.vendor = 'httoop.test'
	h.version = 1
	assert h == 'application/httoop.test+xml'
	assert bytes(h) == b'application/httoop.test+xml; version=1'
	assert h.version == '1'
	assert h.vendor == 'httoop.test'
	assert h.subtype_wo_vendor == 'xml'
