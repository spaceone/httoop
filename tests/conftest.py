from __future__ import unicode_literals

import pytest

from httoop import URI, Body, ClientStateMachine, Headers, Request, Response, ServerStateMachine


@pytest.fixture
def request_():
	return Request()


@pytest.fixture
def response():
	return Response()


@pytest.fixture
def headers():
	return Headers()


@pytest.fixture
def body():
	return Body()


@pytest.fixture
def statemachine():
	return ServerStateMachine('http', 'localhost', 8090)


@pytest.fixture
def clientstatemachine():
	c = ClientStateMachine()
	c.request = Request()
	return c


@pytest.fixture
def uri():
	return URI()
