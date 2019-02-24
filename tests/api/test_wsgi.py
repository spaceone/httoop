# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pytest
import sys

from httoop import Request, Response
from httoop.gateway.wsgi import WSGI


class WSGIClient(WSGI):

	def __init__(self, *args, **kwargs):
		self.request = Request()
		self.response = Response()
		super(WSGIClient, self).__init__(*args, **kwargs)


OK = b'200 OK'
output = b'Hello World!'
response_headers = [(b'Content-type', b'text/plain'), (b'Content-Length', str(len(output)).encode('ascii'))]


def application1(environ, start_response):
	start_response(OK, response_headers)
	return [output]


def application2(environ, start_response):
	start_response(OK, response_headers)
	return [output[:5], output[5:]]


def application3(environ, start_response):
	start_response(OK, response_headers)
	yield output


def application4(environ, start_response):
	start_response(OK, response_headers)
	yield output[:5]
	yield output[5:]


def application5(environ, start_response):
	write = start_response(OK, response_headers)
	write(output)
	return []


def application6(environ, start_response):
	write = start_response(OK, response_headers)
	write(output[:5])
	write(output[5:])
	return []


def application7(environ, start_response):
	write = start_response(OK, response_headers)
	write(output)
	return ['']


def application8(environ, start_response):
	write = start_response(OK, response_headers)
	write(output)
	return [output]


@pytest.mark.parametrize('application', [
	application1,
	application2,
	application3,
	application4,
	application5,
	application6,
	application7,
	application8,
])
def test_wsgi_success(application):
	client = WSGIClient()
	client(application)
	assert client.response.headers
	assert bytes(client.response.body) == output


def application9(environ, start_response):
	return [output]


def application10(environ, start_response):
	yield output


def application11(environ, start_response):
	start_response(OK, response_headers)
	start_response(OK, response_headers)
	yield output


def application12(environ, start_response):
	yield ''


def application13(environ, start_response):
	return ['']


@pytest.mark.parametrize('application', [
	pytest.param(application9, marks=pytest.mark.xfail(reason='No write() call currently')),
	pytest.param(application10, marks=pytest.mark.xfail(reason='No write() call currently')),
	application11,
	application12,
	application13,
])
def test_wsgi_failure(application):
	client = WSGIClient()
	with pytest.raises(RuntimeError):
		client(application)


def application14(environ, start_response):
	raise ValueError('test')


def test_eror_reraising():
	client = WSGIClient()
	with pytest.raises(ValueError):
		client(application14)


def application15(environ, start_response):
	result = environ['HTTP_HOST'] == 'foobar' and environ['CONTENT_LENGTH'] == '0' and environ['CONTENT_TYPE'] == 'text/html'
	try:
		raise ValueError(result)
	except ValueError:
		start_response('200 OK', {}, sys.exc_info())
	return []


def test_essential_parameters():
	client = WSGIClient({'CONTENT_TYPE': 'text/html', 'CONTENT_LENGTH': '0', 'HTTP_HOST': 'foobar'})
	client(application15)
	assert client.exc_info[1].args[0] is True


def test_client_reraising():
	client = WSGIClient({'CONTENT_TYPE': 'text/html', 'CONTENT_LENGTH': '0', 'HTTP_HOST': 'foobar'})
	client.headers_sent = True
	with pytest.raises(ValueError) as exc:
		client(application15)
	assert exc.value.args[0] is True
