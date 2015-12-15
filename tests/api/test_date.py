from httoop import Date
import pytest
import datetime


dates = [{
	'datetime': datetime.datetime(1994, 11, 6, 8, 49, 37),
	'timestamp': 784111777.0,
	'gmtime': (1994, 11, 6, 8, 49, 37, 6, 310, 0),
	'formats': {
		'Sun, 06 Nov 1994 08:49:37 GMT', # RFC 822 / RFC 1123 / RFC 2822
		'Sunday, 06-Nov-94 08:49:37 GMT', # RFC 850 / RFC 1036
		'Sun Nov  6 08:49:37 1994', # C asctime
	},
}]


@pytest.mark.parametrize('date,expected', [(date, data['datetime']) for data in dates for date in data['formats']])
def test_date_datetime(date, expected):
	d = Date.parse(date)
	assert d is not None
	assert d.datetime == expected
	assert d == expected


@pytest.mark.parametrize('date,expected', [(date, data['timestamp']) for data in dates for date in data['formats']])
def test_date_timestamp(date, expected):
	d = Date.parse(date)
	assert d is not None
	assert float(d) == expected
	assert d == expected


@pytest.mark.parametrize('date,expected', [(date, data['gmtime']) for data in dates for date in data['formats']])
def test_date_gmtime(date, expected):
	d = Date.parse(date)
	assert d is not None
	assert d.gmtime == expected
	assert d == expected
