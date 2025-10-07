from datetime import datetime

from app.api.routes import _parse_iso_datetime, _parse_iso_datetimes, _parse_ints


def test_parse_iso_datetime_result():
    assert (
        _parse_iso_datetime('2025-10-01T11:22:33.044Z')
        == datetime(2025, 10, 1, 11, 22, 33, 44000)
    )

def test_parse_iso_datetimes_result():
    assert (
        _parse_iso_datetimes(
            '2025-10-01T11:22:33.044Z'
            + ',2025-10-31T00:12:34.567Z'
            + ',2025-12-31T23:59:59.999Z'
        ) == [
            datetime(2025, 10,  1, 11, 22, 33,  44_000),
            datetime(2025, 10, 31,  0, 12, 34, 567_000),
            datetime(2025, 12, 31, 23, 59, 59, 999_000),
        ]
    )


def test_parse_ints_result():
    assert _parse_ints('1,2,3,4,50,60,123,1000') == [1, 2, 3, 4, 50, 60, 123, 1000]

def test_parse_ints_single_int():
    assert _parse_ints('1') == [1]

def test_parse_ints_allowing_duplicates():
    assert _parse_ints('1,2,3,4,50,50,60,123,123') == [1, 2, 3, 4, 50, 50, 60, 123, 123]

def test_parse_ints_ignoring_duplicates():
    assert (
        _parse_ints('1,2,3,4,50,50,60,123,123', True) == [1, 2, 3, 4, 50, 60, 123]
    )
