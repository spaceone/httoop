import re
import subprocess
import sys
import tempfile


def test_cli_compose():
    assert subprocess.check_output([sys.executable, '-m', 'httoop', 'compose', 'request']) == b'GET / HTTP/1.1\r\n\r\n'
    assert subprocess.check_output([sys.executable, '-m', 'httoop', 'compose', 'response']) == b'HTTP/1.1 200 OK\r\n\r\n'
    assert subprocess.check_output([sys.executable, '-m', 'httoop', 'compose', 'request', '-m', 'PUT', '-u', '/foo', '-H', 'Host: foo']) == b'PUT /foo HTTP/1.1\r\nHost: foo\r\n\r\n'
    assert subprocess.check_output([sys.executable, '-m', 'httoop', 'compose', 'response', '-s', '400', '--reason', 'Evil Request']) == b'HTTP/1.1 400 Evil Request\r\n\r\n'
    assert subprocess.check_output([sys.executable, '-m', 'httoop', 'compose', 'request', '--protocol', '1.0']) == b'GET / HTTP/1.0\r\n\r\n'
    # assert b'GET / HTTP/1.0\r\n\r\n' == subprocess.check_output([sys.executable, '-m', 'httoop', 'compose', 'request', '--protocol', 'HTTP/1.0'])
    p = subprocess.Popen([sys.executable, '-m', 'httoop', 'compose', 'request', '-b', '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    stdout, stderr = p.communicate(b'test')
    assert stdout == b'GET / HTTP/1.1\r\n\r\ntest'

    with tempfile.NamedTemporaryFile() as fd:
        fd.write(b'test')
        fd.flush()
        stdout = subprocess.check_output([sys.executable, '-m', 'httoop', 'compose', 'request', '-b', '@%s' % (fd.name,)])
        assert stdout == b'GET / HTTP/1.1\r\n\r\ntest'


def test_cli_parse():
    with tempfile.NamedTemporaryFile() as fd:
        fd.write(b'PUT /foo HTTP/1.1\r\nHost: foo\r\n\r\n')
        fd.flush()
        stdout = subprocess.check_output([sys.executable, '-m', 'httoop', 'parse', 'request', '--file', fd.name])
        assert re.match(br"^<HTTP Response\(200 text/plain; charset=UTF\-8\)>\n<HTTP Headers\(\[\('Server', b'httoop/\d+\.\d+\.\d+'\)\]\)>\n<HTTP Body\(0x[0-9a-f]+\)>\n$", stdout)

    p = subprocess.Popen([sys.executable, '-m', 'httoop', 'parse', 'response'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    stdout, stderr = p.communicate(b'HTTP/1.1 400 Evil Request\r\n\r\n')
    assert re.match(br"^<HTTP Response\(400 text/plain; charset=UTF\-8\)>\n<HTTP Headers\(\[\('Content\-Length', b'0'\)\]\)>\n<HTTP Body\(0x[0-9a-f]+\)>\nb''\n$", stdout), stdout


def test_invalid_input():
    assert subprocess.check_output([sys.executable, '-m', 'httoop', 'compose', 'request', '--protocol', '1:0', '-H', 'foo']) == b'GET / HTTP/1.1\r\n\r\n'
