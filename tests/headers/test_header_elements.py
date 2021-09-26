import io

import pytest

from httoop.exceptions import InvalidHeader


def test_connection_close(headers):
	headers['Connection'] = 'CLOSE'
	assert headers.get_element('Connection').close


def test_connection_upgrade(headers):
	headers['Connection'] = 'UPgrade'
	assert headers.get_element('Connection').upgrade


def test_expect_100_continue(headers):
	headers['Expect'] = '100-CONtinue'
	assert headers.get_element('Expect').is_100_continue
	headers['Expect'] = '200-foo'
	assert not headers.get_element('Expect').is_100_continue


def test_upgrade_websocket(headers):
	headers['Upgrade'] = 'webSOCKET'
	assert headers.get_element('Upgrade').websocket


def test_content_options_nosniff(headers):
	headers['X-Content-Type-Options'] = 'nosniff'
	assert headers.get_element('X-Content-Type-Options').nosniff


def test_frame_options(headers):
	headers['X-Frame-Options'] = 'Deny'
	assert headers.get_element('X-Frame-Options').deny
	headers['X-Frame-Options'] = 'SameOrigin'
	assert headers.get_element('X-Frame-Options').same_origin
	headers['X-Frame-Options'] = 'ALLOW-from https://example.com/'
	assert headers.get_element('X-Frame-Options').allow_from == ['https://example.com/']


def test_xss_protection(headers):
	headers['X-XSS-Protection'] = '1; mode='
	assert headers.get_element('X-XSS-Protection').enabled
	assert not headers.get_element('X-XSS-Protection').block
	headers['X-XSS-Protection'] = '0; mode=block'
	assert not headers.get_element('X-XSS-Protection').enabled
	assert headers.get_element('X-XSS-Protection').block


def test_strict_transport_security(headers):
	headers['Strict-Transport-Security'] = 'max-age=16070400; includeSubDomains'
	assert headers.get_element('Strict-Transport-Security').include_sub_domains
	assert headers.get_element('Strict-Transport-Security').max_age == 16070400


@pytest.mark.parametrize('byte_range,ranges,content', [
	(b'bytes=0-15', [(0, 15)], [b'this foo bar tes']),
	(b'bytes=-5', [(None, 5)], [b' test']),
	(b'bytes=0-', [(0, None)], [b'this foo bar test']),
	(b'bytes=5-7', [(5, 7)], [b'foo']),
	(b'bytes=-0', [(None, 0)], [b'']),  # TODO: check if valid
	(b'bytes=-5,6-', [(None, 5), (6, None)], [b' test', b'oo bar test']),  # TODO: check if valid
])
def test_range(headers, byte_range, ranges, content):
	fd = io.BytesIO(b'this foo bar test')
	headers['Range'] = byte_range
	assert headers.get_element('Range') == 'bytes'
	assert headers.get_element('Range').ranges == ranges
	assert list(headers.get_element('Range').get_range_content(fd)) == content
	# assert bytes(headers.get_element('Range')) == byte_range  # FIXME: not implemented


@pytest.mark.parametrize('byte_range', [
	'bytes=-',
	'bytes=x',
	'bytes=-1-5',
	'bytes=1--5',
	'bytes=2-1',
	'bytes=0-0',
	'bytes=1-1',
	'bytes=',
	'bytes=5-7,',
	'bytes=5-7,6-8,5-7',
	'bytes=-5,-6',
	'bytes=5-,6-',
])
def test_invalid_range(headers, byte_range):
	headers['Range'] = byte_range
	with pytest.raises(InvalidHeader) as exc:
		headers.elements('Range')
	print(exc.value)


@pytest.mark.parametrize('byte_range,ranges,length', [
	(b'bytes 0-100/3032', (0, 100), 3032),
	(b'bytes 0-100/*', (0, 100), None),
	# (pytest.param(b'bytes */3032', marks=pytest.mark.xfail), (None, None), None)  # FIXME: b'bytes 0-3032/3032'
])
def test_content_range(headers, byte_range, ranges, length):
	headers['Content-Range'] = byte_range
	assert headers.get_element('Content-Range') == 'bytes'
	assert headers.get_element('Content-Range').range == ranges
	assert headers.get_element('Content-Range').length == length
	assert bytes(headers.get_element('Content-Range')) == byte_range


@pytest.mark.parametrize('byte_range', [
	'foo 0-100/3032',
	'bytes 0-100/-3032',
	'bytes -100/3032',
	'bytes 100-/3032',
	'bytes -0-100/3032',
	'bytes 4-2/3032',
	'bytes */*',
	'bytes *-*/*',
	'bytes -/*',
])
def test_invalid_content_range(headers, byte_range):
	headers['Content-Range'] = byte_range
	with pytest.raises(InvalidHeader) as exc:
		headers.get_element('Content-Range')
	print(exc.value)
