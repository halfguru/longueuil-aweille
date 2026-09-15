import asyncio
import logging
import re
from dataclasses import dataclass
from datetime import datetime

from playwright.async_api import Locator, Page
from rich.console import Console

logger = logging.getLogger(__name__)

FRENCH_MONTHS = {
    "janvier": 1,
    "fevrier": 2,
    "février": 2,
    "mars": 3,
    "avril": 4,
    "mai": 5,
    "juin": 6,
    "juillet": 7,
    "aout": 8,
    "août": 8,
    "septembre": 9,
    "octobre": 10,
    "novembre": 11,
    "decembre": 12,
    "décembre": 12,
}

_DATE_PATTERN = re.compile(
    r"(\d{1,2})(?:er)?\s+([A-Za-zÀ-ÿ]+)\s+(\d{4})(?:[,\s]+(\d{1,2})[:hH](\d{2}))?",
    re.IGNORECASE,
)


def parse_french_datetime(text: str) -> datetime | None:
    """Parse a French date string into a datetime object.

    Supports formats like:
      - '16 Septembre 2026, 18:30'
      - '1er Septembre 2026, 12:00'
      - '3 Octobre 2026'
    """
    if not text:
        return None

    cleaned = text.strip()
    match = _DATE_PATTERN.search(cleaned)
    if not match:
        return None

    day_str, month_str, year_str, hour_str, min_str = match.groups()

    month_lower = month_str.lower()
    month = FRENCH_MONTHS.get(month_lower)
    if month is None:
        return None

    day = int(day_str)
    year = int(year_str)
    hour = int(hour_str) if hour_str is not None else 0
    minute = int(min_str) if min_str is not None else 0

    try:
        return datetime(year, month, day, hour, minute)
    except ValueError:
        return None


def format_time_remaining(target: datetime, now: datetime | None = None) -> str:
    """Format the duration between now and target into a human-readable string."""
    if now is None:
        now = datetime.now()

    diff = target - now
    total_seconds = int(diff.total_seconds())
    if total_seconds <= 0:
        return "now"

    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    parts: list[str] = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")

    return " ".join(parts)


@dataclass
class RegistrationWindow:
    resident_start: datetime | None = None
    resident_end: datetime | None = None
    raw_resident_start: str = ""
    raw_resident_end: str = ""

    @property
    def is_open(self) -> bool:
        """Check if resident registration is currently open."""
        if not self.resident_start:
            return False
        now = datetime.now()
        if now < self.resident_start:
            return False
        return not bool(self.resident_end and now > self.resident_end)

    def seconds_until_open(self, now: datetime | None = None) -> float:
        """Seconds remaining until resident registration opens. Returns 0 if already open."""
        if not self.resident_start:
            return 0.0
        if now is None:
            now = datetime.now()
        diff = (self.resident_start - now).total_seconds()
        return max(0.0, diff)


async def fetch_registration_window(
    container: Locator, page: Page, timeout_ms: int = 3000
) -> RegistrationWindow | None:
    """Extract registration dates from the info popup inside a table row or container."""
    try:
        info_btn = container.locator("input[type='image'][title*=\"dates d'inscription\"]")
        if await info_btn.count() == 0:
            return None

        await info_btn.first.click()
        await page.wait_for_selector("table.DatesInscriptions", state="visible", timeout=timeout_ms)

        dates_table = page.locator("table.DatesInscriptions")
        if await dates_table.count() == 0:
            return None

        window = RegistrationWindow()
        current_lieu = ""

        rows = await dates_table.first.locator("tr").all()
        for row in rows:
            lieu_cell = row.locator("td.Lieu")
            if await lieu_cell.count() > 0:
                current_lieu = await lieu_cell.inner_text()

            if "Internet" not in current_lieu:
                continue

            clientelle_cell = row.locator("td.Clientele")
            if await clientelle_cell.count() == 0:
                continue

            clientelle = await clientelle_cell.inner_text()
            if "Résident" not in clientelle or "Non" in clientelle:
                continue

            date_cells = row.locator("td.Dates")
            if await date_cells.count() >= 2:
                start_str = (await date_cells.nth(0).inner_text()).strip()
                end_str = (await date_cells.nth(1).inner_text()).strip()
                window.raw_resident_start = start_str
                window.raw_resident_end = end_str
                window.resident_start = parse_french_datetime(start_str)
                window.resident_end = parse_french_datetime(end_str)
                break

        close_btn = page.locator("a[id*='ctlFermer']")
        if await close_btn.count() > 0:
            await close_btn.first.click()
            await page.wait_for_load_state("networkidle")

        return window if window.raw_resident_start else None

    except Exception as e:
        logger.debug(f"Error extracting registration window: {e}")
        return None


def prevent_sleep() -> None:
    """Prevent Windows from sleeping while waiting for registration."""
    import sys

    if sys.platform == "win32":
        try:
            import ctypes

            es_continuous = 0x80000000
            es_system_required = 0x00000001
            ctypes.windll.kernel32.SetThreadExecutionState(es_continuous | es_system_required)
            logger.debug("Preventing system sleep (ES_SYSTEM_REQUIRED set)")
        except Exception as e:
            logger.debug(f"Could not set thread execution state: {e}")


def restore_sleep() -> None:
    """Restore normal system sleep behavior."""
    import sys

    if sys.platform == "win32":
        try:
            import ctypes

            es_continuous = 0x80000000
            ctypes.windll.kernel32.SetThreadExecutionState(es_continuous)
            logger.debug("Restored normal system sleep")
        except Exception as e:
            logger.debug(f"Could not restore thread execution state: {e}")


async def countdown_sleep(
    total_seconds: float,
    target: datetime,
    label: str = "registration opens",
    update_interval: float = 1.0,
    console: Console | None = None,
) -> None:
    """Sleep asynchronously while showing a live countdown until target time."""
    start = asyncio.get_running_loop().time()
    last_log_time = 0.0

    if console is not None:
        rem_str = format_time_remaining(target)
        status_text = f"[bold cyan]Standing by:[/] [bold]{rem_str}[/] remaining until {label}..."
        with console.status(status_text, spinner="dots") as status:
            while True:
                now = datetime.now()
                remaining = (target - now).total_seconds()
                if remaining <= 0:
                    break

                elapsed = asyncio.get_running_loop().time() - start
                if elapsed >= total_seconds:
                    break

                rem_str = format_time_remaining(target, now)
                status.update(
                    f"[bold cyan]Standing by:[/] [bold]{rem_str}[/] remaining until {label}..."
                )

                sleep_chunk = min(update_interval, max(0.1, remaining))
                await asyncio.sleep(sleep_chunk)
    else:
        while True:
            now = datetime.now()
            remaining = (target - now).total_seconds()
            if remaining <= 0:
                break

            elapsed = asyncio.get_running_loop().time() - start
            if elapsed >= total_seconds:
                break

            # Log countdown progress: every 60 seconds (or every 5 seconds if remaining < 60s)
            log_step = 5.0 if remaining < 60 else 60.0
            if elapsed - last_log_time >= log_step or last_log_time == 0.0:
                last_log_time = elapsed
                rem_str = format_time_remaining(target, now)
                logger.info(f"Standing by: {rem_str} remaining until {label}...")

            sleep_chunk = min(update_interval, max(0.1, remaining))
            await asyncio.sleep(sleep_chunk)
