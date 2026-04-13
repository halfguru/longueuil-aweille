import pytest
from pydantic import ValidationError

from longueuil_aweille.config import Participant, Settings


def test_participant_creation():
    participant = Participant(
        name="Test", carte_acces="01234567890123", telephone="5145551234", age=30
    )
    assert participant.name == "Test"
    assert participant.carte_acces == "01234567890123"
    assert participant.telephone == "5145551234"
    assert participant.age == 30


def test_participant_invalid_carte_acces():
    with pytest.raises(ValidationError, match="14 digits"):
        Participant(name="Test", carte_acces="123", telephone="5145551234", age=30)


def test_participant_invalid_telephone():
    with pytest.raises(ValidationError, match="10 digits"):
        Participant(name="Test", carte_acces="01234567890123", telephone="5551234", age=30)


def test_settings_defaults():
    settings = Settings(activity_name="Test Activity")
    assert settings.headless is False
    assert settings.timeout == 600
    assert settings.refresh_interval == 5.0
    assert settings.participants == []


def test_settings_invalid_timeout():
    with pytest.raises(ValidationError, match="greater than 0"):
        Settings(activity_name="Test", timeout=0)


def test_settings_invalid_refresh_interval():
    with pytest.raises(ValidationError, match="greater than 0"):
        Settings(activity_name="Test", refresh_interval=-1.0)


def test_settings_empty_activity_name():
    with pytest.raises(ValidationError, match="must not be empty"):
        Settings(activity_name="")


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("LONGUEUIL_HEADLESS", "true")
    monkeypatch.setenv("LONGUEUIL_TIMEOUT", "300")
    monkeypatch.setenv("LONGUEUIL_ACTIVITY_NAME", "Test Activity")

    settings = Settings()
    assert settings.headless is True
    assert settings.timeout == 300
    assert settings.activity_name == "Test Activity"


def test_settings_custom_values():
    settings = Settings(
        activity_name="Test Activity",
        headless=True,
        timeout=120,
        participants=[
            Participant(
                name="Participant 1",
                carte_acces="11111111111111",
                telephone="5141111111",
                age=25,
            ),
        ],
    )
    assert settings.headless is True
    assert settings.timeout == 120
    assert len(settings.participants) == 1
    assert settings.participants[0].name == "Participant 1"


def test_settings_from_toml_valid(tmp_path):
    config = tmp_path / "config.toml"
    config.write_text("""
headless = true
timeout = 300
refresh_interval = 2.5
domain = "Test Domain"
activity_name = "Parent-bébé"

[[participants]]
name = "Alice"
carte_acces = "12345678901234"
telephone = "5145551234"
age = 30

[[participants]]
name = "Bob"
carte_acces = "98765432109876"
telephone = "4505559876"
age = 8
""")
    settings = Settings.from_toml(config)
    assert settings.headless is True
    assert settings.timeout == 300
    assert settings.refresh_interval == 2.5
    assert settings.domain == "Test Domain"
    assert settings.activity_name == "Parent-bébé"
    assert len(settings.participants) == 2
    assert settings.participants[0].name == "Alice"
    assert settings.participants[1].carte_acces == "98765432109876"


def test_settings_from_toml_minimal(tmp_path):
    config = tmp_path / "config.toml"
    config.write_text('activity_name = "Test"\n')
    settings = Settings.from_toml(config)
    assert settings.activity_name == "Test"
    assert settings.headless is False
    assert settings.participants == []


def test_settings_from_toml_missing_activity_name(tmp_path):
    config = tmp_path / "config.toml"
    config.write_text("headless = true\n")
    with pytest.raises(ValidationError, match="must not be empty"):
        Settings.from_toml(config)


def test_settings_from_toml_missing_file(tmp_path):
    missing = tmp_path / "nonexistent.toml"
    with pytest.raises(FileNotFoundError):
        Settings.from_toml(missing)


def test_settings_from_toml_invalid_participant(tmp_path):
    config = tmp_path / "config.toml"
    config.write_text("""
activity_name = "Test"

[[participants]]
name = "Bad"
carte_acces = "123"
telephone = "5145551234"
age = 30
""")
    with pytest.raises(ValidationError, match="14 digits"):
        Settings.from_toml(config)


def test_settings_from_toml_invalid_timeout(tmp_path):
    config = tmp_path / "config.toml"
    config.write_text('activity_name = "Test"\ntimeout = -5\n')
    with pytest.raises(ValidationError, match="greater than 0"):
        Settings.from_toml(config)
