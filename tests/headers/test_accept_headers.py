from __future__ import unicode_literals


def test_quality_parameter_in_accept_header(headers):
	headers.parse(b'Accept: application/json; q=0.2, text/plain, text/html; q=0.5, *; q=0')
	assert headers.values('Accept') == ['text/plain', 'text/html', 'application/json', '*/*']
