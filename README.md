# longueuil-aweille

[![CI](https://github.com/halfguru/longueuil-aweille/actions/workflows/ci.yml/badge.svg)](https://github.com/halfguru/longueuil-aweille/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-62%25-green)](https://github.com/halfguru/longueuil-aweille)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-1.40%2B-2EAD33?logo=playwright&logoColor=white)](https://playwright.dev/python/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

Automate municipal activity registration for the City of Longueuil recreation website. Avoid manual page refreshing and never miss a spot again.

> **Aweille!** — "Hurry up!" in Quebec French. Because spots vanish in seconds.

![Demo](demo.gif)

## Features

- Auto-register for any municipal activity (swimming, art, sports, etc.)
- Credential verification before registration
- Multiple participant support
- Auto-retry when registration is not yet open
- Simple TOML configuration
- CLI with rich output
- Robust retry logic with exponential backoff for flaky networks

## Quick Start

```bash
# Install dependencies
uv sync
uv run playwright install chromium

# Copy the example config and fill in your details
cp config.example.toml config.toml

# Verify your credentials work
uv run aweille verify --carte 01234567890123 --tel 5145551234

# Browse available activities
uv run aweille browse

# Run registration
uv run aweille register
```

## Configuration

Copy [`config.example.toml`](config.example.toml) to `config.toml` and fill in your details. See the example file for all available options and documentation.

### Finding Your Domain and Activity

1. Visit the [Longueuil registration site](https://loisir.longueuil.quebec/inscription/)
2. Click "Domaines" to see available categories
3. Note the exact activity name you want
4. Use `uv run aweille browse` to search interactively

## Usage

```bash
# Run registration (verifies credentials by default)
uv run aweille register

# Skip credential verification
uv run aweille register --no-verify

# Run in headless mode
uv run aweille register --headless

# Custom timeout and config
uv run aweille register --timeout 300 --config my-config.toml

# Verify credentials separately
uv run aweille verify --carte 01234567890123 --tel 5145551234

# Browse available activities
uv run aweille browse

# Browse with filters
uv run aweille browse --domain "Activités aquatiques" --available --age 5

# Browse by day and location
uv run aweille browse --day samedi --location "Vieux-Longueuil"
```

## How It Works

1. Opens the Longueuil recreation website
2. Selects the configured domain (activity category)
3. Searches for the activity by name across all pages
4. Waits for registration to open (refreshes periodically)
5. Registers when the spot becomes available
6. Fills in participant credentials
7. Submits the registration

## Development

```bash
# Install dev dependencies
uv sync --all-extras

# Run linter
uv run ruff check .

# Run formatter
uv run ruff format .

# Run type checker
uv run mypy src

# Run tests with coverage
uv run pytest -v --cov

# Install git hooks (pre-commit)
uv run pre-commit install
```

## Architecture

```
src/longueuil_aweille/
├── __main__.py      # CLI entry point (Typer + Rich)
├── config.py        # Pydantic settings & validation
├── registration.py  # RegistrationBot — form filling & submission
├── verify.py        # VerificationBot — credential checking
├── browse.py        # ActivityScraper — activity discovery
├── navigation.py    # Shared navigation helpers & retry logic
├── selectors.py     # CSS/XPath selectors (dataclasses)
└── status.py        # Status enums & pagination utilities
```

## Disclaimer

This tool is for personal use to automate a tedious manual process. Use responsibly and in accordance with the website's terms of service.

## License

MIT
