
import pytest

from httoop import URI


@pytest.mark.parametrize('url,expected', (
    ('ftp://ftp.is.co.za/rfc/rfc1808.txt', ('ftp', '', '', 'ftp.is.co.za', 21, '/rfc/rfc1808.txt', '', '')),
    ('http://www.ietf.org/rfc/rfc2396.txt', ('http', '', '', 'www.ietf.org', 80, '/rfc/rfc2396.txt', '', '')),
    pytest.param('ldap://[2001:db8::7]/c=GB?objectClass?one', ('ldap', '', '', '[2001:db8::7]', 389, '/c=GB', 'objectClass?one', ''), marks=pytest.mark.skipif(True, reason='Parse query in ldap URI?')),
    ('mailto:John.Doe@example.com', ('mailto', '', '', '', None, 'John.Doe@example.com', '', '')),
    ('news:comp.infosystems.www.servers.unix', ('news', '', '', '', None, 'comp.infosystems.www.servers.unix', '', '')),
    ('tel:+1-816-555-1212', ('tel', '', '', '', None, '+1-816-555-1212', '', '')),
    ('telnet://192.0.2.16:80/', ('telnet', '', '', '192.0.2.16', 80, '/', '', '')),
    ('urn:oasis:names:specification:docbook:dtd:xml:4.1.2', ('urn', '', '', '', None, 'oasis:names:specification:docbook:dtd:xml:4.1.2', '', '')),
    ('file:///tmp/junk.txt', ('file', '', '', '', None, '/tmp/junk.txt', '', '')),
    ('imap://mail.python.org/mbox1', ('imap', '', '', 'mail.python.org', 143, '/mbox1', '', '')),
    ('mms://wms.sys.hinet.net/cts/Drama/09006251100.asf', ('mms', '', '', 'wms.sys.hinet.net', 1755, '/cts/Drama/09006251100.asf', '', '')),
    ('nfs://server/path/to/file.txt', ('nfs', '', '', 'server', 2049, '/path/to/file.txt', '', '')),
    ('svn+ssh://svn.zope.org/repos/main/ZConfig/trunk/', ('svn+ssh', '', '', 'svn.zope.org', 22, '/repos/main/ZConfig/trunk/', '', '')),
    ('git+ssh://git@github.com/user/project.git', ('git+ssh', 'git', '', 'github.com', 22, '/user/project.git', '', '')),
))
def test_parse_scheme(url, expected):
    uri = URI(url)
    assert uri.tuple == expected
    assert bytes(uri) == bytes(URI(expected))
