import iso8601
import unittest
from copy import deepcopy
try:
    import cPickle as pickle
except ImportError:
    import pickle

class TestISO8601(unittest.TestCase):
    def test_iso8601_regex(self):
        assert iso8601.ISO8601_REGEX.match("2006-10-11T00:14:33Z")
    
    def test_timezone_regex(self):
        assert iso8601.TIMEZONE_REGEX.match("+01:00")
        assert iso8601.TIMEZONE_REGEX.match("+00:00")
        assert iso8601.TIMEZONE_REGEX.match("+01:20")
        assert iso8601.TIMEZONE_REGEX.match("-01:00")
    
    def test_parse_date(self):
        d = iso8601.parse_date("2006-10-20T15:34:56Z")
        assert d.year == 2006
        assert d.month == 10
        assert d.day == 20
        assert d.hour == 15
        assert d.minute == 34
        assert d.second == 56
        assert d.tzinfo == iso8601.UTC
        
    def test_parse_only_date(self):
        d = iso8601.parse_date("2006-10-20")
        assert d.year == 2006
        assert d.month == 10
        assert d.day == 20
        assert d.hour == 0
        assert d.minute == 0
        assert d.second == 0
        assert d.tzinfo == iso8601.UTC
    
    def test_parse_date_fraction(self):
        d = iso8601.parse_date("2006-10-20T15:34:56.123Z")
        assert d.year == 2006
        assert d.month == 10
        assert d.day == 20
        assert d.hour == 15
        assert d.minute == 34
        assert d.second == 56
        assert d.microsecond == 123000
        assert d.tzinfo == iso8601.UTC
    
    def test_parse_date_fraction_2(self):
        """From bug 6
        
        """
        d = iso8601.parse_date("2007-5-7T11:43:55.328Z'")
        assert d.year == 2007
        assert d.month == 5
        assert d.day == 7
        assert d.hour == 11
        assert d.minute == 43
        assert d.second == 55
        assert d.microsecond == 328000
        assert d.tzinfo == iso8601.UTC
    
    def test_parse_date_tz(self):
        d = iso8601.parse_date("2006-10-20T15:34:56.123+02:30")
        
        assert d.year == 2006
        assert d.month == 10
        assert d.day == 20
        assert d.hour == 15
        assert d.minute == 34
        assert d.second == 56
        assert d.microsecond == 123000
        assert d.tzinfo.tzname(None) == "+02:30"
        offset = d.tzinfo.utcoffset(None)
        assert offset.days == 0
        assert offset.seconds == 60 * 60 * 2.5

    def test_parse_date_tz(self):
        d = iso8601.parse_date("2006-10-20T15:34:56.123+02:30")
        assert d.year == 2006
        assert d.month == 10
        assert d.day == 20
        assert d.hour == 15
        assert d.minute == 34
        assert d.second == 56
        assert d.microsecond == 123000
        assert d.tzinfo.tzname(None) == "+02:30"
        offset = d.tzinfo.utcoffset(None)
        assert offset.days == 0
        assert offset.seconds == 60 * 60 * 2.5

    def test_parse_date_negtz(self):
        d = iso8601.parse_date("2006-10-20T15:34:56.123-02:30")
        assert d.year == 2006
        assert d.month == 10
        assert d.day == 20
        assert d.hour == 15
        assert d.minute == 34
        assert d.second == 56
        assert d.microsecond == 123000
        assert d.tzinfo.tzname(None) == "-02:30"
        offset = d.tzinfo.utcoffset(None)
        assert offset.days == -1
        assert offset.seconds == 86400 - 60 * 60 * 2.5

    def test_parse_date_2d_tz(self):
        d = iso8601.parse_date("2010-07-01 00:01:20+07")
        assert d.year == 2010
        assert d.month == 7
        assert d.day == 1
        assert d.hour == 0
        assert d.minute == 1
        assert d.second == 20
        assert d.tzinfo.tzname(None) == "+07"
        offset = d.tzinfo.utcoffset(None)
        assert offset.days == 0
        assert offset.seconds == 60 * 60 * 7
        
    def test_parse_date_2d_negtz(self):
        d = iso8601.parse_date("2010-07-01 00:01:20-07")
        assert d.year == 2010
        assert d.month == 7
        assert d.day == 1
        assert d.hour == 0
        assert d.minute == 1
        assert d.second == 20
        assert d.tzinfo.tzname(None) == "-07"
        offset = d.tzinfo.utcoffset(None)
        assert offset.days == -1
        assert offset.seconds == 86400 - 60 * 60 * 7

    def test_parse_date_2d_ms_tz(self):
        d = iso8601.parse_date("2011-07-27 21:05:12.843248+07")
        assert d.year == 2011
        assert d.month == 7
        assert d.day == 27
        assert d.hour == 21
        assert d.minute == 5
        assert d.second == 12
        assert d.microsecond == 843248
        assert d.tzinfo.tzname(None) == "+07"
        offset = d.tzinfo.utcoffset(None)
        assert offset.days == 0
        assert offset.seconds == 60 * 60 * 7

    def test_parse_date_2d_ms_negtz(self):
        d = iso8601.parse_date("2011-07-27 21:05:12.843248-07")
        assert d.year == 2011
        assert d.month == 7
        assert d.day == 27
        assert d.hour == 21
        assert d.minute == 5
        assert d.second == 12
        assert d.microsecond == 843248
        assert d.tzinfo.tzname(None) == "-07"
        offset = d.tzinfo.utcoffset(None)
        assert offset.days == -1
        assert offset.seconds == 86400 - 60 * 60 * 7
    
    def test_parse_invalid_date(self):
        self.assertRaises(iso8601.ParseError, iso8601.parse_date, None)
    
    def test_parse_invalid_date2(self):
        self.assertRaises(iso8601.ParseError, iso8601.parse_date, "23")
    
    def test_parse_no_timezone(self):
        """issue 4 - Handle datetime string without timezone
        
        This tests what happens when you parse a date with no timezone. While not
        strictly correct this is quite common. I'll assume UTC for the time zone
        in this case.
        """
        d = iso8601.parse_date("2007-01-01T08:00:00")
        assert d.year == 2007
        assert d.month == 1
        assert d.day == 1
        assert d.hour == 8
        assert d.minute == 0
        assert d.second == 0
        assert d.microsecond == 0
        assert d.tzinfo == iso8601.UTC
    
    def test_parse_no_timezone_different_default(self):
        tz = iso8601.FixedOffset(2, 0, "test offset")
        d = iso8601.parse_date("2007-01-01T08:00:00", default_timezone=tz)
        assert d.tzinfo == tz
    
    def test_space_separator(self):
        """Handle a separator other than T
        
        """
        d = iso8601.parse_date("2007-06-23 06:40:34.00Z")
        assert d.year == 2007
        assert d.month == 6
        assert d.day == 23
        assert d.hour == 6
        assert d.minute == 40
        assert d.second == 34
        assert d.microsecond == 0
        assert d.tzinfo == iso8601.UTC

    def test_deepcopy(self):
        """
        issue 20 - dates returned by parse_date do not support deepcopy

        FixedOffset can not be deep copied (raises a TypeError).
        """
        d = iso8601.parse_date('2012-06-13 11:06:47+02:00')
        d_copy = deepcopy(d)
        assert d is not d_copy
        assert d == d_copy

    def test_pickle_utc(self):
        """Tests (UTC) dates returned by parse_date can be pickled"""
        d = iso8601.parse_date('2012-09-19T01:54:30')
        d_pickled = pickle.dumps(d)
        d_copy = pickle.loads(d_pickled)
        assert d == d_copy

    def test_binary_pickle_utc(self):
        """Tests (UTC) dates returned by parse_date can be (binary) pickled"""
        d = iso8601.parse_date('2012-09-19T01:54:30')
        d_pickled = pickle.dumps(d, pickle.HIGHEST_PROTOCOL)
        d_copy = pickle.loads(d_pickled)
        assert d == d_copy

    def test_pickle_fixed(self):
        """Tests (FixedOffset) dates returned by parse_date can be pickled"""
        d = iso8601.parse_date('2012-09-19T11:59:05+10:00')
        d_pickled = pickle.dumps(d)
        d_copy = pickle.loads(d_pickled)
        assert d == d_copy

    def test_binary_pickle_fixed(self):
        """Tests (FixedOffset) dates returned by parse_date can be (binary) pickled"""
        d = iso8601.parse_date('2012-09-19T11:59:05+10:00')
        d_pickled = pickle.dumps(d, pickle.HIGHEST_PROTOCOL)
        d_copy = pickle.loads(d_pickled)
        assert d == d_copy

    def test_date_no_day(self):
        d = iso8601.parse_date('2012-12')
        assert d.year == 2012
        assert d.month == 12
        assert d.day == 1
        assert d.hour == 0
        assert d.minute == 0
        assert d.second == 0
        assert d.microsecond == 0
        assert d.tzinfo == iso8601.UTC

    def test_date_no_month(self):
        d = iso8601.parse_date('2012')
        assert d.year == 2012
        assert d.month == 1
        assert d.day == 1
        assert d.hour == 0
        assert d.minute == 0
        assert d.second == 0
        assert d.microsecond == 0
        assert d.tzinfo == iso8601.UTC

if __name__ == '__main__':
    unittest.main()

