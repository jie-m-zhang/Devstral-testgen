#!/usr/bin/env python
"""
Test to reproduce the issue with django.utils.http.parse_http_date
where two-digit year check is incorrect.

The bug: RFC 7231 states that years appearing more than 50 years in the future
should be interpreted as representing the most recent year in the past with the
same last two digits. The buggy code hardcodes 0-69 to 2000-2069 and 70-99 to
1970-1999, instead of comparing against the current year.
"""

import datetime
import unittest
from unittest.mock import patch

# Import the function to test
from django.utils.http import parse_http_date

def test_two_digit_year_interpretation():
    """
    Test that two-digit years are interpreted correctly according to RFC 7231.

    In year 2070, a two-digit year "75" should be interpreted as 2075 (only 5 years
    in the future), not 1975 (100 years in the past).

    This test will:
    - FAIL on buggy code (interprets "75" as 1975)
    - PASS on fixed code (interprets "75" as 2075)
    """
    # Test case: In year 2070, "75" should be 2075
    # Create a date string with two-digit year "75"
    date_str = "Wednesday, 01-Jan-75 00:00:00 GMT"

    # Mock the current year to be 2070
    mock_date = datetime.datetime(2070, 1, 1, 0, 0, 0)
    with patch('django.utils.http.datetime') as mock_datetime:
        mock_datetime.datetime.utcnow.return_value = mock_date
        mock_datetime.datetime.side_effect = datetime.datetime

        # Parse the date
        result = parse_http_date(date_str)

        # Convert to datetime to check the year
        result_dt = datetime.datetime.utcfromtimestamp(result)

        # In 2070, year "75" should be interpreted as 2075 (only 5 years in the future)
        # because 2075 - 2070 = 5 <= 50
        expected_year = 2075

        print(f"Parsed date: {result_dt}")
        print(f"Expected year: {expected_year}")
        print(f"Actual year: {result_dt.year}")

        # This assertion will FAIL on buggy code (gets 1975) and PASS on fixed code (gets 2075)
        assert result_dt.year == expected_year, \
            f"Expected year {expected_year}, but got {result_dt.year}. " \
            f"Two-digit year '75' should be interpreted as {expected_year} when current year is 2070."

    print("Test passed - two-digit year interpretation is correct!")

if __name__ == "__main__":
    test_two_digit_year_interpretation()