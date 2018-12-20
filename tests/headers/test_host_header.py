from httoop.exceptions import InvalidHeader
import pytest


def test_http1_1_request_without_host_header():
	pass


def test_http1_0_request_without_host_header():
	pass


@pytest.mark.parametrize('value,host,port', [
	('Www.exaMple.com', 'www.example.com', None),
	('localhost:8090', 'localhost', 8090),
])
def test_host_header_is_fqdn(value, host, port, headers):
	element = _test_iter(value, host, port, headers)
	assert element.is_fqdn
	assert not element.is_ip4
	assert not element.is_ip6


@pytest.mark.parametrize('value,host,port', [
	('127.0.0.1', '127.0.0.1', None),
	('192.168.0.1', '192.168.0.1', None),
	('8.8.8.8:8090', '8.8.8.8', 8090),
])
def test_host_header_is_ip4(value, host, port, headers):
	element = _test_iter(value, host, port, headers)
	assert element.is_ip4
	assert not element.is_ip6
	assert not element.is_fqdn


@pytest.mark.parametrize('value,host,port', [
	('[fe80::b244:33c4:767b:adae]', 'fe80::b244:33c4:767b:adae', None),
	('[::1]', '::1', None),
	('[fe80::b244:33c4:767b:adae]:8090', 'fe80::b244:33c4:767b:adae', 8090),
	('[::1]:8090', '::1', 8090),
])
def test_host_header_is_ip6(value, host, port, headers):
	element = _test_iter(value, host, port, headers)
	assert element.is_ip6
	assert not element.is_ip4
	assert not element.is_fqdn


def _test_iter(header, host, port, headers):
	headers['Host'] = header
	element = headers.element('Host')
	assert port == element.port
	assert host == element.hostname
	return element


@pytest.mark.parametrize('invalid', list(
	list((set('\x7F()<>@,;:/\\[\\]={} \t\\\\^"\'') | set(map(chr, range(0x00, 0x1F)))) - set(';\n\x00')) + [
		pytest.mark.xfail(';'),  # FIXME
		pytest.mark.xfail('\n'),  # FIXME
		pytest.mark.xfail('\x00'),  # FIXME
	]
))
def test_invalid_host_header(invalid, headers):
	headers['Host'] = b'foo%sbar' % (invalid,)
	with pytest.raises(InvalidHeader):
		headers.element('Host')
