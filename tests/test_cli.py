import subprocess


def test_cli():
	assert b'GET / HTTP/1.1\r\n\r\n' == subprocess.check_output(['python', '-m', 'httoop', 'request'])
	assert b'HTTP/1.1 200 OK\r\n\r\n' == subprocess.check_output(['python', '-m', 'httoop', 'response'])
	assert b'PUT /foo HTTP/1.1\r\nHost: foo\r\n\r\n' == subprocess.check_output(['python', '-m', 'httoop', 'request', '-m', 'PUT', '-u', '/foo', '-H', 'Host: foo'])
	assert b'HTTP/1.1 400 Bad Request\r\n\r\n' == subprocess.check_output(['python', '-m', 'httoop', 'response', '-s', '400'])
