from httoop import Date
import datetime


def test_parse_rfc822_rfc1123_rfc2822_date():
	d = Date.parse('Sun, 06 Nov 1994 08:49:37 GMT')
	assert d is not None
	assert d.to_datetime() == datetime.datetime(1994, 11, 6, 8, 49, 37)
#	assert d.timestamp == 784108177.0
#	assert d.to_timetuple() == (1994, 11, 6, 8, 49, 37, 0)


def test_parse_rfc850_rfc1036_date():
	d = Date.parse('Sunday, 06-Nov-94 08:49:37 GMT')
	assert d is not None
	assert d.to_datetime() == datetime.datetime(1994, 11, 6, 8, 49, 37)
#	assert d.timestamp == 784108177.0
#	assert d.to_timetuple() == (1994, 11, 6, 8, 49, 37, 0)


def test_parse_asctime_date():
	d = Date.parse('Sun Nov  6 08:49:37 1994')
	assert d is not None
	assert d.to_datetime() == datetime.datetime(1994, 11, 6, 8, 49, 37)
#	assert d.timestamp == 784108177.0
#	assert d.to_timetuple() == (1994, 11, 6, 8, 49, 37, 0)
