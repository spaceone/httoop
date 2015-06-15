from httoop.exceptions import InvalidHeader
import pytest


def test_http1_1_request_without_host_header():
	pass


def test_http1_0_request_without_host_header():
	pass


def test_host_header_is_fqdn(headers):
	hosts = {
		'Www.exaMple.com': ('www.example.com', None),
		'localhost:8090': ('localhost', 8090),
	}
	for element in _test_iter(hosts, headers):
		assert element.is_fqdn
		assert not element.is_ip4
		assert not element.is_ip6


def test_host_header_is_ip4(headers):
	hosts = {
		'127.0.0.1': ('127.0.0.1', None),
		'192.168.0.1': ('192.168.0.1', None),
		'8.8.8.8:8090': ('8.8.8.8', 8090),
	}
	for element in _test_iter(hosts, headers):
		assert element.is_ip4
		assert not element.is_ip6
		assert not element.is_fqdn


def test_host_header_is_ip6(headers):
	hosts = {
		'[fe80::b244:33c4:767b:adae]': ('fe80::b244:33c4:767b:adae', None),
		'[::1]': ('::1', None),
		'[fe80::b244:33c4:767b:adae]:8090': ('fe80::b244:33c4:767b:adae', 8090),
		'[::1]:8090': ('::1', 8090),
	}
	for element in _test_iter(hosts, headers):
		assert element.is_ip6
		assert not element.is_ip4
		assert not element.is_fqdn


def _test_iter(hosts, headers):
	for header, (host, port) in hosts.items():
		headers['Host'] = header
		element = headers.element('Host')
		assert port == element.port
		assert host == element.hostname
		yield element


def test_invalid_host_header(headers):
	invalids = list('\x7F()<>@,;:/\[\]={} \t\\\\^"\'') + map(chr, range(0x00, 0x1F))
	# FIXME: currently failing chars
	invalids.remove(';')
	invalids.remove('\n')
	invalids.remove('\x00')
	for invalid in invalids:
		headers['Host'] = b'foo%sbar' % (invalid,)
		with pytest.raises(InvalidHeader):
			headers.element('Host')
