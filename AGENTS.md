# AGENTS.md - Coding Agent Guidelines

## Workflow Orchestration

### 1. Plan Mode Default
- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- If something goes sideways, STOP and re-plan immediately - don't keep pushing
- Use plan mode for verification steps, not just building
- Write detailed specs upfront to reduce ambiguity

### 2. Self-Improvement Loop
- After ANY correction from the user: update `tasks/lessons.md` with the pattern
- Write rules for yourself that prevent the same mistake
- Ruthlessly iterate on these lessons until mistake rate drops
- Review lessons at session start for relevant project

### 3. Verification Before Done
- Never mark a task complete without proving it works
- Diff behavior between main and your changes when relevant
- Ask yourself: "Would a staff engineer approve this?"
- Run tests, check logs, demonstrate correctness

### 4. Demand Elegance (Balanced)
- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
- Skip this for simple, obvious fixes - don't over-engineer
- Challenge your own work before presenting it

### 5. Autonomous Bug Fixing
- When given a bug report: just fix it. Don't ask for hand-holding
- Point at logs, errors, failing tests then resolve them
- Zero context switching required from the user
- Go fix failing CI tests without being told how

## Task Management

1. **Plan First**: Write plan to `tasks/todo.md` with checkable items
2. **Verify Plan**: Check in before starting implementation
3. **Track Progress**: Mark items complete as you go
4. **Explain Changes**: High-level summary at each step
5. **Document Results**: Add review section to plan `tasks/todo.md`
6. **Capture Lessons**: Update `tasks/lessons.md` after corrections

## Core Principles

- **Simplicity First**: Make every change as simple as possible. Impact minimal code.
- **No Laziness**: Find root causes. No temporary fixes. Senior developer standards.
- **Minimal Impact**: Changes should only touch what's necessary. Avoid introducing bugs.

See README.md for project details.

## Build/Lint/Test Commands

### Setup
```bash
# Install dependencies using uv
uv sync

# Install dev dependencies
uv sync --all-extras

# Install Playwright browsers
uv run playwright install chromium

# Configure git hooks
git config core.hooksPath .githooks
```

### Running the Application
```bash
# Run registration
uv run aweille register

# Verify credentials
uv run aweille verify --carte 01234567890123 --tel 5145551234

# Run with options
uv run aweille register --headless --timeout 300

# Run with custom config
uv run aweille register --config my-config.toml
```

### Linting and Formatting
```bash
# Format code with ruff
uv run ruff format .

# Lint with ruff
uv run ruff check .

# Lint and auto-fix
uv run ruff check . --fix

# Type checking
uv run mypy src
```

### Testing
```bash
# Run all tests
uv run pytest

# Run a single test file
uv run pytest tests/test_config.py

# Run with verbose output
uv run pytest -v

# Run with coverage
uv run pytest --cov=.
```

<!-- GSD:project-start source:PROJECT.md -->
## Project

**longueuil-aweille**

A Python CLI tool that automates activity registration on the City of Longueuil recreation website using Playwright browser automation. Built for Quebec parents who need to compete for limited municipal activity spots that vanish in seconds. Published on GitHub as a portfolio piece for potential employers and recruiters.

**Core Value:** A polished, well-tested, well-documented CLI tool that demonstrates real-world Python engineering — async patterns, browser automation, clean architecture, and thorough testing — that a recruiter can clone, understand, and run in minutes.

### Constraints

- **Python**: 3.11+ required (stdlib tomllib dependency)
- **Target site**: ASP.NET WebForms site with auto-generated IDs — selectors are inherently fragile
- **No external services**: Must remain a standalone CLI tool, no databases or servers
- **Existing patterns**: Maintain Pydantic settings, Typer CLI, Rich output — don't rewrite the stack
- **Tests must pass**: CI must be green — this is the #1 signal for recruiters
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

## Languages
- Python 3.12 — All source code, tests, configuration loading
- Minimum version constraint: `>=3.11` (declared in `pyproject.toml` line 7)
- TOML — Configuration files (`config.toml`)
- YAML — CI/CD (`.github/workflows/ci.yml`), pre-commit hooks (`.pre-commit-config.yaml`)
- Markdown — Documentation (`README.md`, `AGENTS.md`)
## Runtime
- CPython 3.12 (pinned in `.python-version`)
- Compatible with Python 3.11+ (classifiers in `pyproject.toml` lines 21-23)
- uv — Primary package manager (lockfile: `uv.lock` present)
- Configured via `uv sync` / `uv sync --all-extras`
## Frameworks
- Playwright >=1.40.0 — Browser automation engine (Chromium-based web scraping and form filling)
- Pydantic >=2.0.0 — Data validation and settings models (`Settings`, `Participant`)
- pydantic-settings >=2.0.0 — Settings management with env var prefix (`LONGUEUIL_`)
- Typer >=0.9.0 — CLI framework (declares commands: `register`, `verify`, `browse`)
- Rich >=13.0.0 — Terminal output formatting (panels, tables, colored text)
- pytest >=8.0.0 — Test runner
- pytest-asyncio >=0.23.0 — Async test support (mode: `auto` in `pyproject.toml` line 96)
- pytest-cov >=4.0.0 — Coverage reporting
- hatchling — Build backend (`pyproject.toml` line 52)
- ruff >=0.2.0 — Linter and formatter (replaces flake8, isort, black)
- mypy >=1.8.0 — Static type checking (strict mode)
## Key Dependencies
- `playwright` >=1.40.0 — Drives the entire registration flow via browser automation. Chromium must be installed separately (`uv run playwright install chromium`)
- `pydantic` >=2.0.0 — All data models (`Settings`, `Participant`, `ActivityInfo`, `Selectors`) use Pydantic for validation
- `pydantic-settings` >=2.0.0 — `Settings` extends `BaseSettings` with `LONGUEUIL_` env prefix and TOML loading
- `typer` >=0.9.0 — CLI entry point at `aweille` command (`pyproject.toml` line 43)
- `rich` >=13.0.0 — All user-facing output via `Console`, `Panel`, `Table`
- `tomllib` — TOML parsing for config files (Python 3.11+ stdlib)
- `asyncio` — All Playwright operations are async; `asyncio.run()` bridges from sync CLI to async bots
- `dataclasses` — Used for `Selectors`, `ActivityInfo`, `Activity`, `RegistrationDates`, `VerifySelectors`
- `logging` — Structured logging throughout (`logger = logging.getLogger(__name__)`)
- `enum.Enum` — Status types: `RegistrationStatus`, `VerificationStatus`, `ActivityStatus`
## Configuration
- Config loaded from TOML files via `Settings.from_toml()` (`src/longueuil_aweille/config.py` line 35)
- Env var override supported via `LONGUEUIL_` prefix (e.g., `LONGUEUIL_HEADLESS=true`)
- CLI flags override both config file and env vars (`--headless`, `--timeout`)
- `config.toml` is gitignored (contains participant credentials)
- `pyproject.toml` — Single source of truth for all project config
- `[tool.ruff]` — Linting rules (lines 57-83)
- `[tool.mypy]` — Type checking config (lines 85-93)
- `[tool.pytest.ini_options]` — Test config (lines 95-98)
- `[tool.coverage]` — Coverage source and exclusions (lines 100-109)
- `.pre-commit-config.yaml` — Runs trailing-whitespace, end-of-file-fixer, ruff lint+format, mypy, pytest
- Installed via `git config core.hooksPath .githooks`
## Platform Requirements
- Python 3.11+ (3.12 recommended)
- uv package manager
- Chromium browser (installed via `playwright install chromium`)
- No database required
- No Docker required
- This is a CLI tool, not a deployed service
- Runs locally on user machines
- Requires a display or headless mode (`--headless` flag)
- Target: Linux, macOS, Windows (Playwright cross-platform)
## Tooling Summary
| Tool | Version | Purpose |
|------|---------|---------|
| uv | latest | Package manager, virtualenv, script runner |
| hatchling | latest | Build backend (PEP 517) |
| ruff | >=0.2.0 | Linter + formatter (replaces flake8, isort, black) |
| mypy | >=1.8.0 | Static type checker (strict mode) |
| pytest | >=8.0.0 | Test runner |
| pytest-asyncio | >=0.23.0 | Async test support |
| pytest-cov | >=4.0.0 | Coverage reporting |
| pre-commit | v6.0.0 hooks | Git hook automation |
| Renovate | configured | Automated dependency updates (`.github/workflows/renovate.json`) |
## CI Pipeline
- `ubuntu-latest` runner
- Python 3.12
- `uv sync --all-extras` for dependency installation
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

## Naming Patterns
- Snake_case: `registration.py`, `config.py`, `browse.py`, `status.py`, `verify.py`
- Dunder entry: `__main__.py`, `__init__.py`
- Test files: `test_` prefix — `test_config.py`, `test_bot.py`, `test_cli.py`
- PascalCase for all classes and dataclasses
- Suffix conventions:
- `snake_case` for all functions and methods
- Private methods use single `_` prefix: `_navigate_to_search`, `_fill_credentials`, `_submit`
- Async methods follow same convention: `async def _verify(self, page: Page)`
- `UPPER_SNAKE_CASE`: `DEFAULT_SELECTORS`, `DEFAULT_VERIFY_SELECTORS`, `DEFAULT_BROWSE_SELECTORS`, `DEFAULT_REGISTRATION_URL`
- Type aliases use PascalCase: `PageCallback`
- `snake_case` everywhere: `page_content`, `status_str`, `reg_opens`, `day_lower`
- Loop variables: single-letter `i`, or descriptive `participant`, `activity`
## Code Style
- Tool: Ruff formatter (configured in `pyproject.toml` line 57)
- Line length: 100 characters
- Target: Python 3.11+
- Double quotes for strings (Ruff default)
- Tool: Ruff linter with comprehensive rule set
- Config location: `pyproject.toml` lines 61–80
- Enabled rule categories:
- Ignored rules:
- Config: `.pre-commit-config.yaml`
- Runs: trailing-whitespace fix, end-of-file-fixer, check-yaml, check-toml, check-added-large-files
- Ruff lint + format with auto-fix
- mypy type checking
- pytest test suite
- Tool: mypy with `strict = true`
- Config: `pyproject.toml` lines 85–93
- `warn_return_any = true`, `warn_unused_ignores = true`
- Playwright modules have `ignore_missing_imports = true`
## Type Hints
## Import Organization
- Relative imports (`from .module import ...`) for intra-package references
- Multi-line imports grouped with parentheses
- `from` style preferred over bare `import` for specific names
- `import tomllib` used inline inside `from_toml()` method (lazy import, line 36 of `config.py`)
## Error/Exception Handling
- `BrowseError(Exception)` — base for browse errors (`browse.py` line 16)
- `DomainNotFoundError(BrowseError)` — with custom attributes `domain` and `available_domains` (`browse.py` line 20)
- `typer.Exit(1)` for expected failures (invalid credentials, timeout, etc.)
- `raise typer.Exit(1) from None` to suppress traceback (e.g., `__main__.py` line 288)
- Match/case on status enums for user-facing messages (`__main__.py` lines 130–181)
## Logging
- `logger.info()` — flow tracking: "Starting registration bot...", "Activity found and selected!", "Clicking search button..."
- `logger.error()` — failures: "Invalid credentials", "Registration failed: {e}"
- `logger.warning()` — ambiguous states: "Could not determine verification status"
- `logger.debug()` — parse noise: "Error parsing row: {e}", "Error getting registration dates: {e}"
## Docstrings
## Pydantic Model Patterns
- Use `Field(...)` with `description` for every field — never bare type annotation
- Required fields use `Field(...)` (ellipsis = no default)
- Optional fields provide `default=` or `default_factory=`
- Environment variable prefix `LONGUEUIL_` for env override
- Custom TOML loader via `@classmethod def from_toml(cls, path: Path)` using `tomllib`
## Dataclass Patterns
- `ActivityInfo`, `Selectors` — `registration.py`
- `RegistrationDates`, `Activity`, `BrowseSelectors` — `browse.py`
- `VerifySelectors` — `verify.py`
## Enum Patterns
## Async/Await Patterns
- `await page.goto(url, wait_until="networkidle")` — navigation
- `await page.wait_for_timeout(ms)` — explicit small waits (300–3000ms)
- `await page.wait_for_load_state("networkidle")` — wait for network idle
- `await page.locator(selector).fill(value)` — form filling
- `await element.count()` before `await element.click()` — guard against missing elements
- `await page.locator("body").inner_text()` — read page content for status checking
## Configuration Conventions
## Module Design
- `cli.py` is a thin re-export: `from .__main__ import app` — the actual CLI entry point
- `__init__.py` exports `__version__` only
- No barrel `__all__` exports in source modules (only `cli.py` has `__all__`)
- `RegistrationBot` — registration flow (`registration.py`)
- `VerificationBot` — credential verification (`verify.py`)
- `ActivityScraper` — activity browsing (`browse.py`)
- Shared utilities in `status.py`
- `ActivityStatus`, `RegistrationStatus` — enums
- `get_status_from_image_src()` — helper
- `iterate_pagination()` — generic pagination helper with TypeVar
## CLI Patterns
- Use `typer.Option()` with `--long` and `-s`hort flags
- Boolean options: `--verify/--no-verify`, `--headless/--no-headless`
- Path options use `exists=True` for validation (`--config`)
- Required options use `...` as default (`--carte`, `--tel`)
## Match/Case Usage
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

## Pattern Overview
- Three independent bot classes (`RegistrationBot`, `VerificationBot`, `ActivityScraper`) each owning a full Playwright browser lifecycle
- Configuration loaded from TOML files via Pydantic settings, with CLI option overrides
- Status/result communicated via strongly-typed enums (no exceptions for flow control)
- All browser interactions are async; CLI commands bridge sync→async via `asyncio.run()`
- Selectors externalized into dataclasses for testability and adaptability
## Layers
- Purpose: Parse CLI arguments, display Rich-formatted output, orchestrate bots
- Location: `src/longueuil_aweille/__main__.py`
- Contains: Typer app definition, command handlers, Rich console output
- Depends on: All bot modules, config, status enums
- Used by: End user via `aweille` entry point or `python -m longueuil_aweille`
- Purpose: Load and validate settings from TOML files and environment variables
- Location: `src/longueuil_aweille/config.py`
- Contains: Pydantic `Settings` and `Participant` models
- Depends on: `pydantic`, `pydantic-settings`, `tomllib` (stdlib)
- Used by: CLI layer, `RegistrationBot`
- Purpose: Drive browser automation for registration, verification, and browsing
- Location: `src/longueuil_aweille/registration.py`, `src/longueuil_aweille/verify.py`, `src/longueuil_aweille/browse.py`
- Contains: Bot classes with async `run()` methods, page interaction logic, result parsing
- Depends on: `playwright`, `config.py`, `status.py`
- Used by: CLI layer
- Purpose: Define status enums, provide shared pagination and image-parsing utilities
- Location: `src/longueuil_aweille/status.py`
- Contains: `ActivityStatus`, `RegistrationStatus` enums, `get_status_from_image_src()`, `iterate_pagination()`
- Depends on: `playwright` (for `Page` type only)
- Used by: All bot modules
## Data Flow
- No persistent state — each bot run is self-contained
- `RegistrationBot.last_activity_status`: tracks most recent activity status across pagination attempts
- `ActivityScraper.activities`: accumulates `Activity` dataclass instances during scraping
- `Settings` is immutable after construction (Pydantic model); CLI mutates it only for option overrides before passing to bots
## Key Abstractions
- Purpose: Encapsulate a complete browser automation workflow
- Examples: `src/longueuil_aweille/registration.py` (RegistrationBot), `src/longueuil_aweille/verify.py` (VerificationBot), `src/longueuil_aweille/browse.py` (ActivityScraper)
- Pattern: Each bot owns its full Playwright lifecycle (`async with async_playwright() → launch → new_context → new_page → try/finally close`). Callers invoke `await bot.run()` and receive a result enum.
- Purpose: Externalize CSS/XPath selectors from page interaction logic for testability
- Examples: `src/longueuil_aweille/registration.py` (Selectors, DEFAULT_SELECTORS), `src/longueuil_aweille/verify.py` (VerifySelectors, DEFAULT_VERIFY_SELECTORS), `src/longueuil_aweille/browse.py` (BrowseSelectors, DEFAULT_BROWSE_SELECTORS)
- Pattern: Each bot accepts an optional `selectors` parameter defaulting to a module-level `DEFAULT_*_SELECTORS` constant. Templates like `dossier_input_template` use `{i:02d}` format placeholders for parameterized participant rows.
- Purpose: Strongly-typed result codes for all bot outcomes
- Examples: `src/longueuil_aweille/status.py` (ActivityStatus, RegistrationStatus), `src/longueuil_aweille/verify.py` (VerificationStatus)
- Pattern: String-valued enums. `ActivityStatus` describes activity availability state. `RegistrationStatus` describes registration attempt outcomes. CLI uses `match/case` on these for output formatting.
## Entry Points
- Location: `src/longueuil_aweille/__main__.py`
- Triggers: `aweille` console script (defined in `pyproject.toml` as `longueuil_aweille.cli:app`) or `python -m longueuil_aweille`
- Responsibilities: Defines Typer app with three commands: `register`, `verify`, `browse`
- Location: `src/longueuil_aweille/__main__.py` line 350-351
- Triggers: `python -m longueuil_aweille`
- Responsibilities: Calls `app()` to invoke Typer
- Location: `src/longueuil_aweille/cli.py`
- Exports: `app` (Typer instance) for external consumption
- Also: Individual bot classes and Settings can be imported directly
## Error Handling
- Bots catch all exceptions at the top of `run()`, log the error, and return a failure enum (`RegistrationStatus.FAILED`, `VerificationStatus.ERROR`)
- `RegistrationBot.run()` takes a screenshot on exception and saves to `error-{timestamp}.png`
- `ActivityScraper.run()` preserves partial results in `self.activities` on failure
- `DomainNotFoundError` is re-raised from scraper (not swallowed) for CLI-level handling
- Uses `match/case` on status enums to display appropriate Rich panels
- Error statuses trigger `typer.Exit(1)` for non-zero exit codes
- Missing config file validated by Typer's `exists=True` option
- Bot methods like `_submit()` and `_check_result()` parse page body text for French-language indicator strings
- No structured API responses — all state detection is via text pattern matching in rendered HTML
## Async Patterns
- All bots are fully async using `async/await` with Playwright's async API
- CLI bridges sync Typer handlers to async bots via `asyncio.run(bot.run())`
- The only sync→async bridge outside of this is `_prompt_unregister()` which uses `loop.run_in_executor()` to call `input()` without blocking the event loop
```python
```
- `page.wait_for_timeout(ms)` — used extensively for short delays between interactions (300-3000ms)
- `page.wait_for_load_state("networkidle")` — waits for page to fully load after navigation/clicks
- `page.reload(wait_until="networkidle")` — refresh in polling loop
- `asyncio.sleep()` — used for configurable refresh intervals in the polling loop
## Cross-Cutting Concerns
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, or `.github/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
