import re

import pytest
from playwright.async_api import Error as PlaywrightError
from playwright.async_api import async_playwright

from longueuil_aweille.selectors import DEFAULT_CART_SELECTORS, DEFAULT_VERIFY_SELECTORS

SUCCESS_HTML = "<html><body><p>Place r&eacute;serv&eacute;e</p></body></html>"

ALREADY_ENROLLED_HTML = (
    "<html><body><p>Vous &ecirc;tes d&eacute;j&agrave; inscrit</p></body></html>"
)

VERIFY_VALID_HTML = """<html><body>
<input name="numero" type="text">
<input name="telephone" type="text">
<input name="action" type="submit">
<p>Voici les informations de votre dossier</p>
</body></html>"""

VERIFY_INVALID_HTML = """<html><body>
<input name="numero" type="text">
<input name="telephone" type="text">
<input name="action" type="submit">
<p>Le num&eacute;ro n'est pas valide</p>
</body></html>"""

VERIFY_ERROR_HTML = """<html><body>
<input name="numero" type="text">
<input name="telephone" type="text">
<input name="action" type="submit">
<p>Some unknown response</p>
</body></html>"""


async def test_verify_bot_invalid():
    from longueuil_aweille.verify import VerificationBot, VerificationStatus

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.route(
            re.compile(r".*"),
            lambda route: route.fulfill(
                body=VERIFY_INVALID_HTML, content_type="text/html; charset=utf-8"
            ),
        )
        await page.goto("http://mock-test.local/verify")

        bot = VerificationBot(
            carte_acces="01234567890123",
            telephone="5145551234",
            headless=True,
        )
        result = await bot._check_result(page)
        assert result == VerificationStatus.INVALID
        await browser.close()


async def test_verify_bot_valid():
    from longueuil_aweille.verify import VerificationBot, VerificationStatus

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.route(
            re.compile(r".*"),
            lambda route: route.fulfill(
                body=VERIFY_VALID_HTML, content_type="text/html; charset=utf-8"
            ),
        )
        await page.goto("http://mock-test.local/verify")

        bot = VerificationBot(
            carte_acces="01234567890123",
            telephone="5145551234",
            headless=True,
        )
        result = await bot._check_result(page)
        assert result == VerificationStatus.VALID
        await browser.close()


async def test_verify_bot_error_unknown():
    from longueuil_aweille.verify import VerificationBot, VerificationStatus

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.route(
            re.compile(r".*"),
            lambda route: route.fulfill(
                body=VERIFY_ERROR_HTML, content_type="text/html; charset=utf-8"
            ),
        )
        await page.goto("http://mock-test.local/verify")

        bot = VerificationBot(
            carte_acces="01234567890123",
            telephone="5145551234",
            headless=True,
        )
        result = await bot._check_result(page)
        assert result == VerificationStatus.ERROR
        await browser.close()


async def test_verify_fill_form():
    from longueuil_aweille.verify import VerificationBot

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.route(
            re.compile(r".*"),
            lambda route: route.fulfill(
                body=VERIFY_VALID_HTML, content_type="text/html; charset=utf-8"
            ),
        )
        await page.goto("http://mock-test.local/verify")

        bot = VerificationBot(
            carte_acces="01234567890123",
            telephone="5145551234",
            headless=True,
            selectors=DEFAULT_VERIFY_SELECTORS,
        )
        await bot._fill_form(page)

        carte_val = await page.locator("input[name='numero']").input_value()
        tel_val = await page.locator("input[name='telephone']").input_value()
        assert carte_val == "01234567890123"
        assert tel_val == "5145551234"
        await browser.close()


async def test_submit_detects_success():
    from longueuil_aweille.registration import RegistrationBot

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.route(
            re.compile(r".*"),
            lambda route: route.fulfill(body=SUCCESS_HTML, content_type="text/html; charset=utf-8"),
        )
        await page.goto("http://mock-test.local/success")

        bot = RegistrationBot.__new__(RegistrationBot)
        bot.selectors = DEFAULT_CART_SELECTORS

        result = await bot._wait_for_result(page, timeout_ms=2000)
        assert "Place" in result and "serv" in result
        await browser.close()


async def test_submit_detects_already_enrolled():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.route(
            re.compile(r".*"),
            lambda route: route.fulfill(
                body=ALREADY_ENROLLED_HTML, content_type="text/html; charset=utf-8"
            ),
        )
        await page.goto("http://mock-test.local/enrolled")

        from longueuil_aweille.registration import RegistrationBot

        bot = RegistrationBot.__new__(RegistrationBot)
        bot.selectors = DEFAULT_CART_SELECTORS

        result = await bot._wait_for_result(page, timeout_ms=2000)
        assert "inscrit" in result
        await browser.close()


async def test_submit_returns_failed_on_unknown():
    unknown_html = """<html><body>
<button id="ctlMenuActionBas_ctlAppelPanierConfirm">Validate</button>
<p>Something unexpected</p>
</body></html>"""

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.route(
            re.compile(r".*"),
            lambda route: route.fulfill(body=unknown_html, content_type="text/html; charset=utf-8"),
        )
        await page.goto("http://mock-test.local/unknown")

        from longueuil_aweille.registration import RegistrationBot, RegistrationStatus

        bot = RegistrationBot.__new__(RegistrationBot)
        bot.selectors = DEFAULT_CART_SELECTORS

        status = await bot._submit(page)
        assert status == RegistrationStatus.FAILED
        await browser.close()


async def test_browse_scrapes_activities():
    from longueuil_aweille.browse import ActivityScraper
    from longueuil_aweille.status import ActivityStatus

    table_html = """<html><body>
<table>
<tr>
<td><img id="GrilleSelecteur" src="InscrDispo.png" alt="Disponible"></td>
<td>info</td>
<td>Swim Kids</td>
<td>Aquatics</td><td>5</td><td>12</td><td>Jan</td><td>Mar</td>
<td>City</td><td>10</td><td>50$</td><td>Lundi</td><td>18:00</td><td>Pool</td>
<td>Extra</td>
</tr>
</table>
</body></html>"""

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.route(
            re.compile(r".*"),
            lambda route: route.fulfill(body=table_html, content_type="text/html; charset=utf-8"),
        )

        scraper = ActivityScraper(headless=True)
        await page.goto("http://mock-test.local/browse")
        await scraper._scrape_current_page(page)

        assert len(scraper.activities) == 1
        assert scraper.activities[0].name == "Swim Kids"
        assert scraper.activities[0].status == ActivityStatus.AVAILABLE
        await browser.close()


async def test_browse_scrapes_full_activity():
    from longueuil_aweille.browse import ActivityScraper
    from longueuil_aweille.status import ActivityStatus

    table_html = """<html><body>
<table>
<tr>
<td><img id="GrilleSelecteur" src="Complet.png" alt="Complet"></td>
<td>info</td>
<td>Yoga</td>
<td>Fitness</td><td>18</td><td>65</td><td>Feb</td><td>Apr</td>
<td>Studio</td><td>0</td><td>30$</td><td>Mercredi</td><td>19:00</td><td>Gym</td>
<td>Extra</td>
</tr>
</table>
</body></html>"""

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.route(
            re.compile(r".*"),
            lambda route: route.fulfill(body=table_html, content_type="text/html; charset=utf-8"),
        )

        scraper = ActivityScraper(headless=True)
        await page.goto("http://mock-test.local/browse")
        await scraper._scrape_current_page(page)

        assert len(scraper.activities) == 1
        assert scraper.activities[0].status == ActivityStatus.FULL
        assert scraper.activities[0].spots == 0
        await browser.close()


async def test_browse_skips_short_rows():
    table_html = """<html><body>
<table>
<tr><td>header1</td><td>header2</td></tr>
</table>
</body></html>"""

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.route(
            re.compile(r".*"),
            lambda route: route.fulfill(body=table_html, content_type="text/html; charset=utf-8"),
        )

        from longueuil_aweille.browse import ActivityScraper

        scraper = ActivityScraper(headless=True)
        await page.goto("http://mock-test.local/browse")
        await scraper._scrape_current_page(page)

        assert len(scraper.activities) == 0
        await browser.close()


async def test_retry_goto_succeeds_first_try():
    from longueuil_aweille.navigation import retry_goto

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        call_count = 0

        async def handle(route):
            nonlocal call_count
            call_count += 1
            await route.fulfill(body="<html><body>ok</body></html>", content_type="text/html")

        await page.route(re.compile(r".*"), handle)
        await retry_goto(page, "http://mock-test.local/page")
        assert call_count == 1
        await browser.close()


async def test_retry_goto_retries_on_failure():
    from longueuil_aweille.navigation import retry_goto

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        call_count = 0

        async def handle(route):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                await route.abort()
            else:
                await route.fulfill(body="<html><body>ok</body></html>", content_type="text/html")

        await page.route(re.compile(r".*"), handle)
        await retry_goto(page, "http://mock-test.local/page", max_retries=3)
        assert call_count == 3
        await browser.close()


async def test_retry_goto_raises_after_max_retries():
    from longueuil_aweille.navigation import retry_goto

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.route(re.compile(r".*"), lambda route: route.abort())

        with pytest.raises(PlaywrightError):
            await retry_goto(page, "http://mock-test.local/page", max_retries=2)
        await browser.close()


async def test_registration_fill_credentials():
    from longueuil_aweille.config import Participant, Settings
    from longueuil_aweille.registration import RegistrationBot

    cart_html = """<html><body>
<input id="ctlPanierActivites_ctlActivites_ctl00_ctlRow_ctlListeIdentification_ctlListe_itm0_ctlBloc_ctlDossier" type="text">
<input id="ctlPanierActivites_ctlActivites_ctl00_ctlRow_ctlListeIdentification_ctlListe_itm0_ctlBloc_ctlNip" type="text">
</body></html>"""

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.route(
            re.compile(r".*"),
            lambda route: route.fulfill(body=cart_html, content_type="text/html; charset=utf-8"),
        )
        await page.goto("http://mock-test.local/cart")

        settings = Settings(
            activity_name="Test",
            participants=[
                Participant(
                    name="Test", age=10, carte_acces="01234567890123", telephone="5145551234"
                )
            ],
        )
        bot = RegistrationBot(settings)
        await bot._fill_credentials(page)

        dossier_val = await page.locator(
            "#ctlPanierActivites_ctlActivites_ctl00_ctlRow_ctlListeIdentification_ctlListe_itm0_ctlBloc_ctlDossier"
        ).input_value()
        nip_val = await page.locator(
            "#ctlPanierActivites_ctlActivites_ctl00_ctlRow_ctlListeIdentification_ctlListe_itm0_ctlBloc_ctlNip"
        ).input_value()
        assert dossier_val == "01234567890123"
        assert nip_val == "5145551234"
        await browser.close()


async def test_try_select_on_page_no_activity():
    from longueuil_aweille.config import Settings
    from longueuil_aweille.registration import RegistrationBot

    no_match_html = """<html><body>
<table><tr><td>Some other activity</td></tr></table>
</body></html>"""

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.route(
            re.compile(r".*"),
            lambda route: route.fulfill(
                body=no_match_html, content_type="text/html; charset=utf-8"
            ),
        )
        await page.goto("http://mock-test.local/search")

        settings = Settings(activity_name="Nonexistent Activity")
        bot = RegistrationBot(settings)
        result = await bot._try_select_on_page(page)
        assert result is None
        await browser.close()


async def test_try_select_activity_full():
    from longueuil_aweille.config import Settings
    from longueuil_aweille.registration import RegistrationBot, RegistrationStatus

    full_html = """<html><body>
<table><tr>
<td><input type="image" id="SomeSelecteur" src="InscrDispo.png"></td>
<td>Test Activity</td><td>COMPLET</td>
</tr></table>
</body></html>"""

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.route(
            re.compile(r".*"),
            lambda route: route.fulfill(body=full_html, content_type="text/html; charset=utf-8"),
        )
        await page.goto("http://mock-test.local/search")

        settings = Settings(activity_name="Test Activity")
        bot = RegistrationBot(settings)
        result = await bot._try_select_on_page(page)
        assert result == RegistrationStatus.ACTIVITY_FULL
        await browser.close()


async def test_try_select_activity_cancelled():
    from longueuil_aweille.config import Settings
    from longueuil_aweille.registration import RegistrationBot, RegistrationStatus

    cancelled_html = """<html><body>
<table><tr>
<td><input type="image" id="SomeSelecteur" src="InscrDispo.png"></td>
<td>Test Activity</td><td>ANNUL&Eacute;E</td>
</tr></table>
</body></html>"""

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.route(
            re.compile(r".*"),
            lambda route: route.fulfill(
                body=cancelled_html, content_type="text/html; charset=utf-8"
            ),
        )
        await page.goto("http://mock-test.local/search")

        settings = Settings(activity_name="Test Activity")
        bot = RegistrationBot(settings)
        result = await bot._try_select_on_page(page)
        assert result == RegistrationStatus.ACTIVITY_CANCELLED
        await browser.close()


async def test_try_select_never_available():
    from longueuil_aweille.config import Settings
    from longueuil_aweille.registration import RegistrationBot, RegistrationStatus

    never_html = """<html><body>
<table><tr>
<td><input type="image" id="SomeSelecteur" src="JamaisDispo.png"></td>
<td>Test Activity</td>
</tr></table>
</body></html>"""

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.route(
            re.compile(r".*"),
            lambda route: route.fulfill(body=never_html, content_type="text/html; charset=utf-8"),
        )
        await page.goto("http://mock-test.local/search")

        settings = Settings(activity_name="Test Activity")
        bot = RegistrationBot(settings)
        result = await bot._try_select_on_page(page)
        assert result == RegistrationStatus.REGISTRATION_NEVER_AVAILABLE
        await browser.close()


async def test_try_select_not_yet():
    from longueuil_aweille.config import Settings
    from longueuil_aweille.registration import RegistrationBot, RegistrationStatus

    not_yet_html = """<html><body>
<table><tr>
<td><input type="image" id="SomeSelecteur" src="NotNow.png"></td>
<td>Test Activity</td>
</tr></table>
</body></html>"""

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.route(
            re.compile(r".*"),
            lambda route: route.fulfill(body=not_yet_html, content_type="text/html; charset=utf-8"),
        )
        await page.goto("http://mock-test.local/search")

        settings = Settings(activity_name="Test Activity")
        bot = RegistrationBot(settings)
        result = await bot._try_select_on_page(page)
        assert result == RegistrationStatus.FAILED
        await browser.close()


async def test_submit_invalid_credentials():
    invalid_html = """<html><body>
<button id="ctlMenuActionBas_ctlAppelPanierConfirm">Validate</button>
<p>Aucun dossier n'a &eacute;t&eacute; retrouv&eacute;</p>
</body></html>"""

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.route(
            re.compile(r".*"),
            lambda route: route.fulfill(body=invalid_html, content_type="text/html; charset=utf-8"),
        )
        await page.goto("http://mock-test.local/submit")

        from longueuil_aweille.registration import RegistrationBot, RegistrationStatus

        bot = RegistrationBot.__new__(RegistrationBot)
        bot.selectors = DEFAULT_CART_SELECTORS

        status = await bot._submit(page)
        assert status == RegistrationStatus.INVALID_CREDENTIALS
        await browser.close()


async def test_submit_age_criteria_not_met():
    age_html = """<html><body>
<button id="ctlMenuActionBas_ctlAppelPanierConfirm">Validate</button>
<p>ne r&eacute;pond pas au crit&egrave;re d'&acirc;ge</p>
</body></html>"""

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.route(
            re.compile(r".*"),
            lambda route: route.fulfill(body=age_html, content_type="text/html; charset=utf-8"),
        )
        await page.goto("http://mock-test.local/submit")

        from longueuil_aweille.registration import RegistrationBot, RegistrationStatus

        bot = RegistrationBot.__new__(RegistrationBot)
        bot.selectors = DEFAULT_CART_SELECTORS

        status = await bot._submit(page)
        assert status == RegistrationStatus.AGE_CRITERIA_NOT_MET
        await browser.close()


async def test_submit_error_on_page():
    error_html = """<html><body>
<button id="ctlMenuActionBas_ctlAppelPanierConfirm">Validate</button>
<p>Erreur du syst&egrave;me</p>
</body></html>"""

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.route(
            re.compile(r".*"),
            lambda route: route.fulfill(body=error_html, content_type="text/html; charset=utf-8"),
        )
        await page.goto("http://mock-test.local/submit")

        from longueuil_aweille.registration import RegistrationBot, RegistrationStatus

        bot = RegistrationBot.__new__(RegistrationBot)
        bot.selectors = DEFAULT_CART_SELECTORS

        status = await bot._submit(page)
        assert status == RegistrationStatus.FAILED
        await browser.close()


async def test_verify_run_valid():
    from longueuil_aweille.verify import VerificationBot, VerificationStatus

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.route(
            re.compile(r".*"),
            lambda route: route.fulfill(
                body=VERIFY_VALID_HTML, content_type="text/html; charset=utf-8"
            ),
        )

        bot = VerificationBot(
            carte_acces="01234567890123",
            telephone="5145551234",
            headless=True,
            selectors=DEFAULT_VERIFY_SELECTORS,
        )
        bot.verification_url = "http://mock-test.local/verify"

        async def mock_run():
            page_obj = await context.new_page()
            await page_obj.route(
                re.compile(r".*"),
                lambda route: route.fulfill(
                    body=VERIFY_VALID_HTML, content_type="text/html; charset=utf-8"
                ),
            )
            await page_obj.goto("http://mock-test.local/verify")
            await bot._fill_form(page_obj)
            await page_obj.locator(DEFAULT_VERIFY_SELECTORS.submit_button).first.click()
            result = await bot._check_result(page_obj)
            return result

        result = await mock_run()
        assert result == VerificationStatus.VALID
        await browser.close()
