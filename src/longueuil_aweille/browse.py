import logging
from dataclasses import dataclass

from playwright.async_api import Locator, Page, async_playwright

from .navigation import navigate_to_search
from .selectors import DEFAULT_BROWSE_SELECTORS, BrowseSelectors
from .status import (
    ActivityStatus,
    get_status_from_image_src,
    iterate_pagination,
)

logger = logging.getLogger(__name__)


class BrowseError(Exception):
    pass


class DomainNotFoundError(BrowseError):
    def __init__(self, domain: str, available_domains: list[str]):
        self.domain = domain
        self.available_domains = available_domains
        super().__init__(f"Domain '{domain}' not found. Available: {', '.join(available_domains)}")


@dataclass
class RegistrationDates:
    resident_start: str = ""
    resident_end: str = ""


@dataclass
class Activity:
    name: str
    code: str
    domain: str
    age_min: int
    age_max: int
    start_date: str
    end_date: str
    promoter: str
    spots: int
    price: str
    days: str
    times: str
    location: str
    status: ActivityStatus
    page_url: str = ""
    registration_dates: RegistrationDates | None = None


class ActivityScraper:
    def __init__(
        self,
        domain: str = "",
        available_only: bool = False,
        headless: bool = True,
        timeout: int = 60,
        registration_url: str = "https://loisir.longueuil.quebec/inscription/Pages/Anonyme/Resultat/Page.fr.aspx?m=1",
        selectors: BrowseSelectors = DEFAULT_BROWSE_SELECTORS,
    ):
        self.domain = domain
        self.available_only = available_only
        self.headless = headless
        self.timeout = timeout
        self.registration_url = registration_url
        self.selectors = selectors
        self.activities: list[Activity] = []

    async def run(self) -> list[Activity]:
        logger.info("Starting activity scraper...")
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=self.headless)
            context = await browser.new_context()
            page = await context.new_page()

            try:
                await navigate_to_search(
                    page,
                    registration_url=self.registration_url,
                    domain=self.domain,
                    available_only=self.available_only,
                )
                await self._scrape_all_pages(page)
                return self.activities
            except DomainNotFoundError:
                raise
            except Exception as e:
                logger.error(f"Scraping failed: {e}")
                return self.activities
            finally:
                await browser.close()

    async def _scrape_all_pages(self, page: Page) -> None:
        await self._scrape_current_page(page)

        async def scrape_page(p: Page) -> None:
            await self._scrape_current_page(p)
            return None

        await iterate_pagination(
            page,
            scrape_page,
            pagination_selector=self.selectors.pagination_links,
        )

    async def _scrape_current_page(self, page: Page) -> None:
        rows = await page.locator("table tr").all()
        count = len(rows)
        logger.info(f"Found {count} rows on current page")

        for row in rows:
            activity = await self._parse_row(row, page)
            if activity and activity.name:
                self.activities.append(activity)

    async def _parse_row(self, row: Locator, page: Page) -> Activity | None:
        try:
            cells = row.locator("td")
            cell_count = await cells.count()

            if cell_count < 14:
                return None

            status = ActivityStatus.AVAILABLE

            status_cell = cells.nth(0)
            status_img = status_cell.locator("img[id*='Grille'], img[src*='Inscr']").first
            if await status_img.count() > 0:
                src = await status_img.get_attribute("src") or ""
                alt = await status_img.get_attribute("alt") or ""
                status = get_status_from_image_src(src, alt)

            name_cell = await cells.nth(2).inner_text()
            name_lines = name_cell.strip().split("\n")
            name = name_lines[0].strip() if name_lines else ""
            code = name_lines[1].strip() if len(name_lines) > 1 else ""

            if not name or len(name) < 3:
                return None

            domain = (await cells.nth(3).inner_text()).strip()

            age_min_str = (await cells.nth(4).inner_text()).strip()
            age_max_str = (await cells.nth(5).inner_text()).strip()

            try:
                age_min = int(age_min_str) if age_min_str else 0
            except ValueError:
                age_min = 0
            try:
                age_max = int(age_max_str) if age_max_str else 150
            except ValueError:
                age_max = 150

            start_date = (await cells.nth(6).inner_text()).strip()
            end_date = (await cells.nth(7).inner_text()).strip()
            promoter = (await cells.nth(8).inner_text()).strip()

            spots_str = (await cells.nth(9).inner_text()).strip()
            try:
                spots = int(spots_str) if spots_str else 0
            except ValueError:
                spots = 0

            price = (await cells.nth(10).inner_text()).strip()
            days = (await cells.nth(11).inner_text()).strip()
            times = (await cells.nth(12).inner_text()).strip()
            location = (await cells.nth(13).inner_text()).strip()

            registration_dates = await self._get_registration_dates(cells.nth(1), page)

            return Activity(
                name=name,
                code=code,
                domain=domain,
                age_min=age_min,
                age_max=age_max,
                start_date=start_date,
                end_date=end_date,
                promoter=promoter,
                spots=spots,
                price=price,
                days=days,
                times=times,
                location=location,
                status=status,
                page_url=page.url,
                registration_dates=registration_dates,
            )

        except Exception as e:
            logger.debug(f"Error parsing row: {e}")
            return None

    async def _get_registration_dates(
        self, info_cell: Locator, page: Page
    ) -> RegistrationDates | None:
        try:
            info_btn = info_cell.locator("input[type='image'][title*=\"dates d'inscription\"]")
            if await info_btn.count() == 0:
                return None

            await info_btn.click()
            await page.wait_for_selector("table.DatesInscriptions", state="visible", timeout=3000)

            dates_table = page.locator("table.DatesInscriptions")
            if await dates_table.count() == 0:
                return None

            dates = RegistrationDates()
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
                    dates.resident_start = (await date_cells.nth(0).inner_text()).strip()
                    dates.resident_end = (await date_cells.nth(1).inner_text()).strip()
                    break

            close_btn = page.locator("a[id*='ctlFermer']")
            if await close_btn.count() > 0:
                await close_btn.first.click()
                await page.wait_for_load_state("networkidle")

            return dates if dates.resident_start else None

        except Exception as e:
            logger.debug(f"Error getting registration dates: {e}")
            return None

    def filter_activities(
        self,
        name_contains: str = "",
        location_contains: str = "",
        day: str = "",
        age: int = 0,
    ) -> list[Activity]:
        filtered = self.activities

        if name_contains:
            filtered = [a for a in filtered if name_contains.lower() in a.name.lower()]

        if location_contains:
            filtered = [a for a in filtered if location_contains.lower() in a.location.lower()]

        if day:
            day_map = {
                "mon": ["lun", "monday", "lundi"],
                "tue": ["mar", "tuesday", "mardi"],
                "wed": ["mer", "wednesday", "mercredi"],
                "thu": ["jeu", "thursday", "jeudi"],
                "fri": ["ven", "friday", "vendredi"],
                "sat": ["sam", "saturday", "samedi"],
                "sun": ["dim", "sunday", "dimanche"],
            }
            day_lower = day.lower()[:3]
            day_variants = day_map.get(day_lower, [day_lower])

            def matches_day(activity: Activity) -> bool:
                days_lower = activity.days.lower()
                return any(v in days_lower for v in day_variants)

            filtered = [a for a in filtered if matches_day(a)]

        if age > 0:
            filtered = [a for a in filtered if a.age_min <= age <= a.age_max]

        return filtered
