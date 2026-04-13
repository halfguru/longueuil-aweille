import re
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Participant(BaseSettings):
    name: str = Field(..., description="Participant name for logging")
    age: int = Field(..., description="Participant age for validation")
    carte_acces: str = Field(..., description="Numéro de carte d'accès (14 digits)")
    telephone: str = Field(..., description="Numéro de téléphone (10 digits)")

    @field_validator("carte_acces")
    @classmethod
    def validate_carte_acces(cls, v: str) -> str:
        if not re.fullmatch(r"\d{14}", v):
            raise ValueError("carte_acces must be exactly 14 digits")
        return v

    @field_validator("telephone")
    @classmethod
    def validate_telephone(cls, v: str) -> str:
        if not re.fullmatch(r"\d{10}", v):
            raise ValueError("telephone must be exactly 10 digits")
        return v


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LONGUEUIL_")

    registration_url: str = Field(
        default="https://loisir.longueuil.quebec/inscription/Pages/Anonyme/Resultat/Page.fr.aspx?m=1",
        description="Registration website URL",
    )
    headless: bool = Field(default=False, description="Run browser in headless mode")
    timeout: int = Field(default=600, gt=0, description="Timeout in seconds")
    refresh_interval: float = Field(default=5.0, gt=0.0, description="Refresh interval in seconds")
    domain: str = Field(
        default="Activités aquatiques (Vieux-Longueuil)",
        description="Domain/category to select (e.g., 'Activités aquatiques (Vieux-Longueuil)')",
    )
    activity_name: str = Field(
        default="",
        description="Activity name to search for (e.g., 'Parent-bébé', 'Niveau 1')",
    )
    participants: list[Participant] = Field(default_factory=list)

    @field_validator("activity_name")
    @classmethod
    def validate_activity_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("activity_name must not be empty")
        return v

    @classmethod
    def from_toml(cls, path: Path) -> "Settings":
        import tomllib

        with path.open("rb") as f:
            data = tomllib.load(f)

        participants_data = data.pop("participants", [])
        participants = [Participant(**p) for p in participants_data]
        return cls(**data, participants=participants)
