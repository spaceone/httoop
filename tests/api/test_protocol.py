# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from httoop.exceptions import InvalidLine


def test_protocol_tuple(request_):
	request_.protocol.parse(b'HTTP/1.0')
	assert request_.protocol == (1, 0)


def test_set_protocol_tuple(request_):
	request_.protocol = (1, 0)
	assert bytes(request_.protocol) == b'HTTP/1.0'


def test_protocol_minor_mayor(request_):
	request_.protocol = (1, 0)
	assert request_.protocol.major == 1
	assert request_.protocol.minor == 0


def test_protocol_compare_bytes(request_):
	request_.protocol = (1, 0)
	assert request_.protocol == b'HTTP/1.0'


def test_set_protocol_to_protocol(request_, response):
	request_.protocol = (1, 0)
	response.protocol = request_.protocol
	assert response.protocol == (1, 0)


@pytest.mark.parametrize('invalid', [
	u'HTTP/111',
	u'HTTP/2',
	u'HTTP/3',
	u'HTTP→1.1',
	u'HTTÖ/1.1',
])
def test_invalid_protocol(request_, invalid):
	with pytest.raises(InvalidLine):
		request_.protocol.set(invalid)


def test_protocol_comparision(request_):
	request_.protocol = (1, 2)
	assert request_.protocol < (2, 0)
	assert request_.protocol < 2
	assert request_.protocol > (0, 9)
	assert request_.protocol > 0
	assert request_.protocol < (1, 3)
	assert request_.protocol > (1, 0)
	assert request_.protocol == (1, 2)
	assert request_.protocol != (2, 0)
	assert request_.protocol == 1
	assert request_.protocol != 0
	assert request_.protocol != 2
	assert request_.protocol != 'foo'
	assert request_.protocol != b'foo'
	assert request_.protocol >= (1, 2)
	assert request_.protocol >= (1, 1)
	assert request_.protocol <= (1, 2)
	assert request_.protocol <= (2, 1)
	assert not (request_.protocol != 1)
