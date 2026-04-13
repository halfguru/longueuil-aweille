import asyncio
import logging
from typing import Literal

from playwright.async_api import Page

from .selectors import SearchSelectors

logger = logging.getLogger(__name__)


async def retry_goto(
    page: Page,
    url: str,
    *,
    max_retries: int = 3,
    wait_until: Literal["commit", "domcontentloaded", "load", "networkidle"] = "networkidle",
) -> None:
    for attempt in range(max_retries):
        try:
            await page.goto(url, wait_until=wait_until)
            return
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            backoff = 2**attempt
            logger.warning(
                f"page.goto() failed (attempt {attempt + 1}/{max_retries}): {e}. "
                f"Retrying in {backoff}s..."
            )
            await asyncio.sleep(backoff)


async def navigate_to_search(
    page: Page,
    registration_url: str,
    activity_name: str = "",
    domain: str = "",
    available_only: bool = True,
    selectors: SearchSelectors | None = None,
) -> None:
    if selectors is None:
        from .selectors import DEFAULT_SEARCH_SELECTORS

        selectors = DEFAULT_SEARCH_SELECTORS

    logger.info("Opening registration website...")
    await retry_goto(page, registration_url, wait_until="domcontentloaded")

    cookie_btn = page.locator("#c-p-bn")
    try:
        await cookie_btn.click(timeout=5000)
        logger.info("Dismissed cookie consent dialog")
        await page.wait_for_load_state("domcontentloaded")
    except Exception:
        logger.debug("No cookie dialog found, continuing...")

    if activity_name:
        logger.info(f"Filling search keyword: {activity_name}")
        await page.wait_for_selector(selectors.keyword_search, state="visible")
        await page.locator(selectors.keyword_search).fill(activity_name)
        await page.locator(selectors.search_option_or).click()

    logger.info("Opening Disponibilités tab...")
    await page.get_by_role("link", name="Disponibilités").click()
    await page.wait_for_selector(selectors.available_only_radio, state="visible")

    if available_only:
        logger.info("Selecting 'available only' filter...")
        await page.locator(selectors.available_only_radio).click()
    else:
        await page.locator(selectors.search_all_radio).click()

    if domain:
        logger.info("Opening Domaines tab...")
        await page.get_by_role("link", name="Domaines").click()
        await page.wait_for_selector("input[type='checkbox']", state="visible")

        logger.info(f"Selecting domain: {domain}")
        checkbox = page.locator(
            f"//*[contains(text(), '{domain}')]/preceding::input[@type='checkbox'][1]"
        )
        await checkbox.first.click()

    logger.info("Clicking search button...")
    await page.locator(selectors.search_button).click()
    await page.wait_for_load_state("domcontentloaded")
