
import pytest

from httoop import URI


@pytest.mark.parametrize('url,expected', (
    (b'http://..', ('http', '', '', '..', 80, '', '', '')),
    (b'http:///..', ('http', '', '', '', 80, '/', '', '')),
    (b'http://.', ('http', '', '', '.', 80, '', '', '')),
    (b'http:///.', ('http', '', '', '', 80, '/', '', '')),
    (b'http:.', ('http', '', '', '', 80, '/', '', '')),
    (b'http:..', ('http', '', '', '', 80, '/', '', '')),
    (b'http:/', ('http', '', '', '', 80, '/', '', '')),
    pytest.param(b'http://f/..%2f..', ('http', '', '', 'f', 80, '/', '', ''), marks=pytest.mark.xfail(reason='Incorrect but we want to preserve /.')),
))
def test_abspath(url, expected):
    uri = URI()
    uri.parse(url)
    uri.abspath()
    assert uri.tuple == expected
    uri.normalize()
    assert uri.tuple == expected
