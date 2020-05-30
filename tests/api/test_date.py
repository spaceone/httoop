from __future__ import unicode_literals
from httoop import Date, InvalidDate
import pytest
import datetime


dates = [{
	'datetime': datetime.datetime(1994, 11, 6, 8, 49, 37),
	'timestamp': 784111777.0,
	'lt': Date(784111776.0),
	'gt': Date(784111778.0),
	'gmtime': (1994, 11, 6, 8, 49, 37, 6, 310, 0),
	'formats': {
		'Sun, 06 Nov 1994 08:49:37 GMT',  # RFC 822 / RFC 1123 / RFC 2822
		'Sunday, 06-Nov-94 08:49:37 GMT',  # RFC 850 / RFC 1036
		'Sun Nov  6 08:49:37 1994',  # C asctime
	},
}]


@pytest.mark.parametrize('date,expected,lt,gt', [(date, data['datetime'], data['lt'], data['gt']) for data in dates for date in data['formats']])
def test_date_datetime(date, expected, lt, gt):
	for d in (Date.parse(date.encode('utf-8')), Date(date)):
		assert d is not None
		assert d.datetime == expected
		assert d == expected
		assert d == Date(date)

	assert gt > date
	assert lt < date


@pytest.mark.parametrize('date,expected,lt,gt', [(date, data['timestamp'], data['lt'], data['gt']) for data in dates for date in data['formats']])
def test_date_timestamp(date, expected, lt, gt):
	for d in (Date.parse(date.encode('utf-8')), Date(date)):
		assert d is not None
		assert float(d) == expected
		assert d == expected
		assert d == Date(date)

	assert gt > date
	assert lt < date


@pytest.mark.parametrize('date,expected,lt,gt', [(date, data['gmtime'], data['lt'], data['gt']) for data in dates for date in data['formats']])
def test_date_gmtime(date, expected, lt, gt):
	for d in (Date.parse(date.encode('utf-8')), Date(date)):
		assert d is not None
		assert d.gmtime == expected
		assert d == expected
		assert d == Date(date)

	assert gt > date
	assert lt < date


def test_date_comparing_none():
	d = Date(datetime.datetime(1994, 11, 6, 8, 49, 37))
	assert d == Date(d)
	assert not d == None  # noqa
	assert d > None
	assert not d < None


@pytest.mark.parametrize('invalid', [
	'2017-02-02',
	'2017-02-02 08:49:37',
])
def test_invalid_date(invalid):
	with pytest.raises(InvalidDate):
		Date(invalid)

	d = Date(784111777.0)
	assert d != invalid
	assert not d == invalid
	assert d > invalid
	assert not d < invalid

	with pytest.raises(TypeError):
		Date({})
