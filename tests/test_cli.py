import subprocess


def test_cli():
	assert 'GET / HTTP/1.1\r\n\r\n' == subprocess.check_output(['python', '-m', 'httoop', 'request'])
	assert 'HTTP/1.1 200 OK\r\n\r\n' == subprocess.check_output(['python', '-m', 'httoop', 'response'])
	assert 'PUT /foo HTTP/1.1\r\nHost: foo\r\n\r\n' == subprocess.check_output(['python', '-m', 'httoop', 'request', '-m', 'PUT', '-u', '/foo', '-H', 'Host: foo'])
	assert 'HTTP/1.1 400 Bad Request\r\n\r\n' == subprocess.check_output(['python', '-m', 'httoop', 'response', '-s', '400'])
