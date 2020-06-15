import sys
import tempfile
import subprocess


def test_cli():
	assert b'GET / HTTP/1.1\r\n\r\n' == subprocess.check_output([sys.executable, '-m', 'httoop', 'request'])
	assert b'HTTP/1.1 200 OK\r\n\r\n' == subprocess.check_output([sys.executable, '-m', 'httoop', 'response'])
	assert b'PUT /foo HTTP/1.1\r\nHost: foo\r\n\r\n' == subprocess.check_output([sys.executable, '-m', 'httoop', 'request', '-m', 'PUT', '-u', '/foo', '-H', 'Host: foo'])
	assert b'HTTP/1.1 400 Evil Request\r\n\r\n' == subprocess.check_output([sys.executable, '-m', 'httoop', 'response', '-s', '400', '--reason', 'Evil Request'])
	assert b'GET / HTTP/1.0\r\n\r\n' == subprocess.check_output([sys.executable, '-m', 'httoop', 'request', '--protocol', '1.0'])
	#assert b'GET / HTTP/1.0\r\n\r\n' == subprocess.check_output([sys.executable, '-m', 'httoop', 'request', '--protocol', 'HTTP/1.0'])
	p = subprocess.Popen([sys.executable, '-m', 'httoop', 'request', '-b', '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
	stdout, stderr = p.communicate(b'test')
	assert b'GET / HTTP/1.1\r\n\r\ntest' == stdout

	with tempfile.NamedTemporaryFile() as fd:
		fd.write(b'test')
		fd.flush()
		stdout = subprocess.check_output([sys.executable, '-m', 'httoop', 'request', '-b', '@%s' % (fd.name,)])
		assert b'GET / HTTP/1.1\r\n\r\ntest' == stdout


def test_invalid_input():
	assert b'GET / HTTP/1.1\r\n\r\n' == subprocess.check_output([sys.executable, '-m', 'httoop', 'request', '--protocol', '1:0', '-H', 'foo'])
