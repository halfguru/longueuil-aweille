"""Tests for RegistrationBot."""

from longueuil_aweille.config import Participant, Settings
from longueuil_aweille.registration import RegistrationBot
from longueuil_aweille.selectors import DEFAULT_CART_SELECTORS, CartSelectors
from longueuil_aweille.status import RegistrationStatus


def test_bot_creation():
    """Test that RegistrationBot can be instantiated with Settings."""
    settings = Settings(
        domain="Test Domain",
        activity_name="Test Activity",
        participants=[
            Participant(name="Test", age=10, carte_acces="01234567890123", telephone="5145551234")
        ],
    )
    bot = RegistrationBot(settings)
    assert bot.settings == settings
    assert bot.selectors == DEFAULT_CART_SELECTORS
    assert bot.last_activity_status is None


def test_bot_with_custom_selectors():
    """Test that RegistrationBot accepts custom selectors."""

    custom_selectors = CartSelectors(
        cart_button="#custom-cart",
        dossier_input_template="#custom-dossier-{i:02d}",
        nip_input_template="#custom-nip-{i:02d}",
        unregister_button_template="#custom-unregister-{i:02d}",
        validate_button="#custom-validate",
    )

    settings = Settings(
        domain="Test Domain",
        activity_name="Test Activity",
        participants=[
            Participant(name="Test", age=10, carte_acces="01234567890123", telephone="5145551234")
        ],
    )

    bot = RegistrationBot(settings, selectors=custom_selectors)
    assert bot.selectors == custom_selectors


def test_registration_status_enum():
    """Test that all RegistrationStatus values are accessible."""
    assert RegistrationStatus.SUCCESS.value == "success"
    assert RegistrationStatus.ALREADY_ENROLLED.value == "already_enrolled"
    assert RegistrationStatus.INVALID_CREDENTIALS.value == "invalid_credentials"
    assert RegistrationStatus.AGE_CRITERIA_NOT_MET.value == "age_criteria_not_met"
    assert RegistrationStatus.ACTIVITY_FULL.value == "activity_full"
    assert RegistrationStatus.ACTIVITY_CANCELLED.value == "activity_cancelled"
    assert RegistrationStatus.REGISTRATION_NEVER_AVAILABLE.value == "registration_never_available"
    assert RegistrationStatus.FAILED.value == "failed"
    assert RegistrationStatus.TIMEOUT.value == "timeout"


def test_default_selectors():
    """Test that DEFAULT_CART_SELECTORS has all required fields."""
    assert DEFAULT_CART_SELECTORS.cart_button == "#ctlGrille_ctlMenuActionsBas_ctlAppelPanierIdent"
    assert DEFAULT_CART_SELECTORS.validate_button == "#ctlMenuActionBas_ctlAppelPanierConfirm"
    assert "{i:02d}" in DEFAULT_CART_SELECTORS.dossier_input_template
    assert "{i:02d}" in DEFAULT_CART_SELECTORS.nip_input_template


def test_selector_template_formatting():
    """Test that selector templates format correctly."""
    result = DEFAULT_CART_SELECTORS.dossier_input_template.format(i=0)
    assert "ctl00" in result

    result = DEFAULT_CART_SELECTORS.dossier_input_template.format(i=5)
    assert "ctl05" in result

    result = DEFAULT_CART_SELECTORS.dossier_input_template.format(i=10)
    assert "ctl10" in result
