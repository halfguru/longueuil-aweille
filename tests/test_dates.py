from datetime import datetime

from longueuil_aweille.dates import (
    RegistrationWindow,
    format_time_remaining,
    parse_french_datetime,
)


def test_parse_standard_french_datetime():
    dt = parse_french_datetime("16 Septembre 2026, 18:30")
    assert dt == datetime(2026, 9, 16, 18, 30)


def test_parse_premier_french_datetime():
    dt = parse_french_datetime("1er Septembre 2026, 12:00")
    assert dt == datetime(2026, 9, 1, 12, 0)


def test_parse_date_only():
    dt = parse_french_datetime("3 Octobre 2026")
    assert dt == datetime(2026, 10, 3, 0, 0)


def test_parse_case_insensitive_and_accents():
    dt = parse_french_datetime("25 FÉVRIER 2026, 09h15")
    assert dt == datetime(2026, 2, 25, 9, 15)

    dt2 = parse_french_datetime("15 août 2026, 14:00")
    assert dt2 == datetime(2026, 8, 15, 14, 0)


def test_parse_invalid_date():
    assert parse_french_datetime("") is None
    assert parse_french_datetime("Not a date") is None
    assert parse_french_datetime("32 Janvier 2026") is None


def test_format_time_remaining():
    now = datetime(2026, 9, 15, 10, 0, 0)
    target = datetime(2026, 9, 16, 18, 30, 15)
    # 1 day, 8 hours, 30 minutes, 15 seconds
    formatted = format_time_remaining(target, now=now)
    assert formatted == "1d 8h 30m 15s"


def test_format_time_remaining_past():
    now = datetime(2026, 9, 16, 18, 30, 0)
    target = datetime(2026, 9, 16, 18, 20, 0)
    assert format_time_remaining(target, now=now) == "now"


def test_registration_window_is_open():
    window = RegistrationWindow(
        resident_start=datetime(2026, 9, 16, 18, 30),
        resident_end=datetime(2026, 9, 30, 8, 0),
    )
    # Before
    assert not window.is_open and window.seconds_until_open(datetime(2026, 9, 16, 18, 0)) == 1800.0

    # During (simulate now)
    now_during = datetime(2026, 9, 16, 18, 35)
    assert window.seconds_until_open(now_during) == 0.0


async def test_countdown_sleep_expires():
    from datetime import timedelta

    from longueuil_aweille.dates import countdown_sleep

    target = datetime.now() + timedelta(milliseconds=50)
    # Total seconds small so it finishes immediately
    await countdown_sleep(0.05, target=target, update_interval=0.01)


async def test_countdown_sleep_with_console():
    from datetime import timedelta
    from unittest.mock import MagicMock

    from rich.console import Console

    from longueuil_aweille.dates import countdown_sleep

    console = MagicMock(spec=Console)
    status_mock = MagicMock()
    console.status.return_value.__enter__.return_value = status_mock

    target = datetime.now() + timedelta(milliseconds=50)
    await countdown_sleep(0.05, target=target, update_interval=0.01, console=console)

    console.status.assert_called_once()
    assert status_mock.update.called
