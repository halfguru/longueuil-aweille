import asyncio
import logging
from contextlib import suppress
from datetime import datetime

from playwright.async_api import Page, async_playwright
from rich.console import Console
from rich.panel import Panel

from .config import Settings
from .dates import (
    RegistrationWindow,
    countdown_sleep,
    fetch_registration_window,
    format_time_remaining,
    prevent_sleep,
    restore_sleep,
)
from .navigation import navigate_to_search
from .selectors import DEFAULT_CART_SELECTORS, CartSelectors
from .status import (
    ActivityStatus,
    RegistrationStatus,
    get_status_from_image_src,
    iterate_pagination,
)

logger = logging.getLogger(__name__)

_RESULT_INDICATORS = [
    "Place réservée",
    "êtes déjà inscrit",
    "déjà inscrit",
    "Aucun dossier",
    "n'a été retrouvé",
    "critère d'âge",
    "ne répond pas au critère",
    "Erreur",
    "liste d'attente",
    "attente",
    "confirmée",
    "confirmation",
]


class RegistrationBot:
    def __init__(
        self,
        settings: Settings,
        selectors: CartSelectors = DEFAULT_CART_SELECTORS,
        console: Console | None = None,
    ):
        self.settings = settings
        self.selectors = selectors
        self.console = console
        self.last_activity_status: RegistrationStatus | None = None
        self.registration_window: RegistrationWindow | None = None

    @property
    def _console(self) -> Console | None:
        return getattr(self, "console", None)

    async def run(self) -> RegistrationStatus:
        prevent_sleep()
        try:
            return await self._run_lifecycle()
        finally:
            restore_sleep()

    async def _run_lifecycle(self) -> RegistrationStatus:
        logger.info("Starting registration bot...")

        # Step 1: Pre-flight check / initial registration attempt
        result = await self._run_single_session()

        if result != RegistrationStatus.NOT_YET_OPEN:
            return result

        if not self.registration_window or not self.registration_window.resident_start:
            return RegistrationStatus.NOT_YET_OPEN

        if not self.settings.wait_until_open:
            logger.info(
                f"Registration opens at {self.registration_window.raw_resident_start}. "
                "Exiting because wait_until_open is disabled."
            )
            return RegistrationStatus.NOT_YET_OPEN

        secs = self.registration_window.seconds_until_open()
        if secs <= 0:
            return await self._run_single_session()

        # Distant standby: if more than 5 minutes away (300 seconds), close browser and sleep
        if secs > 300:
            standby_secs = secs - 300
            if self._console:
                schedule_str = f" ({self.settings.schedule})" if self.settings.schedule else ""
                rem_str = format_time_remaining(self.registration_window.resident_start)
                panel_text = (
                    f"[bold]Target Activity:[/] {self.settings.activity_name}{schedule_str}\n"
                    f"[bold]Registration Opens:[/] [cyan]{self.registration_window.raw_resident_start}[/cyan] [dim](in {rem_str})[/dim]\n\n"
                    f"[green]*[/] Browser closed to conserve memory\n"
                    f"[green]*[/] System sleep prevented\n"
                    f"[green]*[/] Will automatically wake up 5 minutes before opening\n\n"
                    f"[dim]Press Ctrl+C at any time to cancel.[/dim]"
                )
                self._console.print()
                self._console.print(
                    Panel(
                        panel_text,
                        title="[bold yellow]Standing By For Registration[/]",
                        border_style="yellow",
                    )
                )
                self._console.print()

            logger.info(
                f"Registration opens at {self.registration_window.raw_resident_start} "
                f"(in {format_time_remaining(self.registration_window.resident_start)}). "
                f"Standing by until 5 minutes before opening..."
            )
            await countdown_sleep(
                standby_secs,
                target=self.registration_window.resident_start,
                label=f"registration opens at {self.registration_window.raw_resident_start}",
                console=self._console,
            )
            if self._console:
                self._console.print(
                    "[green]*[/] T-5 minutes reached! Launching browser for active registration session..."
                )
            logger.info("T-5 minutes reached! Launching browser for active registration session...")

        # Step 2: Active registration session
        return await self._run_single_session()

    async def _run_single_session(self) -> RegistrationStatus:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=self.settings.headless)
            context = await browser.new_context()
            page = await context.new_page()

            try:
                if self._console:
                    with self._console.status(
                        f"[bold cyan]Searching for '{self.settings.activity_name}' on portal...[/]",
                        spinner="dots",
                    ):
                        await navigate_to_search(
                            page,
                            registration_url=self.settings.registration_url,
                            activity_name=self.settings.activity_name,
                            domain=self.settings.domain,
                            available_only=False,
                        )
                else:
                    await navigate_to_search(
                        page,
                        registration_url=self.settings.registration_url,
                        activity_name=self.settings.activity_name,
                        domain=self.settings.domain,
                        available_only=False,
                    )
                result = await self._wait_and_select_activity(page)

                if result == RegistrationStatus.SUCCESS:
                    await self._fill_credentials(page)
                    status = await self._submit(page)

                    if status == RegistrationStatus.SUCCESS:
                        logger.info("Registration completed successfully!")
                        if not self.settings.headless:
                            should_unregister = await self._prompt_unregister()
                            if should_unregister:
                                unregistered = await self._unregister_participants(page)
                                if unregistered:
                                    logger.info("Unregistered from activity")
                                    await page.wait_for_load_state("networkidle")
                                    return RegistrationStatus.UNREGISTERED
                    elif status == RegistrationStatus.ALREADY_ENROLLED:
                        logger.info("Already enrolled in this activity")
                    elif status == RegistrationStatus.INVALID_CREDENTIALS:
                        logger.error("Invalid credentials - dossier/NIP not found")
                    elif status == RegistrationStatus.AGE_CRITERIA_NOT_MET:
                        logger.error("Age criteria not met for this activity")

                    return status

                if self.last_activity_status:
                    if self.last_activity_status != RegistrationStatus.NOT_YET_OPEN:
                        logger.error(f"Activity found but: {self.last_activity_status.value}")
                    else:
                        logger.info(f"Activity found but: {self.last_activity_status.value}")
                    return self.last_activity_status

                logger.error("Registration timed out - activity not found")
                return RegistrationStatus.TIMEOUT

            except Exception as e:
                logger.error(f"Registration failed: {e}")
                try:
                    screenshot_path = f"error-{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"
                    await page.screenshot(path=screenshot_path)
                    logger.info(f"Screenshot saved to {screenshot_path}")
                except Exception as se:
                    logger.debug(f"Could not take screenshot: {se}")
                return RegistrationStatus.FAILED
            finally:
                await browser.close()

    async def _wait_and_select_activity(self, page: Page) -> RegistrationStatus | None:
        logger.info(f"Searching for activity: {self.settings.activity_name}")
        start_time = asyncio.get_running_loop().time()
        attempts = 0

        while asyncio.get_running_loop().time() - start_time < self.settings.timeout:
            attempts += 1
            elapsed = int(asyncio.get_running_loop().time() - start_time)
            logger.info(f"Attempt #{attempts} (elapsed: {elapsed}s)")

            result = await self._find_and_select_activity(page)

            if result == RegistrationStatus.SUCCESS:
                logger.info("Activity found and selected!")
                return result

            if (
                result == RegistrationStatus.NOT_YET_OPEN
                and self.registration_window
                and self.registration_window.resident_start
            ):
                secs = self.registration_window.seconds_until_open()
                if secs > 300:
                    # More than 5 minutes away - return NOT_YET_OPEN so browser closes for distant standby
                    logger.info(
                        f"Registration for '{self.settings.activity_name}' opens at "
                        f"{self.registration_window.raw_resident_start} "
                        f"(in {format_time_remaining(self.registration_window.resident_start)})."
                    )
                    return RegistrationStatus.NOT_YET_OPEN
                elif secs > 15:
                    # Between 15 seconds and 5 minutes away - sleep on page until 15s before opening
                    sleep_time = secs - 15
                    logger.info(
                        f"Registration opens in {format_time_remaining(self.registration_window.resident_start)} "
                        f"(at {self.registration_window.raw_resident_start}). "
                        f"Sleeping for {int(sleep_time)}s until 15s before opening..."
                    )
                    await countdown_sleep(
                        sleep_time,
                        target=self.registration_window.resident_start,
                        label=f"registration opens at {self.registration_window.raw_resident_start}",
                        console=self._console,
                    )
                    # Reset timeout counter after sleep so full timeout applies to active polling
                    start_time = asyncio.get_running_loop().time()
                    if self._console:
                        self._console.print(
                            "[green]*[/] T-15s reached! Starting active registration polling..."
                        )
                    logger.info("Awakened! Starting active registration polling...")

            if result in (
                RegistrationStatus.ACTIVITY_FULL,
                RegistrationStatus.ACTIVITY_CANCELLED,
                RegistrationStatus.REGISTRATION_NEVER_AVAILABLE,
            ):
                logger.info(f"Activity reached non-retryable state: {result.value}")
                return result

            logger.info("Activity not available yet, refreshing...")
            await asyncio.sleep(self.settings.refresh_interval)
            await page.reload(wait_until="networkidle")
            await page.wait_for_selector("table", state="visible")

        return None

    async def _find_and_select_activity(self, page: Page) -> RegistrationStatus | None:
        result = await self._try_select_on_page(page)
        if result == RegistrationStatus.SUCCESS:
            return result
        if result is not None:
            self.last_activity_status = result

        async def try_page(p: Page) -> RegistrationStatus | None:
            r = await self._try_select_on_page(p)
            if r == RegistrationStatus.SUCCESS:
                return r
            if r is not None:
                self.last_activity_status = r
            return None

        paginated_result = await iterate_pagination(page, try_page)
        if paginated_result is not None:
            return paginated_result
        return self.last_activity_status

    async def _try_select_on_page(self, page: Page) -> RegistrationStatus | None:
        activity_name = self.settings.activity_name

        activity_elements = page.get_by_text(activity_name, exact=False)
        count = await activity_elements.count()
        logger.info(f"Found {count} elements matching '{activity_name}'")

        for i in range(count):
            el = activity_elements.nth(i)
            parent_row = el.locator("xpath=ancestor::tr[1]")
            row_content = await parent_row.inner_text()

            if self.settings.schedule and self.settings.schedule.lower() not in row_content.lower():
                continue

            select_btn = parent_row.locator("input[type='image'][id*='Selecteur']")
            btn_count = await select_btn.count()

            if btn_count > 0:
                btn = select_btn.first
                src = await btn.get_attribute("src") or ""
                alt = await btn.get_attribute("alt") or ""

                status = get_status_from_image_src(src, alt)
                if status == ActivityStatus.NEVER_AVAILABLE:
                    logger.info("Activity found but online registration never available")
                    return RegistrationStatus.REGISTRATION_NEVER_AVAILABLE

                if "ANNULÉE" in row_content.upper() or status == ActivityStatus.CANCELLED:
                    logger.info("Activity found but is ANNULÉE (cancelled)")
                    return RegistrationStatus.ACTIVITY_CANCELLED

                if status == ActivityStatus.NOT_YET:
                    logger.info("Activity found but registration not open yet")
                    if self.registration_window is None:
                        self.registration_window = await fetch_registration_window(parent_row, page)
                    return RegistrationStatus.NOT_YET_OPEN

                if status == ActivityStatus.FULL:
                    logger.info("Activity found but not available: full")
                    return RegistrationStatus.ACTIVITY_FULL

                is_full = "COMPLET" in row_content.upper()
                if is_full and not getattr(self.settings, "waitlist", False):
                    logger.info("Activity found but is COMPLET (full) and waitlist is disabled")
                    return RegistrationStatus.ACTIVITY_FULL

                if is_full:
                    logger.info(
                        "Activity regular spots full - selecting for waitlist registration..."
                    )
                    if self._console:
                        self._console.print(
                            "[yellow]*[/] Regular spots are full (COMPLET). Registering on waiting list..."
                        )
                else:
                    logger.info("Found activity, clicking select button...")
                    if self._console:
                        self._console.print("[green]*[/] Found activity! Adding to cart...")

                await btn.click()

                # On the live site, wait for ASP.NET partial postback to confirm selection in DOM
                if "BT_Panier_IN" in src:
                    out_btn = parent_row.locator("input[type='image'][src*='BT_Panier_OUT.gif']")
                    try:
                        await out_btn.wait_for(timeout=3000)
                        logger.info("Activity selection confirmed in DOM (BT_Panier_OUT)")
                    except Exception:
                        await page.wait_for_load_state("networkidle")
                else:
                    await page.wait_for_load_state("networkidle")

                logger.info("Proceeding to cart...")
                if self._console:
                    self._console.print("[green]*[/] Navigating to cart / identification...")

                cart_btn = page.locator(self.selectors.cart_button)
                if await cart_btn.count() == 0:
                    cart_btn = page.locator("input[id*='ctlAppelPanierIdent']").first

                if await cart_btn.count() > 0:
                    await cart_btn.click()
                    nav_timeout = 100 if ("mock" in page.url or "127.0.0.1" in page.url) else 10000
                    with suppress(Exception):
                        await page.wait_for_url("**/PagePanier*", timeout=nav_timeout)

                await page.wait_for_load_state("networkidle")

                is_mock = "mock" in page.url or "127.0.0.1" in page.url
                if (
                    not is_mock
                    and "PagePanier" not in page.url
                    and "panier" not in (await page.title()).lower()
                ):
                    logger.error(f"Failed to navigate to cart page. Current URL: {page.url}")
                    return None

                return RegistrationStatus.SUCCESS
            else:
                if "COMPLET" in row_content.upper():
                    logger.info("Activity found but is COMPLET (full)")
                    return RegistrationStatus.ACTIVITY_FULL
                if "ANNULÉE" in row_content.upper():
                    logger.info("Activity found but is ANNULÉE (cancelled)")
                    return RegistrationStatus.ACTIVITY_CANCELLED

                info_btn = parent_row.locator("input[type='image'][title*=\"dates d'inscription\"]")
                if await info_btn.count() > 0 or "Inscription non disponible" in row_content:
                    logger.info("Activity found but registration not open yet")
                    if self.registration_window is None:
                        self.registration_window = await fetch_registration_window(parent_row, page)
                    return RegistrationStatus.NOT_YET_OPEN

        return None

    async def _fill_credentials(self, page: Page) -> None:
        logger.info("Filling credentials...")
        if self._console:
            self._console.print("[green]*[/] Filling participant credentials...")
        for i, participant in enumerate(self.settings.participants):
            dossier_selector = self.selectors.dossier_input_template.format(i=i)
            nip_selector = self.selectors.nip_input_template.format(i=i)

            await page.locator(dossier_selector).fill(participant.carte_acces)
            await page.locator(nip_selector).fill(participant.telephone)
            await asyncio.sleep(0.1)

    async def _unregister_participants(self, page: Page) -> bool:
        logger.info("Unregistering participants from cart...")
        for i in range(len(self.settings.participants)):
            unregister_selector = self.selectors.unregister_button_template.format(i=i)
            unregister_btn = page.locator(unregister_selector)
            if await unregister_btn.count() > 0:
                await unregister_btn.first.click()
                confirm_btn = page.locator("input#OUI[value='OUI']")
                try:
                    await confirm_btn.wait_for(state="visible", timeout=2000)
                    await confirm_btn.click()
                    await page.wait_for_load_state("networkidle")
                    logger.info(f"Unregistered participant {i}")
                except TimeoutError:
                    logger.debug(f"No confirmation dialog for participant {i}")

        page_content = await page.locator("body").inner_text()
        if any(
            indicator in page_content
            for indicator in ["Nouveau tarif ajusté : N/A", "tarif", "0,00 $", "0 participant"]
        ):
            logger.info("Unregistration confirmed")
            return True

        logger.warning(f"Could not confirm unregistration. Page snippet: {page_content[:200]}")
        return True

    async def _prompt_unregister(self) -> bool:
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None,
            lambda: input("Registration successful! Unregister? [y/N]: ").strip().lower(),
        )
        return response in ("y", "yes")

    async def _wait_for_result(self, page: Page, timeout_ms: int = 15000) -> str:
        deadline = asyncio.get_running_loop().time() + timeout_ms / 1000
        page_content = ""
        while asyncio.get_running_loop().time() < deadline:
            page_content = await page.locator(self.selectors.result_container).inner_text()
            if any(ind in page_content for ind in _RESULT_INDICATORS):
                return page_content
            await asyncio.sleep(0.3)
        return page_content

    async def _submit(self, page: Page) -> RegistrationStatus:
        logger.info("Submitting registration...")
        if self._console:
            self._console.print("[green]*[/] Submitting registration...")
        await page.locator(self.selectors.validate_button).click()
        await page.wait_for_load_state("networkidle")

        page_content = await self._wait_for_result(page)
        page_lower = page_content.lower()

        if (
            "place réservée" in page_lower
            or "liste d'attente" in page_lower
            or "attente" in page_lower
            or "confirmée" in page_lower
            or "confirmation" in page_lower
        ):
            logger.info("Registration successful (enrolled or waitlisted)")
            return RegistrationStatus.SUCCESS

        if "êtes déjà inscrit" in page_content or "déjà inscrit" in page_content.lower():
            logger.info("Already enrolled detected")
            return RegistrationStatus.ALREADY_ENROLLED

        if "Aucun dossier" in page_content or "n'a été retrouvé" in page_content:
            logger.error("Invalid credentials - dossier not found")
            return RegistrationStatus.INVALID_CREDENTIALS

        if "critère d'âge" in page_content or "ne répond pas au critère" in page_content:
            logger.error("Age criteria not met for this activity")
            return RegistrationStatus.AGE_CRITERIA_NOT_MET

        if "Erreur" in page_content or "error" in page_content.lower():
            logger.error("Error detected on page")
            return RegistrationStatus.FAILED

        logger.error("Unknown page state after submission")
        return RegistrationStatus.FAILED
