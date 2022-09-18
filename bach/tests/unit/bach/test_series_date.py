"""
Copyright 2022 Objectiv B.V.
"""
import datetime

import numpy
import pytest

from bach import SeriesDate
from bach.expression import Expression


def test_supported_value_to_literal(dialect):
    def assert_call(value, expected_token_value: str):
        result = SeriesDate.supported_value_to_literal(dialect=dialect, value=value, dtype='timestamp')
        assert result == Expression.string_value(expected_token_value)

    # ## datetime
    assert_call(datetime.datetime(1999, 1, 15, 13, 37, 1, 23), '1999-01-15')
    assert_call(datetime.datetime(1969, 12, 31, 1, 2, 3, 00),  '1969-12-31')
    assert_call(datetime.datetime(2050, 7, 7, 7, 7, 7, 7),     '2050-07-07')

    # TODO: datetime with timezone set

    # ## date
    assert_call(datetime.date(1999, 1, 15),  '1999-01-15')
    assert_call(datetime.date(1969, 12, 31), '1969-12-31')
    assert_call(datetime.date(2050, 7, 7),   '2050-07-07')

    # ## np.datetime64
    assert_call(numpy.datetime64('2022-01-01 12:34:56.7800'),                   '2022-01-01')
    assert_call(numpy.datetime64('2022-01-03'),                                 '2022-01-03')
    assert_call(numpy.datetime64('1995-03-31 01:33:37.123456'),                 '1995-03-31')
    # datetime64 objects with differing precision. We only support up to milliseconds
    assert_call(numpy.datetime64('1995-03-31 01:33:37.1234567'),                '1995-03-31')
    assert_call(numpy.datetime64('1995-03-31 01:33:37.123456789012', 's'),      '1995-03-31')
    assert_call(numpy.datetime64('1995-03-31 01:33:37.123456789012', 'ms'),     '1995-03-31')
    assert_call(numpy.datetime64('1995-03-31 01:33:37.123456789012', 'us'),     '1995-03-31')
    assert_call(numpy.datetime64('1995-03-31 01:33:37.123456789012', 'ns'),     '1995-03-31')
    # rounding can be a bit unexpected because of limited precision, therefore we always truncate excess precision
    assert_call(numpy.datetime64('1995-03-31 01:33:37.123456001', 'ns'),        '1995-03-31')
    assert_call(numpy.datetime64('1995-03-31 01:33:37.123456499', 'ns'),        '1995-03-31')
    assert_call(numpy.datetime64('1995-03-31 01:33:37.123456500', 'ns'),        '1995-03-31')
    assert_call(numpy.datetime64('1995-03-31 01:33:37.123456569', 'ns'),        '1995-03-31')
    assert_call(numpy.datetime64('1995-03-31 01:33:37.123456999', 'ns'),        '1995-03-31')

    # Special case: Not-a-Time will be represented as NULL
    nat = numpy.datetime64('NaT')
    dtype = 'date'
    assert SeriesDate.supported_value_to_literal(dialect, nat, dtype) == Expression.construct('NULL')

    # ## strings
    assert_call('2022-01-01 12:34:56.7800',    '2022-01-01')
    assert_call('1995-03-31 01:33:37.123456',  '1995-03-31')
    assert_call('1999-12-31 23:59:59',         '1999-12-31')
    assert_call('1999-12-31 23:59',            '1999-12-31')
    assert_call('2022-01-03',                  '2022-01-03')

    # ## None
    assert SeriesDate.supported_value_to_literal(dialect, None, dtype) == Expression.construct('NULL')


def test_supported_value_to_literal_str_non_happy_path(dialect):
    dtype = 'date'
    with pytest.raises(ValueError, match=r'Not a valid string literal: .* for date'):
        SeriesDate.supported_value_to_literal(dialect, '2022-01-03 aa:bb', dtype)

    with pytest.raises(ValueError, match=r'Not a valid string literal: .* for date'):
        SeriesDate.supported_value_to_literal(dialect, '01/03/99 12:13:00', dtype)

    with pytest.raises(ValueError, match=r'Not a valid string literal: .* for date'):
        SeriesDate.supported_value_to_literal(dialect, '01/03/99 12:13:00', dtype)
